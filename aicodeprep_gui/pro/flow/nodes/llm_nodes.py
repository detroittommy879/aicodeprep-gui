"""LLM provider nodes for Flow Studio using the internal LLM client."""

from __future__ import annotations
import logging
from typing import Any, Dict, Optional

from .base import BaseExecNode
from aicodeprep_gui.pro.llm.llm_client import LLMClient, LLMError
from aicodeprep_gui.pro.ai_assist.endpoint_config import get_active_endpoint
from aicodeprep_gui.pro.flow.model_picker import (
    choose_random_model_ids,
    list_compatible_model_ids,
)

# Guard Qt import for popups
try:
    from PySide6 import QtWidgets
except ImportError:
    QtWidgets = None

try:
    from NodeGraphQt.constants import NodePropWidgetEnum
except ImportError:
    class NodePropWidgetEnum:
        QLINE_EDIT = 3
        QCOMBO_BOX = 5

_cached_model_options = [
    "gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet-20241022",
    "gemini-1.5-pro", "gemini-1.5-flash", "o1-mini", "o3-mini",
    "random", "random_free"
]
_fetching_models = False

def trigger_bg_model_fetch():
    global _fetching_models
    if not _fetching_models:
        _fetching_models = True
        import threading
        def _fetch():
            try:
                from aicodeprep_gui.pro.ai_assist.endpoint_config import get_active_endpoint
                endpoint = get_active_endpoint() or {}
                if endpoint.get("selected_model") and endpoint["selected_model"] not in _cached_model_options:
                    _cached_model_options.insert(0, endpoint["selected_model"])
                url, api_key = endpoint.get("url", ""), endpoint.get("api_key", "")
                if url:
                    from aicodeprep_gui.pro.flow.model_picker import list_compatible_model_ids
                    models = list_compatible_model_ids(url, api_key)
                    for m in reversed(models):
                        if m not in _cached_model_options:
                            _cached_model_options.insert(0, m)
            except Exception as e:
                logging.debug(f"Failed to bg fetch models: {e}")
        threading.Thread(target=_fetch, daemon=True).start()

trigger_bg_model_fetch()

def _patch_prop_combobox():
    try:
        from NodeGraphQt.custom_widgets.properties_bin.prop_widgets_base import PropComboBox
        if hasattr(PropComboBox, "_patched_for_editable"): return
        orig_init = PropComboBox.__init__
        def patched_init(self, parent=None):
            orig_init(self, parent)
            self.setEditable(True)
            self.currentTextChanged.connect(lambda t: self.value_changed.emit(self.get_name(), self.currentText()) if hasattr(self, 'value_changed') else None)
        def patched_set_value(self, value):
            val_str = str(value) if value is not None else ""
            if val_str != self.currentText():
                from PySide6 import QtCore
                idx = self.findText(val_str, QtCore.Qt.MatchExactly)
                self.blockSignals(True)
                if idx >= 0:
                    self.setCurrentIndex(idx)
                else:
                    self.setCurrentText(val_str)
                self.blockSignals(False)
        PropComboBox.__init__ = patched_init
        PropComboBox.set_value = patched_set_value
        PropComboBox._patched_for_editable = True
    except Exception:
        pass
_patch_prop_combobox()

def _get_compat_provider_label() -> str:
    try:
        from aicodeprep_gui.pro.ai_assist.endpoint_config import get_active_endpoint
        ep_name = (get_active_endpoint() or {}).get("name", "").strip()
        return f"compatible ({ep_name})" if ep_name else "compatible"
    except Exception:
        return "compatible"


