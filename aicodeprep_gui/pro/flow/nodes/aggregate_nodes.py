"""Aggregation nodes for Flow Studio including Best-of-N synthesis."""

from __future__ import annotations
from typing import Any, Dict, Optional
import logging

from .base import BaseExecNode
from aicodeprep_gui.pro.llm.litellm_client import LLMClient, LLMError

# Import NodeGraphQt constants for property widget types
try:
    from NodeGraphQt.constants import NodePropWidgetEnum
except ImportError:
    class NodePropWidgetEnum:
        QLINE_EDIT = 3
        QTEXT_EDIT = 4
        QCOMBO_BOX = 5
        QSPINBOX = 9  # For numeric spinners

# Guard Qt import for popups
try:
    from PySide6 import QtWidgets
except ImportError:
    QtWidgets = None


BEST_OF_DEFAULT_PROMPT = (
    "You will receive:\n"
    "- The original context (the code and the user question/prompt),\n"
    "- N candidate answers from different models.\n\n"
    "Task:\n"
    "1) Analyze the strengths and weaknesses of each candidate.\n"
    "2) Synthesize a 'best of all' answer that is better than any single one.\n"
    "3) Where relevant, cite brief pros/cons observed.\n"
    "4) Ensure the final answer is complete, correct, and practical.\n"
)


class BestOfNNode(BaseExecNode):
    """Best-of-N synthesizer node that analyzes multiple candidate outputs."""
    __identifier__ = "aicp.flow"
    NODE_NAME = "Best-of-N Synthesizer"

    def __init__(self):
        super().__init__()
        # Inputs
        self.add_input("context")  # the original context text

        # Create up to 10 candidate input slots
        # The node will automatically use however many are connected
        self.MAX_CANDIDATES = 10
        for i in range(1, self.MAX_CANDIDATES + 1):
            self.add_input(f"candidate{i}")

        self.add_output("text")

        # Properties for the LLM used for synthesis
        # openrouter | openai | gemini | compatible
        self.create_property("provider", "openrouter", widget_type=NodePropWidgetEnum.QCOMBO_BOX.value,
                             items=["openrouter", "openai", "gemini", "compatible"])
        self.create_property(
            "api_key", "", widget_type=NodePropWidgetEnum.QLINE_EDIT.value)
        self.create_property(
            "base_url", "https://openrouter.ai/api/v1", widget_type=NodePropWidgetEnum.QLINE_EDIT.value)
        # if provider=openrouter, supports 'random'/'random_free' via model_mode
        self.create_property(
            "model", "", widget_type=NodePropWidgetEnum.QLINE_EDIT.value)
        # choose | random | random_free
        self.create_property("model_mode", "random_free", widget_type=NodePropWidgetEnum.QCOMBO_BOX.value,
                             items=["choose", "random", "random_free"])
        # Use QTEXT_EDIT widget type for multiline editing
        try:
            self.create_property(
                "extra_prompt", BEST_OF_DEFAULT_PROMPT, widget_type=NodePropWidgetEnum.QTEXT_EDIT.value)
        except Exception:
            # Fallback for older NodeGraphQt versions
            self.create_property("extra_prompt", BEST_OF_DEFAULT_PROMPT)

    def _warn(self, msg: str):
        """Show warning message to user."""
        if QtWidgets is not None:
            try:
                QtWidgets.QMessageBox.warning(None, self.NODE_NAME, msg)
            except Exception:
                logging.warning(f"[{self.NODE_NAME}] {msg}")
        else:
            logging.warning(f"[{self.NODE_NAME}] {msg}")

    def run(self, inputs: Dict[str, Any], settings: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute the Best-of-N synthesis."""
        context = (inputs.get("context") or "").strip()
        candidates = []

        # Automatically collect all connected candidates
        # Iterate through candidate1, candidate2, etc. and collect what's present
        for i in range(1, self.MAX_CANDIDATES + 1):
            key = f"candidate{i}"
            if key in inputs:
                v = (inputs.get(key) or "").strip()
                if v:
                    candidates.append(v)
            else:
                # Stop at first unconnected slot
                break

        logging.info(
            f"[{self.NODE_NAME}] Auto-detected {len(candidates)} connected candidate(s), context length: {len(context)}")
        logging.info(
            f"[{self.NODE_NAME}] All input keys: {list(inputs.keys())}")
        for idx, cand in enumerate(candidates, 1):
            logging.info(
                f"[{self.NODE_NAME}] Candidate {idx} length: {len(cand)}")

        if not context:
            self._warn("Missing 'context' input.")
            return {}
        if not candidates:
            self._warn(
                "No candidate inputs provided. Check that LLM nodes produced output.")
            logging.error(
                f"[{self.NODE_NAME}] Input keys received: {list(inputs.keys())}")
            for key, val in inputs.items():
                logging.error(
                    f"[{self.NODE_NAME}] {key}: {type(val)} = {repr(val)[:100]}")
            return {}

        provider = (self.get_property("provider")
                    or "openrouter").strip().lower()
        api_key = self.get_property("api_key") or ""
        base_url = self.get_property("base_url") or ""
        model = self.get_property("model") or ""
        mode = (self.get_property("model_mode")
                or "random_free").strip().lower()
        extra_prompt = self.get_property(
            "extra_prompt") or BEST_OF_DEFAULT_PROMPT

        # Resolve API key from config if missing
        if not api_key:
            try:
                from aicodeprep_gui.config import get_api_key
                api_key = get_api_key(provider)
            except Exception:
                pass

        if not api_key:
            from aicodeprep_gui.config import get_config_dir
            config_dir = get_config_dir()
            self._warn(
                f"Missing API key for provider '{provider}'.\n\nPlease edit: {config_dir / 'api-keys.toml'}\n\nAdd your API key under [{provider}] section.")
            return {}

        # Resolve model for OpenRouter random/random_free if needed
        if provider == "openrouter":
            if mode in ("random", "random_free"):
                models = LLMClient.list_models_openrouter(api_key)
                pick = LLMClient.openrouter_pick_model(
                    models, free_only=(mode == "random_free"))
                if not pick:
                    self._warn(
                        "Could not pick a model from OpenRouter for synthesis.")
                    return {}
                # LiteLLM requires 'openrouter/' prefix
                model = f"openrouter/{pick}"
            elif model:
                # User provided a model - ensure proper prefix
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

        # Build synthesis prompt
        # We'll pass in everything as user content; system message left empty
        lines = [extra_prompt, "\n---\nOriginal Context:\n",
                 context, "\n---\nCandidate Answers:\n"]
        for idx, c in enumerate(candidates, 1):
            lines.append(f"\n[Candidate {idx}]\n{c}\n")
        user_text = "".join(lines)

        try:
            out = LLMClient.chat(
                model=model,
                user_content=user_text,
                api_key=api_key,
                base_url=(base_url if provider in (
                    "openrouter", "compatible") else None),
                extra_headers={
                    "Accept": "application/json"} if provider == "openrouter" else None,
                system_content=None
            )
            return {"text": out}
        except LLMError as e:
            self._warn(str(e))
            return {}
