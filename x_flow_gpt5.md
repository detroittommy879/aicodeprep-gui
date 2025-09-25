Title: Phase 1 – Execute Flow Studio with LiteLLM: Multi-provider routing, Best-of-N synthesis, Clipboard/File output

Goal (high-level)

- Turn the current Flow Studio (NodeGraphQt) visuals into an executable flow engine.
- Add nodes for calling LLMs via LiteLLM (OpenRouter, OpenAI, Gemini, OpenAI-compatible).
- Add a “Best-of-N” synthesis node that takes N outputs and generates a best version by prompting another LLM.
- Provide a ready-to-run built-in flow template: ContextOutput -> 5x OpenRouter model nodes -> BestOfN synthesis -> Clipboard + FileWrite(best_of_n.txt).
- Allow selecting models from dropdowns (with special “random” and “random_free” on OpenRouter).
- Use QSettings-backed API keys by default; show a popup if missing at run-time.
- Keep it simple and synchronous (sequential) for now; context window checks can be added later.

Important notes

- We will not use the LiteLLM proxy. Only the Python library.
- We’ll keep Pro-vs-Free gating relaxed: Run Flow should work for everyone so you can test. (Read-only edit gating can remain in Free).
- Execution is single-threaded in Phase 1 to keep code simple.
- We add a small “simple flow language” loader for easy AI/typed graph generation later (optional), and a built-in loader function that programmatically builds the best-of-5 OpenRouter graph.

Task 0 – Create a new branch

- Create a new branch for this development: feature/flow-exec-litellm

Task 1 – Add dependency: LiteLLM
File: pyproject.toml
Why: We need LiteLLM to call OpenRouter/OpenAI/Gemini/OpenAI-compatible endpoints with one unified API.

1. In the [project] dependencies list, append:
   "litellm>=1.40.0"

Example patch:

- Find the [project] section with `dependencies = [` and add a new line before the closing `]`:
  "litellm>=1.40.0"

2. Run `pip install -e .` or ensure the environment picks up the dependency.

Task 2 – Add a unified LiteLLM client wrapper
File: aicodeprep_gui/pro/llm/litellm_client.py (new)
Why: Centralize provider-specific headers, base URLs, model-list fetching, and one-shot chat completion logic.

## Create the file with this content:

from **future** import annotations
import os
import json
import random
import logging
from typing import Any, Dict, List, Optional, Tuple

try:
import litellm
except Exception as e:
litellm = None
\_LITELLM_IMPORT_ERROR = e

import requests

class LLMError(Exception):
pass

