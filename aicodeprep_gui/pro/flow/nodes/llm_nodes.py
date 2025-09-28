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

            # UI properties
            # Storing as string properties for session; we can also add embedded widgets if needed.
            self.create_property("api_key", "")
            self.create_property("base_url", "")
            self.create_property("model", "")
            self.create_property("model_mode", "choose")  # 'choose' | 'random' | 'random_free'
            self.create_property("provider", "generic")   # openrouter|openai|gemini|compatible|generic
        except Exception:
            pass

    # Utility to show user-friendly error
    def _warn(self, msg: str):
        if QtWidgets is not None:
            try:
                QtWidgets.QMessageBox.warning(None, getattr(self, 'NODE_NAME', 'LLM Node'), msg)
            except Exception:
                logging.warning(f"[{getattr(self, 'NODE_NAME', 'LLM Node')}] {msg}")
        else:
            logging.warning(f"[{getattr(self, 'NODE_NAME', 'LLM Node')}] {msg}")

    # Child classes can override to set sensible defaults
    def default_provider(self) -> str:
        return "generic"

    def default_base_url(self) -> str:
        return ""

    def resolve_api_key(self) -> str:
        """
        Resolve API key from node prop or QSettings fallback.
        """
        try:
            # Node property preference
            ak = self.get_property("api_key") or ""
        except Exception:
            ak = ""

        if ak:
            return ak

        # QSettings fallback by provider name
        try:
            from PySide6 import QtCore
            settings = QtCore.QSettings("aicodeprep-gui", "APIKeys")
            provider = self.get_property("provider") or self.default_provider()
            group = f"{provider}"
            settings.beginGroup(group)
            ak = settings.value("api_key", "", type=str)
            settings.endGroup()
            if ak:
                return ak
        except Exception:
            pass
        return ""

    def resolve_base_url(self) -> str:
        try:
            bu = self.get_property("base_url") or self.default_base_url()
        except Exception:
            bu = self.default_base_url()
        return bu

    def resolve_model(self, api_key: str) -> Optional[str]:
        """
        Resolve which model to call based on 'model' + 'model_mode'.
        Subclasses may override to implement 'random' / 'random_free'.
        """
        try:
            mode = (self.get_property("model_mode") or "choose").strip().lower()
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

        provider = (self.get_property("provider") or self.default_provider()).strip().lower()
        api_key = self.resolve_api_key()
        if not api_key:
            self._warn(f"Missing API key for provider '{provider}'. Please set it in node or in Settings (APIKeys).")
            return {}

        base_url = self.resolve_base_url()
        model = self.resolve_model(api_key)

        if provider == "openrouter":
            # Random or random_free modes handled here
            try:
                mode = (self.get_property("model_mode") or "choose").strip().lower()
            except Exception:
                mode = "choose"
            if mode in ("random", "random_free"):
                from aicodeprep_gui.pro.llm.litellm_client import LLMClient
                models = LLMClient.list_models_openrouter(api_key)
                pick = LLMClient.openrouter_pick_model(models, free_only=(mode == "random_free"))
                if not pick:
                    self._warn("Could not pick a model from OpenRouter. Check API key or connectivity.")
                    return {}
                model = pick

        if provider == "compatible" and not base_url:
            self._warn("OpenAI-compatible provider requires a base_url.")
            return {}

        try:
            out = LLMClient.chat(
                model=model,
                user_content=text,
                api_key=api_key,
                base_url=base_url if base_url else None,
                extra_headers=self._extra_headers_for_provider(provider),
                system_content=system
            )
            return {"text": out}
        except LLMError as e:
            self._warn(str(e))
            return {}

    def _extra_headers_for_provider(self, provider: str) -> Dict[str, str]:
        """
        OpenRouter requires Accept and optionally HTTP-Referer/Title. We'll provide minimal Accept.
        """
        provider = provider.lower()
        if provider == "openrouter":
            return {"Accept": "application/json"}
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
            # Provide hints for UI
            self.create_property("ui_hint_models", "Choose a model id, or set model_mode to 'random' or 'random_free'")
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
            self.set_property("base_url", "")  # OpenAI official does not need base_url
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