class LLMBaseNode(BaseExecNode):
    """
    Base LLM node: expects an input 'text' and optional 'system', produces output 'text'.
    Child classes define defaults for provider/base_url and handle model listing if needed.
    """

    def __init__(self):
        super().__init__()
        # IO
        self.add_input("text")
        self.add_input("system")  # optional
        self.add_output("text")

        # UI properties with proper widget types for better editing
        self.create_property("provider", "generic", widget_type=NodePropWidgetEnum.QCOMBO_BOX.value,
                             items=["openai", "openrouter", "gemini", _get_compat_provider_label(), "generic"])
        self.create_property("model_mode", "choose", widget_type=NodePropWidgetEnum.QCOMBO_BOX.value,
                             items=["choose", "random", "random_free"])
        self.create_property(
            "model", "", widget_type=NodePropWidgetEnum.QCOMBO_BOX.value, items=list(_cached_model_options))
        self.create_property(
            "api_key", "", widget_type=NodePropWidgetEnum.QLINE_EDIT.value)
        self.create_property(
            "base_url", "", widget_type=NodePropWidgetEnum.QLINE_EDIT.value)
        # Optional: write output to file for debugging (e.g., "llm1.md")
        self.create_property(
            "output_file", "", widget_type=NodePropWidgetEnum.QLINE_EDIT.value)
        # Sampling parameters for creativity/randomness control
        self.create_property(
            "temperature", 0.7, widget_type=NodePropWidgetEnum.QLINE_EDIT.value)
        self.create_property(
            "top_p", 1.0, widget_type=NodePropWidgetEnum.QLINE_EDIT.value)

        # Add read-only text widget to display model info
        try:
            self.add_text_input('_info_display', '',
                                multi_line=False, tab=None)
            # Make it read-only
            try:
                widget = self.get_widget('_info_display')
                if widget and hasattr(widget, 'get_custom_widget'):
                    qt_widget = widget.get_custom_widget()
                    if qt_widget and hasattr(qt_widget, 'setReadOnly'):
                        qt_widget.setReadOnly(True)
                        qt_widget.setStyleSheet(
                            "background: transparent; border: none;")
            except Exception:
                pass
        except Exception:
            pass

        # Schedule label display update after node is fully initialized
        try:
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, self._update_node_label)
        except Exception:
            pass

    def _update_node_label(self):
        """Update the node's display name with current model and settings (single line)."""
        try:
            from NodeGraphQt import BaseNode as NGBaseNode
            base_name = getattr(self, 'NODE_NAME', 'LLM Node')
            model = ""
            model_mode = "choose"
            temperature = 0.7
            top_p = 1.0

            # Get properties using BaseNode's get_property to avoid any overrides
            try:
                model = (NGBaseNode.get_property(self, "model") or "").strip()
                model_mode = (NGBaseNode.get_property(
                    self, "model_mode") or "choose").strip()
                temperature = NGBaseNode.get_property(
                    self, "temperature") or 0.7
                top_p = NGBaseNode.get_property(self, "top_p") or 1.0
            except Exception as e:
                logging.debug(f"Error getting properties for label: {e}")

            # Build compact single-line display
            # Strategy: If model is set, use just the model name. Otherwise use base name.
            if model:
                # Show just the model name (last part after /)
                model_short = model.split('/')[-1] if '/' in model else model
                # Truncate to fit node width better
                if len(model_short) > 20:
                    model_short = model_short[:17] + "..."
                display = model_short
            elif model_mode in ("random", "random_free"):
                # For random mode, show the mode
                display = f"{base_name} [{model_mode}]"
            else:
                # Default: just the base name
                display = base_name

            # Add sampling params if non-default (compact) as suffix
            params = []
            if temperature is not None and temperature != 0.7:
                params.append(f"T{temperature}")
            if top_p is not None and top_p != 1.0:
                params.append(f"P{top_p}")
            if params:
                display = f"{display} ({','.join(params)})"

            # Update node name
            if hasattr(self, 'set_name'):
                self.set_name(display)

            # Also update the info display widget if it exists
            try:
                # Build info text for widget (can be longer)
                info_parts = []
                if model:
                    info_parts.append(f"Model: {model}")
                elif model_mode in ("random", "random_free"):
                    info_parts.append(f"Mode: {model_mode}")
                if temperature != 0.7:
                    info_parts.append(f"Temp: {temperature}")
                if top_p != 1.0:
                    info_parts.append(f"TopP: {top_p}")

                if info_parts and hasattr(self, 'set_property'):
                    info_text = " | ".join(info_parts)
                    # Use the base class's set_property to avoid recursion
                    from NodeGraphQt import BaseNode as NGBaseNode
                    NGBaseNode.set_property(
                        self, '_info_display', info_text, push_undo=False)
            except Exception as e:
                logging.debug(f"Failed to update info widget: {e}")
        except Exception as e:
            logging.debug(f"Failed to update node label: {e}")

    # Utility to show user-friendly error
    def _warn(self, msg: str):
        # Always log the warning
        logging.warning(f"[{getattr(self, 'NODE_NAME', 'LLM Node')}] {msg}")

        # Don't show message boxes from worker threads - they can cause crashes
        # The engine will handle showing errors to the user in the main thread

    def set_property(self, name: str, value, push_undo: bool = True):
        """Override to update node display when key properties change."""
        result = super().set_property(name, value, push_undo)
        # Update display when model-related properties change
        if name in ("model", "model_mode", "temperature", "top_p"):
            self._update_node_label()
        return result

    def on_input_connected(self, in_port, out_port):
        """Override to update display when connections change."""
        super().on_input_connected(in_port, out_port)
        self._update_node_label()

    def on_input_disconnected(self, in_port, out_port):
        """Override to update display when connections change."""
        super().on_input_disconnected(in_port, out_port)
        self._update_node_label()

    # Child classes can override to set sensible defaults
    def get_resolved_provider(self) -> str:
        try:
            from NodeGraphQt import BaseNode as NGBaseNode
            val = (NGBaseNode.get_property(self, "provider") or self.default_provider()).strip().lower()
            if val.startswith("compatible"):
                return "compatible"
            return val
        except Exception:
            return self.default_provider()

    def default_provider(self) -> str:

        return "generic"

    def default_base_url(self) -> str:
        return ""

    def resolve_api_key(self) -> str:
        """
        Resolve API key from node prop or config file fallback.
        """
        try:
            # Node property preference
            ak = self.get_property("api_key") or ""
        except Exception:
            ak = ""

        if ak:
            return ak

        try:
            provider = self.get_resolved_provider()
        except Exception:
            provider = self.default_provider()

        if provider == "compatible":
            endpoint = get_active_endpoint() or {}
            endpoint_key = (endpoint.get("api_key") or "").strip()
            if endpoint_key:
                return endpoint_key

        # Config file fallback by provider name
        try:
            from aicodeprep_gui.config import get_api_key
            ak = get_api_key(provider)
            if ak:
                return ak
        except Exception:
            pass
        return ""

    def resolve_base_url(self) -> str:
        try:
            # Node property first
            bu = self.get_property("base_url") or ""
            if bu:
                return bu

            provider = self.get_resolved_provider()
            if provider == "compatible":
                endpoint = get_active_endpoint() or {}
                endpoint_url = (endpoint.get("url") or "").strip()
                if endpoint_url:
                    return endpoint_url

            # Config file fallback
            from aicodeprep_gui.config import get_provider_config
            config = get_provider_config(provider)
            bu = config.get("base_url", "")
            if bu:
                return bu

            # Default fallback
            return self.default_base_url()
        except Exception:
            return self.default_base_url()

    def resolve_model(self, api_key: str) -> Optional[str]:
        """
        Resolve which model to call based on 'model' + 'model_mode'.
        Subclasses may override to implement 'random' / 'random_free'.
        """
        try:
            mode = (self.get_property("model_mode")
                    or "choose").strip().lower()
            model = (self.get_property("model") or "").strip()
            provider = self.get_resolved_provider()
        except Exception:
            mode, model, provider = "choose", "", self.default_provider()

        random_requested = model.lower() == "random"

        if provider == "compatible" and (mode in ("random", "random_free") or random_requested):
            base_url = self.resolve_base_url()
            model_ids = list_compatible_model_ids(base_url, api_key)
            picks = choose_random_model_ids(model_ids, 1)
            return picks[0] if picks else None

        if mode == "choose":
            if model and not random_requested:
                return model
            if provider == "compatible":
                endpoint = get_active_endpoint() or {}
                selected_model = (endpoint.get("selected_model") or "").strip()
                if selected_model:
                    return selected_model
                base_url = (endpoint.get("url") or "").strip(
                ) or self.resolve_base_url()
                if base_url:
                    model_ids = list_compatible_model_ids(base_url, api_key)
                    if model_ids:
                        return model_ids[0]
            return model or None
        return None  # let child classes handle random modes

    def run(self, inputs: Dict[str, Any], settings: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute the LLM call using the internal HTTP client.
        """
        try:
            text = inputs.get("text") or ""
            system = inputs.get("system") or None
            if not text:
                self._warn("No input 'text' provided.")
                return {}

            provider = self.get_resolved_provider()
            base_url = self.resolve_base_url()
            api_key = self.resolve_api_key()

            if provider == "compatible" and not base_url:
                from aicodeprep_gui.pro.ai_assist.endpoint_config import get_endpoints_file
                self._warn(
                    "OpenAI-compatible provider requires a base_url.\n\n"
                    f"Please edit: {get_endpoints_file()}"
                )
                return {}

            if not api_key and provider != "compatible":
                from aicodeprep_gui.config import get_config_dir
                config_dir = get_config_dir()
                self._warn(
                    f"Missing API key for provider '{provider}'.\n\nPlease edit: {config_dir / 'api-keys.toml'}\n\nAdd your API key under [{provider}] section.")
                return {}

            model = self.resolve_model(api_key)

            # Debug logging
            logging.info(
                f"[{self.NODE_NAME}] Provider: {provider}, Model: {model}, Base URL: {base_url}")

            if provider == "openrouter":
                # Random or random_free modes handled here
                try:
                    mode = (self.get_property("model_mode")
                            or "choose").strip().lower()
                except Exception:
                    mode = "choose"

                logging.info(f"[{self.NODE_NAME}] OpenRouter mode: {mode}")

                if mode in ("random", "random_free"):
                    # LLMClient is already imported at the top of the file
                    try:
                        models = LLMClient.list_models_openrouter(api_key)
                        logging.info(
                            f"[{self.NODE_NAME}] Found {len(models)} OpenRouter models")
                        pick = LLMClient.openrouter_pick_model(
                            models, free_only=(mode == "random_free"))
                        if not pick:
                            self._warn(
                                "Could not pick a model from OpenRouter. Check API key or connectivity.")
                            return {}
                        # Flow nodes store OpenRouter models with a provider prefix.
                        model = f"openrouter/{pick}"
                        logging.info(
                            f"[{self.NODE_NAME}] Selected model: {model}")
                    except Exception as e:
                        self._warn(f"Failed to get OpenRouter models: {e}")
                        return {}
                elif not model:
                    # If no model specified and not in random mode, default to a known free model
                    model = "openrouter/openai/gpt-3.5-turbo:free"
                    logging.info(
                        f"[{self.NODE_NAME}] Using default model: {model}")
                else:
                    # User provided a model in choose mode - ensure proper prefix
                    if model.startswith("openrouter/openrouter/"):
                        # User accidentally added openrouter/ prefix, remove one
                        model = model.replace(
                            "openrouter/openrouter/", "openrouter/", 1)
                        logging.info(
                            f"[{self.NODE_NAME}] Removed duplicate openrouter prefix: {model}")
                    elif not model.startswith("openrouter/"):
                        model = f"openrouter/{model}"
                        logging.info(
                            f"[{self.NODE_NAME}] Added openrouter prefix: {model}")
                    else:
                        logging.info(
                            f"[{self.NODE_NAME}] Model already has correct prefix: {model}")

            if not model:
                self._warn(
                    f"No model specified for provider '{provider}'. Please set a model or use random mode.")
                return {}

            # Get sampling parameters
            temperature = None
            top_p = None
            try:
                temp_val = self.get_property("temperature")
                if temp_val is not None and temp_val != "":
                    temperature = float(temp_val)
            except (ValueError, TypeError):
                logging.warning(
                    f"[{self.NODE_NAME}] Invalid temperature value, using default")

            try:
                top_p_val = self.get_property("top_p")
                if top_p_val is not None and top_p_val != "":
                    top_p = float(top_p_val)
            except (ValueError, TypeError):
                logging.warning(
                    f"[{self.NODE_NAME}] Invalid top_p value, using default")

            try:
                logging.info(
                    f"[{self.NODE_NAME}] Making LLM call with model: {model}")
                logging.info(
                    f"[{self.NODE_NAME}] API details - provider: {provider}, base_url: {base_url}, "
                    f"input_length: {len(text)}, has_system: {bool(system)}, temperature: {temperature}, top_p: {top_p}")
                out = LLMClient.chat(
                    model=model,
                    user_content=text,
                    api_key=api_key,
                    base_url=base_url if base_url else None,
                    extra_headers=self._extra_headers_for_provider(provider),
                    system_content=system,
                    temperature=temperature,
                    top_p=top_p,
                    provider=provider,
                )
                logging.info(
                    f"[{self.NODE_NAME}] LLM call successful, response length: {len(out) if out else 0}")
                if not out:
                    logging.warning(
                        f"[{self.NODE_NAME}] LLM returned empty response!")

                # Write to file if output_file is specified
                try:
                    output_file = self.get_property("output_file") or ""
                    if output_file and out:
                        from pathlib import Path
                        # Expand ~ for home directory
                        out_path = Path(output_file).expanduser()
                        out_path.parent.mkdir(parents=True, exist_ok=True)
                        out_path.write_text(out, encoding="utf-8")
                        logging.info(
                            f"[{self.NODE_NAME}] Wrote output to {out_path}")
                except Exception as write_err:
                    logging.warning(
                        f"[{self.NODE_NAME}] Failed to write output file: {write_err}")

                return {"text": out}
            except LLMError as e:
                error_msg = f"LLM Error: {str(e)}"
                self._warn(error_msg)
                logging.error(f"[{self.NODE_NAME}] {error_msg}", exc_info=True)
                logging.error(
                    f"[{self.NODE_NAME}] ⚠️ Returning empty output due to error - downstream nodes will not receive data from this node")
                return {}
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                self._warn(error_msg)
                logging.error(f"[{self.NODE_NAME}] {error_msg}", exc_info=True)
                logging.error(
                    f"[{self.NODE_NAME}] ⚠️ Returning empty output due to error - downstream nodes will not receive data from this node")
                return {}
        except Exception as outer_e:
            # Catch any exception in the entire run method
            error_msg = f"Fatal error in LLM node execution: {str(outer_e)}"
            logging.error(f"[{self.NODE_NAME}] {error_msg}", exc_info=True)
            try:
                self._warn(error_msg)
            except Exception:
                pass  # Even warning failed
            return {}

    def _extra_headers_for_provider(self, provider: str) -> Dict[str, str]:
        """
        OpenRouter requires specific headers for proper functionality.
        """
        provider = provider.lower()
        if provider == "openrouter":
            try:
                from aicodeprep_gui.config import get_provider_config
                config = get_provider_config("openrouter")
                site_url = config.get(
                    "site_url", "https://github.com/detroittommy879/aicodeprep-gui")
                app_name = config.get("app_name", "aicodeprep-gui")

                return {
                    "Accept": "application/json",
                    "HTTP-Referer": site_url,
                    "X-Title": app_name
                }
            except Exception:
                return {
                    "Accept": "application/json",
                    "HTTP-Referer": "https://github.com/detroittommy879/aicodeprep-gui",
                    "X-Title": "aicodeprep-gui"
                }
        return {}


class OpenRouterNode(LLMBaseNode):
    """OpenRouter LLM provider node."""
    __identifier__ = "aicp.flow"
    NODE_NAME = "OpenRouter LLM"

    def __init__(self):
        super().__init__()
        try:
            self.set_property("provider", "openrouter")
            self.set_property("base_url", "https://openrouter.ai/api/v1")
            # Default to random_free mode for easy testing
            self.set_property("model_mode", "random_free")
            # Leave model empty for random modes
            self.set_property("model", "")
            # Provide hints for UI
            self.create_property(
                "ui_hint_models", "Choose a model id, or set model_mode to 'random' or 'random_free'")
        except Exception:
            pass

    def default_provider(self) -> str:
        return "openrouter"

    def default_base_url(self) -> str:
        return "https://openrouter.ai/api/v1"

    def resolve_model(self, api_key: str) -> Optional[str]:
        # Let parent handle `choose` mode; random/random_free handled in run()
        return super().resolve_model(api_key)


class OpenAINode(LLMBaseNode):
    """OpenAI LLM provider node."""
    __identifier__ = "aicp.flow"
    NODE_NAME = "OpenAI LLM"

    def __init__(self):
        super().__init__()
        try:
            self.set_property("provider", "openai")
            # OpenAI official does not need base_url
            self.set_property("base_url", "")
        except Exception:
            pass

    def default_provider(self) -> str:
        return "openai"


class GeminiNode(LLMBaseNode):
    """Gemini LLM provider node."""
    __identifier__ = "aicp.flow"
    NODE_NAME = "Gemini LLM"

    def __init__(self):
        super().__init__()
        try:
            self.set_property("provider", "gemini")
            # Gemini models can be entered with or without a provider prefix.
            self.set_property("base_url", "")  # not needed for Gemini
        except Exception:
            pass

    def default_provider(self) -> str:
        return "gemini"


class OpenAICompatibleNode(LLMBaseNode):
    """Generic OpenAI-Compatible LLM provider node."""
    __identifier__ = "aicp.flow"
    NODE_NAME = "OpenAI-Compatible LLM"

    def __init__(self):
        super().__init__()
        try:
            self.set_property("provider", "compatible")
            self.set_property("base_url", "")
        except Exception:
            pass

    def default_provider(self) -> str:
        return "compatible"