class LLMClient:
"""
Minimal wrapper on top of LiteLLM for simple chat completions and model listing.
"""

    @staticmethod
    def ensure_lib(parent=None):
        if litellm is None:
            from PySide6 import QtWidgets
            QtWidgets.QMessageBox.critical(
                parent,
                "LiteLLM missing",
                f"litellm is not installed. Please install it first.\n\n{_LITELLM_IMPORT_ERROR}"
            )
            raise LLMError("litellm not installed")

    @staticmethod
    def chat(
        model: str,
        user_content: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        system_content: Optional[str] = None,
    ) -> str:
        """
        Perform a one-shot chat completion.
        """
        LLMClient.ensure_lib()

        headers = extra_headers.copy() if extra_headers else {}
        # LiteLLM uses `api_key` parameter; leave env fallback as-is
        kwargs = {}
        if api_key:
            kwargs["api_key"] = api_key
        if base_url:
            # Some providers (OpenRouter / generic OpenAI-compatible) need base_url
            kwargs["base_url"] = base_url

        messages = []
        if system_content:
            messages.append({"role": "system", "content": system_content})
        messages.append({"role": "user", "content": user_content})

        try:
            resp = litellm.completion(
                model=model,
                messages=messages,
                extra_headers=headers if headers else None,
                **kwargs
            )
            # LiteLLM uses OpenAI response format
            return resp.choices[0].message.get("content", "")
        except Exception as e:
            raise LLMError(f"Chat error: {e}") from e

    # ---- Model listing helpers ----

    @staticmethod
    def list_models_openrouter(api_key: str) -> List[Dict[str, Any]]:
        """
        List models via OpenRouter API: GET https://openrouter.ai/api/v1/models
        """
        url = "https://openrouter.ai/api/v1/models"
        try:
            r = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
            r.raise_for_status()
            data = r.json()
            return data.get("data", [])
        except Exception as e:
            logging.error(f"OpenRouter model list fetch failed: {e}")
            return []

    @staticmethod
    def list_models_openai(api_key: str) -> List[Dict[str, Any]]:
        url = "https://api.openai.com/v1/models"
        try:
            r = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
            r.raise_for_status()
            data = r.json()
            # OpenAI style returns {"data":[{"id":...}, ...]}
            return data.get("data", [])
        except Exception as e:
            logging.error(f"OpenAI model list fetch failed: {e}")
            return []

    @staticmethod
    def list_models_openai_compatible(base_url: str, api_key: str) -> List[Dict[str, Any]]:
        """
        Generic OpenAI-compatible endpoints should have /v1/models or /models
        We'll try both.
        """
        tried = []
        for suffix in ("/v1/models", "/models"):
            url = base_url.rstrip("/") + suffix
            tried.append(url)
            try:
                r = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
                if r.status_code == 404:
                    continue
                r.raise_for_status()
                data = r.json()
                return data.get("data", [])
            except Exception:
                continue
        logging.error(f"OpenAI-compatible models failed. Tried: {', '.join(tried)}")
        return []

    @staticmethod
    def openrouter_pick_model(models: List[Dict[str, Any]], free_only: bool) -> Optional[str]:
        """
        Pick a random model id from OpenRouter's list (optionally only ':free' models).
        """
        ids = []
        for m in models:
            mid = m.get("id") or m.get("name")
            if not mid:
                continue
            if free_only and not mid.endswith(":free"):
                continue
            ids.append(mid)
        if not ids:
            return None
        return random.choice(ids)

---

Task 3 – Add LLM nodes and Best-of-N node
We’ll create two new modules with executable nodes:

3A) File: aicodeprep_gui/pro/flow/nodes/llm_nodes.py (new)
Why: Nodes that call providers via LiteLLM. Accept a `text` input, optional `system`, and produce `text` output.

## Create the file with this content:

from **future** import annotations
import logging
from typing import Any, Dict, Optional

from .base import BaseExecNode
from aicodeprep_gui.pro.llm.litellm_client import LLMClient, LLMError

# Guard Qt import for popups

from PySide6 import QtWidgets

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
        try:
            QtWidgets.QMessageBox.warning(None, self.NODE_NAME, msg)
        except Exception:
            logging.warning(f"[{self.NODE_NAME}] {msg}")

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
        model = self.resolve_model(api_key=api_key)

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
**identifier** = "aicp.flow"
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
**identifier** = "aicp.flow"
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
**identifier** = "aicp.flow"
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
**identifier** = "aicp.flow"
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

---

3B) File: aicodeprep_gui/pro/flow/nodes/aggregate_nodes.py (new)
Why: A Best-of-N synthesizer node that consumes multiple candidate outputs plus original context and calls an LLM to synthesize a best version using an extra prompt.

## Create the file with this content:

from **future** import annotations
from typing import Any, Dict, Optional
import logging

