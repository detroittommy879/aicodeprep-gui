"""LLM provider nodes for Flow Studio using LiteLLM."""

from __future__ import annotations
import logging
from typing import Any, Dict, Optional

from .base import BaseExecNode
from aicodeprep_gui.pro.llm.litellm_client import LLMClient, LLMError

# Guard Qt import for popups
try:
    from PySide6 import QtWidgets
except ImportError:
    QtWidgets = None


class LLMBaseNode(BaseExecNode):
    """
    Base LLM node: expects an input 'text' and optional 'system', produces output 'text'.
    Child classes define defaults for provider/base_url and handle model listing if needed.
    """

    def __init__(self):
        super().__init__()
        try:
            # IO
            self.add_input("text")
            self.add_input("system")  # optional
            self.add_output("text")

            # UI properties with proper widget types for better editing
            self.create_property("provider", "generic", widget_type="list",
                                 items=["openrouter", "openai", "gemini", "compatible", "generic"])
            self.create_property("model_mode", "choose", widget_type="list",
                                 items=["choose", "random", "random_free"])
            self.create_property("model", "", widget_type="text")
            self.create_property("api_key", "", widget_type="text")
            self.create_property("base_url", "", widget_type="text")
        except Exception:
            pass

    # Utility to show user-friendly error
    def _warn(self, msg: str):
        if QtWidgets is not None:
            try:
                QtWidgets.QMessageBox.warning(
                    None, getattr(self, 'NODE_NAME', 'LLM Node'), msg)
            except Exception:
                logging.warning(
                    f"[{getattr(self, 'NODE_NAME', 'LLM Node')}] {msg}")
        else:
            logging.warning(
                f"[{getattr(self, 'NODE_NAME', 'LLM Node')}] {msg}")

    # Child classes can override to set sensible defaults
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

        # Config file fallback by provider name
        try:
            from aicodeprep_gui.config import get_api_key
            provider = self.get_property("provider") or self.default_provider()
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

            # Config file fallback
            from aicodeprep_gui.config import get_provider_config
            provider = self.get_property("provider") or self.default_provider()
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
        except Exception:
            mode, model = "choose", ""

        if mode == "choose":
            return model or None
        return None  # let child classes handle random modes

    def run(self, inputs: Dict[str, Any], settings: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute the LLM call using LiteLLM.
        """
        text = inputs.get("text") or ""
        system = inputs.get("system") or None
        if not text:
            self._warn("No input 'text' provided.")
            return {}

        provider = (self.get_property("provider")
                    or self.default_provider()).strip().lower()
        api_key = self.resolve_api_key()
        if not api_key:
            from aicodeprep_gui.config import get_config_dir
            config_dir = get_config_dir()
            self._warn(
                f"Missing API key for provider '{provider}'.\n\nPlease edit: {config_dir / 'api-keys.toml'}\n\nAdd your API key under [{provider}] section.")
            return {}

        base_url = self.resolve_base_url()
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
                from aicodeprep_gui.pro.llm.litellm_client import LLMClient
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
                    # LiteLLM requires 'openrouter/' prefix
                    model = f"openrouter/{pick}"
                    logging.info(f"[{self.NODE_NAME}] Selected model: {model}")
                except Exception as e:
                    self._warn(f"Failed to get OpenRouter models: {e}")
                    return {}
            elif not model:
                # If no model specified and not in random mode, default to a known free model
                model = "openrouter/openai/gpt-3.5-turbo:free"
                logging.info(
                    f"[{self.NODE_NAME}] Using default model: {model}")
            else:
                # User provided a model in choose mode - add prefix if not present
                if not model.startswith("openrouter/"):
                    model = f"openrouter/{model}"
                    logging.info(
                        f"[{self.NODE_NAME}] Added openrouter prefix: {model}")

        if provider == "compatible" and not base_url:
            self._warn("OpenAI-compatible provider requires a base_url.")
            return {}

        if not model:
            self._warn(
                f"No model specified for provider '{provider}'. Please set a model or use random mode.")
            return {}

        try:
            logging.info(
                f"[{self.NODE_NAME}] Making LLM call with model: {model}")
            out = LLMClient.chat(
                model=model,
                user_content=text,
                api_key=api_key,
                base_url=base_url if base_url else None,
                extra_headers=self._extra_headers_for_provider(provider),
                system_content=system
            )
            logging.info(
                f"[{self.NODE_NAME}] LLM call successful, response length: {len(out) if out else 0}")
            return {"text": out}
        except LLMError as e:
            self._warn(f"LLM Error: {str(e)}")
            logging.error(f"[{self.NODE_NAME}] LLM Error: {str(e)}")
            return {}
        except Exception as e:
            self._warn(f"Unexpected error: {str(e)}")
            logging.error(f"[{self.NODE_NAME}] Unexpected error: {str(e)}")
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
            # LiteLLM handles model like "gemini/gemini-1.5-pro"
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