from .base import BaseExecNode
from aicodeprep_gui.pro.llm.litellm_client import LLMClient, LLMError
from PySide6 import QtWidgets

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
**identifier** = "aicp.flow"
NODE_NAME = "Best-of-N Synthesizer"

    def __init__(self):
        super().__init__()
        try:
            # Inputs
            self.add_input("context")  # the original context text
            # We'll provide 5 inputs by default: candidate1..candidate5
            for i in range(1, 6):
                self.add_input(f"candidate{i}")

            self.add_output("text")

            # Properties for the LLM used for synthesis
            self.create_property("provider", "openrouter")   # openrouter | openai | gemini | compatible
            self.create_property("api_key", "")
            self.create_property("base_url", "https://openrouter.ai/api/v1")
            self.create_property("model", "")                # if provider=openrouter, supports 'random'/'random_free' via model_mode
            self.create_property("model_mode", "random_free")# choose | random | random_free
            self.create_property("extra_prompt", BEST_OF_DEFAULT_PROMPT)
        except Exception:
            pass

    def _warn(self, msg: str):
        try:
            QtWidgets.QMessageBox.warning(None, self.NODE_NAME, msg)
        except Exception:
            logging.warning(f"[{self.NODE_NAME}] {msg}")

    def run(self, inputs: Dict[str, Any], settings: Optional[Dict] = None) -> Dict[str, Any]:
        context = (inputs.get("context") or "").strip()
        candidates = []
        for i in range(1, 100):  # support more than 5 later
            key = f"candidate{i}"
            if key not in inputs:
                break
            v = (inputs.get(key) or "").strip()
            if v:
                candidates.append(v)

        if not context:
            self._warn("Missing 'context' input.")
            return {}
        if not candidates:
            self._warn("No candidate inputs provided.")
            return {}

        provider = (self.get_property("provider") or "openrouter").strip().lower()
        api_key = self.get_property("api_key") or ""
        base_url = self.get_property("base_url") or ""
        model = self.get_property("model") or ""
        mode = (self.get_property("model_mode") or "random_free").strip().lower()
        extra_prompt = self.get_property("extra_prompt") or BEST_OF_DEFAULT_PROMPT

        # Resolve API key from QSettings if missing
        if not api_key:
            try:
                from PySide6 import QtCore
                settings = QtCore.QSettings("aicodeprep-gui", "APIKeys")
                settings.beginGroup(provider)
                api_key = settings.value("api_key", "", type=str)
                settings.endGroup()
            except Exception:
                pass

        if not api_key:
            self._warn("Missing API key for synthesis. Set in node or via Settings (APIKeys).")
            return {}

        # Resolve model for OpenRouter random/random_free if needed
        if provider == "openrouter" and (mode in ("random", "random_free")):
            from aicodeprep_gui.pro.llm.litellm_client import LLMClient
            models = LLMClient.list_models_openrouter(api_key)
            pick = LLMClient.openrouter_pick_model(models, free_only=(mode == "random_free"))
            if not pick:
                self._warn("Could not pick a model from OpenRouter for synthesis.")
                return {}
            model = pick

        # Build synthesis prompt
        # We'll pass in everything as user content; system message left empty
        lines = [extra_prompt, "\n---\nOriginal Context:\n", context, "\n---\nCandidate Answers:\n"]
        for idx, c in enumerate(candidates, 1):
            lines.append(f"\n[Candidate {idx}]\n{c}\n")
        user_text = "".join(lines)

        try:
            out = LLMClient.chat(
                model=model,
                user_content=user_text,
                api_key=api_key,
                base_url=(base_url if provider in ("openrouter", "compatible") else None),
                extra_headers={"Accept": "application/json"} if provider == "openrouter" else None,
                system_content=None
            )
            return {"text": out}
        except LLMError as e:
            self._warn(str(e))
            return {}

---

Task 4 – Make IO nodes executable (Clipboard/File/ContextOutput)
File: aicodeprep_gui/pro/flow/nodes/io_nodes.py
Why: These currently only define ports/properties. We add a run() to make them do work.

1. Open file and replace the entire content with the following updated version:

---

"""I/O nodes for Flow Studio (Phase 1 - executable)."""

# Guard NodeGraphQt import so non-installed environments still launch the app.

try:
from NodeGraphQt import BaseNode # type: ignore
except Exception as e: # pragma: no cover
class BaseNode: # minimal stub to keep imports safe; not used without NodeGraphQt
def **init**(self, \*args, \*\*kwargs):
raise ImportError(
"NodeGraphQt is required for Flow Studio nodes. "
f"Original import error: {e}"
)

from .base import BaseExecNode
from typing import Any, Dict, Optional
import os
from PySide6 import QtWidgets

class ContextOutputNode(BaseExecNode):
**identifier** = "aicp.flow"
NODE_NAME = "Context Output"

    def __init__(self):
        super().__init__()
        # Outputs
        try:
            self.add_output("text")
        except Exception:
            pass

        # Properties
        try:
            self.create_property("path", "fullcode.txt")
            self.create_property("use_latest_generated", True)
        except Exception:
            pass

    def run(self, inputs: Dict[str, Any], settings: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Read the context text from path (default: fullcode.txt).
        In future we could regenerate context on-demand.
        """
        path = self.get_property("path") or "fullcode.txt"
        abspath = os.path.join(os.getcwd(), path)
        if not os.path.isfile(abspath):
            QtWidgets.QMessageBox.warning(None, self.NODE_NAME, f"Context file not found: {abspath}")
            return {}
        try:
            with open(abspath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            return {"text": content}
        except Exception as e:
            QtWidgets.QMessageBox.warning(None, self.NODE_NAME, f"Error reading context file: {e}")
            return {}

class ClipboardNode(BaseExecNode):
**identifier** = "aicp.flow"
NODE_NAME = "Clipboard"

    def __init__(self):
        super().__init__()
        try:
            self.add_input("text")
        except Exception:
            pass

    def run(self, inputs: Dict[str, Any], settings: Optional[Dict] = None) -> Dict[str, Any]:
        text = inputs.get("text") or ""
        if not text:
            return {}
        try:
            clip = QtWidgets.QApplication.clipboard()
            clip.setText(text)
        except Exception:
            pass
        return {}

class FileWriteNode(BaseExecNode):
**identifier** = "aicp.flow"
NODE_NAME = "File Write"

    def __init__(self):
        super().__init__()
        try:
            self.add_input("text")
        except Exception:
            pass

        try:
            self.create_property("path", "fullcode.txt")
        except Exception:
            pass

    def run(self, inputs: Dict[str, Any], settings: Optional[Dict] = None) -> Dict[str, Any]:
        text = inputs.get("text") or ""
        path = self.get_property("path") or "output.txt"
        abspath = os.path.join(os.getcwd(), path)
        try:
            with open(abspath, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            QtWidgets.QMessageBox.warning(None, self.NODE_NAME, f"Failed writing file: {e}")
        return {}

class OutputDisplayNode(BaseExecNode):
**identifier** = "aicp.flow"
NODE_NAME = "Output Display"

    def __init__(self):
        super().__init__()
        try:
            self.add_input("text")
            self.create_property("last_result", "")
        except Exception:
            pass

    def run(self, inputs: Dict[str, Any], settings: Optional[Dict] = None) -> Dict[str, Any]:
        text = inputs.get("text") or ""
        # Store it so Properties Bin can show it
        try:
            self.set_property("last_result", text)
        except Exception:
            pass
        return {}

---

Task 5 – Add a small execution engine
File: aicodeprep_gui/pro/flow/engine.py (new)
Why: Traverse the NodeGraphQt graph, compute a topological order, and run nodes with input dictionaries built from connected outputs.

## Create the file with this content:

from **future** import annotations
from typing import Any, Dict, List, Tuple, Set, Optional
import logging

# Qt for popups

from PySide6 import QtWidgets, QtCore

def _safe_node_id(node) -> str:
try:
return str(node.id)
except Exception:
return f"node_{id(node)}"

def \_input_ports(node): # Try various APIs across NodeGraphQt versions
for api in ("input_ports", "inputs"):
if hasattr(node, api):
try:
ports = getattr(node, api)() # Ensure list
if isinstance(ports, dict):
return list(ports.values())
return list(ports)
except Exception:
pass # Fallback: try iterating 'inputs()' if it's an iterator
try:
return list(node.inputs())
except Exception:
return []

def \_output_ports(node):
for api in ("output_ports", "outputs"):
if hasattr(node, api):
try:
ports = getattr(node, api)()
if isinstance(ports, dict):
return list(ports.values())
return list(ports)
except Exception:
pass
try:
return list(node.outputs())
except Exception:
return []

def _port_name(port) -> str:
for name_attr in ("name", "port_name", "label"):
if hasattr(port, name_attr):
try:
return str(getattr(port, name_attr))
except Exception:
continue
return f"port_{id(port)}"

def \_connected_input_sources(port) -> List[Tuple[Any, Any]]:
"""
For an input port, return list of (src_node, src_port) connected to it.
"""
out = []
for api in ("connected_ports", "connections"):
if hasattr(port, api):
try:
conns = getattr(port, api)() # Normalize to list of ports (src or dst)
for cp in conns:
try:
n = cp.node()
if hasattr(cp, "port_type") and getattr(cp, "port_type") == "in": # cp is an input; we want the other side if available
pass
out.append((n, cp))
except Exception:
continue
if out:
return out
except Exception:
continue # If no direct API, return empty (no connection)
return []

def topological_order(nodes) -> List[Any]:
"""
Best-effort topological order using input connections as dependencies.
"""
node_list = list(nodes)
indeg: Dict[str, int] = {}
id_to_node: Dict[str, Any] = {}

    # Build indegree
    for n in node_list:
        nid = _safe_node_id(n)
        id_to_node[nid] = n
        indeg[nid] = 0

    for n in node_list:
        nid = _safe_node_id(n)
        for ip in _input_ports(n):
            srcs = _connected_input_sources(ip)
            for (src_node, src_port) in srcs:
                if src_node is None:
                    continue
                sid = _safe_node_id(src_node)
                if sid in indeg and sid != nid:
                    indeg[nid] += 1

    # Kahn
    queue = [id_to_node[nid] for nid, d in indeg.items() if d == 0]
    order: List[Any] = []
    visited: Set[str] = set()

    while queue:
        u = queue.pop(0)
        uid = _safe_node_id(u)
        if uid in visited:
            continue
        visited.add(uid)
        order.append(u)

        # Decrement indeg of neighbors
        for v in node_list:
            vid = _safe_node_id(v)
            if vid in visited:
                continue
            # If v depends on u
            dep = False
            for ip in _input_ports(v):
                for (src_node, src_port) in _connected_input_sources(ip):
                    if src_node and _safe_node_id(src_node) == uid:
                        dep = True
                        break
                if dep:
                    break
            if dep:
                indeg[vid] -= 1
                if indeg[vid] <= 0:
                    queue.append(v)

    # If cycle, just append remaining
    if len(order) < len(node_list):
        for n in node_list:
            if n not in order:
                order.append(n)

    return order

def \_gather_inputs_for_node(graph, node, results: Dict[Tuple[str, str], Any]) -> Dict[str, Any]:
"""
Build {input_port_name: value} from upstream results.
"""
inputs: Dict[str, Any] = {}
for ip in \_input_ports(node):
ip_name = \_port_name(ip)
srcs = \_connected_input_sources(ip)
if not srcs:
continue # Take the first source by default (multi-in ports merge strategy can be added later)
src_node, src_port = srcs[0]
out_key = (\_safe_node_id(src_node), \_port_name(src_port))
if out_key in results:
inputs[ip_name] = results[out_key]
return inputs

def execute_graph(graph, parent_widget=None) -> None:
"""
Execute the entire graph once in topological order.
"""
try:
nodes = graph.all_nodes()
except Exception as e:
QtWidgets.QMessageBox.warning(parent_widget, "Run Flow", f"Graph error: {e}")
return

    order = topological_order(nodes)
    results: Dict[Tuple[str, str], Any] = {}

    for node in order:
        # Some nodes are BaseExecNode; check for run()
        if not hasattr(node, "run") or not callable(getattr(node, "run")):
            # Skip non-exec nodes (cosmetic)
            continue

        # Build inputs from upstream outputs
        in_data = _gather_inputs_for_node(graph, node, results)
        try:
            out = node.run(in_data, settings=None) or {}
        except Exception as e:
            logging.error(f"Node '{getattr(node, 'NODE_NAME', 'node')}' failed: {e}")
            QtWidgets.QMessageBox.warning(parent_widget, "Run Flow", f"Node failed: {e}")
            out = {}

        # Store outputs
        for op in _output_ports(node):
            oname = _port_name(op)
            if oname in out:
                results[(_safe_node_id(node), oname)] = out[oname]

---

Task 6 – Wire Run button, register new nodes, and add a built-in template
File: aicodeprep_gui/pro/flow/flow_dock.py
Why: Enable Run Flow, register LLM nodes and BestOfN node, and add a helper to build the best-of-5 graph.

1. In \_create_toolbar(self), find:
   self.\_act_run = toolbar.addAction("Run Flow")
   self.\_act_run.setEnabled(False)
   Replace those two lines with:
   self.\_act_run = toolbar.addAction("Run Flow")
   self.\_act_run.setEnabled(True)
   self.\_act_run.triggered.connect(self.\_on_run_clicked)

2. Add a private method \_on_run_clicked(self) to call the engine and show errors.
   Find a place under the toolbar handlers section and add:
   def \_on_run_clicked(self):
   try:
   from .engine import execute_graph
   execute_graph(self.graph, parent_widget=self)
   except Exception as e:
   from PySide6 import QtWidgets
   QtWidgets.QMessageBox.warning(self, "Run Flow", f"Execution failed: {e}")

3. Register our new nodes (LLM and BestOfN)
   In def \_register_nodes(self), extend the import and registration.

Replace the entire \_register_nodes method body with:
def \_register_nodes(self):
try:
from .nodes.io_nodes import (
ContextOutputNode,
ClipboardNode,
FileWriteNode,
OutputDisplayNode,
)
from .nodes.llm_nodes import (
OpenRouterNode,
OpenAINode,
GeminiNode,
OpenAICompatibleNode,
)
from .nodes.aggregate_nodes import BestOfNNode

            self.graph.register_node(ContextOutputNode)
            self.graph.register_node(ClipboardNode)
            self.graph.register_node(FileWriteNode)
            self.graph.register_node(OutputDisplayNode)

            self.graph.register_node(OpenRouterNode)
            self.graph.register_node(OpenAINode)
            self.graph.register_node(GeminiNode)
            self.graph.register_node(OpenAICompatibleNode)

            self.graph.register_node(BestOfNNode)
        except Exception as e:
            logging.error(f"Failed to register Flow Studio nodes: {e}")

4.  Add a helper to programmatically build the “Best-of-5 OpenRouter” template
    Still in flow_dock.py, add a new method near \_load_default_flow_or_build:

        def load_template_best_of_5_openrouter(self):
            """
            Build:
                ContextOutput -> [5x OpenRouter LLM nodes] -> BestOfNNode -> Clipboard + FileWrite(best_of_n.txt)
            """
            try:
                # Clear graph first (best-effort)
                try:
                    if hasattr(self.graph, "clear_session"):
                        self.graph.clear_session()
                    else:
                        for n in list(getattr(self.graph, "all_nodes", lambda: [])()):
                            try:
                                if hasattr(self.graph, "delete_node"):
                                    self.graph.delete_node(n)
                            except Exception:
                                continue
                except Exception:
                    pass

                # Create nodes
                from .nodes.io_nodes import ContextOutputNode, ClipboardNode, FileWriteNode
                from .nodes.llm_nodes import OpenRouterNode
                from .nodes.aggregate_nodes import BestOfNNode

                ctx = self._create_node_compat(ContextOutputNode, "aicp.flow", "Context Output", (0, 0))

                or_nodes = []
                x = 350
                y = -200
                for i in range(5):
                    n = self._create_node_compat(OpenRouterNode, "aicp.flow", "OpenRouter LLM", (x, y + i * 100))
                    if n and hasattr(n, "set_property"):
                        n.set_property("model_mode", "random_free")
                        n.set_property("model", "")  # left blank, random_free will pick
                    or_nodes.append(n)

                best = self._create_node_compat(BestOfNNode, "aicp.flow", "Best-of-N Synthesizer", (700, 0))
                if best and hasattr(best, "set_property"):
                    best.set_property("provider", "openrouter")
                    best.set_property("model_mode", "random_free")
                    # base_url already defaulted to OpenRouter

                clip = self._create_node_compat(ClipboardNode, "aicp.flow", "Clipboard", (1050, -60))
                fwr = self._create_node_compat(FileWriteNode, "aicp.flow", "File Write", (1050, 60))
                if fwr and hasattr(fwr, "set_property"):
                    fwr.set_property("path", "best_of_n.txt")

                # Wire: ctx.text -> each OpenRouter input.text
                try:
                    out_text = None
                    if hasattr(ctx, "get_output_by_name"):
                        out_text = ctx.get_output_by_name("text")
                    elif hasattr(ctx, "output_port"):
                        out_text = ctx.output_port("text")

                    for n in or_nodes:
                        if not n:
                            continue
                        in_text = None
                        if hasattr(n, "get_input_by_name"):
                            in_text = n.get_input_by_name("text")
                        elif hasattr(n, "input_port"):
                            in_text = n.input_port("text")
                        if out_text and in_text:
                            self.graph.connect_ports(out_text, in_text)
                except Exception as e:
                    logging.error(f"Failed connecting ctx->OpenRouter: {e}")

                # Wire: ctx.text -> best.context
                try:
                    best_in_ctx = best.get_input_by_name("context") if hasattr(best, "get_input_by_name") else None
                    out_text = ctx.get_output_by_name("text") if hasattr(ctx, "get_output_by_name") else None
                    if out_text and best_in_ctx:
                        self.graph.connect_ports(out_text, best_in_ctx)
                except Exception as e:
                    logging.error(f"Failed connecting ctx->best.context: {e}")

                # Wire: each OR.text -> best.candidate{i}
                try:
                    for i, n in enumerate(or_nodes, 1):
                        if not n:
                            continue
                        or_out = n.get_output_by_name("text") if hasattr(n, "get_output_by_name") else None
                        best_in = best.get_input_by_name(f"candidate{i}") if hasattr(best, "get_input_by_name") else None
                        if or_out and best_in:
                            self.graph.connect_ports(or_out, best_in)
                except Exception as e:
                    logging.error(f"Failed connecting OpenRouter->best candidates: {e}")

                # Wire: best.text -> Clipboard + FileWrite.text
                try:
                    best_out = best.get_output_by_name("text") if hasattr(best, "get_output_by_name") else None
                    in_clip = clip.get_input_by_name("text") if hasattr(clip, "get_input_by_name") else None
                    in_fwr  = fwr.get_input_by_name("text")  if hasattr(fwr, "get_input_by_name")  else None
                    if best_out and in_clip:
                        self.graph.connect_ports(best_out, in_clip)
                    if best_out and in_fwr:
                        self.graph.connect_ports(best_out, in_fwr)
                except Exception as e:
                    logging.error(f"Failed connecting best->outputs: {e}")

                # Optional auto-layout
                try:
                    if hasattr(self.graph, "auto_layout_nodes"):
                        self.graph.auto_layout_nodes()
                except Exception:
                    pass

            except Exception as e:
                logging.error(f"load_template_best_of_5_openrouter failed: {e}")

5.  Optional: Keep read-only gating, but allow Run in Free
    We already enabled Run unconditionally above.

Task 7 – Add Flow menu items to main window for easy access
File: aicodeprep_gui/gui/main_window.py
Why: Allow loading the built-in best-of-5 template and trigger Run from the menu, leveraging the Flow Studio dock.

1.  In **init**, after building Flow menu:
    Find this section (it already creates flow_menu and import/export/reset actions):

            flow_menu = mb.addMenu("&Flow")

            flow_import_act = QtGui.QAction("Import Flow JSON…", self)
            flow_import_act.triggered.connect(self._flow_import_action)
            flow_menu.addAction(flow_import_act)

            flow_export_act = QtGui.QAction("Export Flow JSON…", self)
            flow_export_act.triggered.connect(self._flow_export_action)
            flow_menu.addAction(flow_export_act)

            flow_reset_act = QtGui.QAction("Reset to Default Flow", self)
            flow_reset_act.triggered.connect(self._flow_reset_action)
            flow_menu.addAction(flow_reset_act)

            flow_menu.addSeparator()

ADD the following two actions right after flow_menu.addSeparator():
flow_bestof5_act = QtGui.QAction("Load Built-in: Best-of-5 (OpenRouter)", self)
def \_load_bestof5():
if not self.\_ensure_flow_dock():
QtWidgets.QMessageBox.warning(self, "Flow Studio", "Flow Studio could not be initialized.")
return
if hasattr(self.flow_dock, "load_template_best_of_5_openrouter"):
self.flow_dock.load_template_best_of_5_openrouter()
self.flow_dock.show()
else:
QtWidgets.QMessageBox.warning(self, "Flow Studio", "Dock missing 'load_template_best_of_5_openrouter'.")

        flow_bestof5_act.triggered.connect(_load_bestof5)
        flow_menu.addAction(flow_bestof5_act)

        flow_run_act = QtGui.QAction("Run Current Flow", self)
        def _run_current_flow():
            if not self._ensure_flow_dock():
                QtWidgets.QMessageBox.warning(self, "Flow Studio", "Flow Studio could not be initialized.")
                return
            if hasattr(self.flow_dock, "_on_run_clicked"):
                self.flow_dock._on_run_clicked()
                self.flow_dock.show()
            else:
                QtWidgets.QMessageBox.warning(self, "Flow Studio", "Dock missing '_on_run_clicked'.")
        flow_run_act.triggered.connect(_run_current_flow)
        flow_menu.addAction(flow_run_act)

Explanation:

- “Load Built-in: Best-of-5 (OpenRouter)” quickly sets up the entire example graph.
- “Run Current Flow” calls the dock’s run handler.

Task 8 – Add API key storage helper (optional)
We’re already reading QSettings in nodes if api_key property is blank. You can help users by providing a trivial “API Keys” dialog later, but not required for Phase 1. For now, users can paste keys directly into node properties via the Properties Bin.

Task 9 – Provide a “simple flow language” JSON (optional) and loader (vNext)

- We’ll skip in Phase 1, since we added a built-in template method and “Import Flow JSON” already works with NodeGraphQt sessions. For the “type what they want” DSL, we’ll add it in Phase 2 when we see what prompts work best. The Best-of-5 loader is a good starting point.

Task 10 – Prepare a sample “flow.json” the user can load (optional)

- Because NodeGraphQt session formats vary, generating them by hand is fragile. Instead, ship the built-in loader in Step 6 and tell users to click Flow -> “Load Built-in: Best-of-5 (OpenRouter)”.
- If you still want a file to load from disk, after loading the template, use Flow -> “Export Flow JSON…” and save it as flow.json in your project. That exported session will be loadable on other machines.

Task 11 – Token/context window check (stub)

- We will not implement full token-window verification in Phase 1. The simplest stub: add a TODO in LLM nodes to fetch model metadata (context window) with /models and compare to `Estimated tokens` in GUI. That will be Phase 2.

Task 12 – Quick smoke test checklist

1. Start app. Ensure Flow Studio toggle shows the dock.
2. Flow -> Load Built-in: Best-of-5 (OpenRouter).
3. Ensure Context Output points to fullcode.txt. First, click “GENERATE CONTEXT!” to create fullcode.txt.
4. Select the Best-of-5 action again to rebuild (optional).
5. Flow -> Run Current Flow.
6. First run will prompt for missing API key (OpenRouter). Enter an API key into the OpenRouter LLM nodes (or add to QSettings under “aicodeprep-gui/APIKeys/openrouter/api_key”).
7. Observe it picks random free models and synthesizes a best-of into the Clipboard and writes best_of_n.txt to disk.
8. Inspect FileWrite node property path and ensure best_of_n.txt exists.

Tip: You can reduce “randomness” by setting specific model ids on each OpenRouter LLM node (set model_mode=choose, model=“model-id”).

Task 13 – Minimal guardrails and logging

- All LLM nodes use QMessageBox warnings to prompt for API key or connectivity issues.
- Execution engine catches node exceptions and keeps going with warnings so users can debug faulty nodes without crashing.

That’s it for Phase 1. You now have:

- Executable flow engine.
- Provider nodes via LiteLLM (OpenRouter, OpenAI, Gemini, OpenAI-compatible).
- Best-of-N synthesis node.
- Built-in best-of-5 template + Run menu items.
- Clipboard and file outputs.
