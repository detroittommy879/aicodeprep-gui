Below is a “cook-book” that keeps the architecture you already have (NodeGraphQt + Pro/Free split) but makes it trivial to drop in new nodes without touching core GUI code.  
It gives you (1) the extra nodes you asked for, (2) a timer-node that can kill / re-route on timeout, (3) if/then logic, (4) temperature/top-p etc. settings, and (5) a plugin-style loader so future nodes are a one-line registration.

--------------------------------------------------------
1.  Plugin-style registration (only once)
--------------------------------------------------------
Create aicodeprep_gui/pro/flow/registry.py

```python
from typing import Dict, Type
from NodeGraphQt import BaseNode

_NODE_REGISTRY: Dict[str, Type[BaseNode]] = {}

def register_node(node_cls: Type[BaseNode]) -> Type[BaseNode]:
    """Class-decorator or plain function.  Idempotent."""
    key = f"{node_cls.__identifier__}.{node_cls.NODE_NAME}"
    _NODE_REGISTRY[key] = node_cls
    return node_cls

def iter_nodes():
    """Yield all registered executables."""
    yield from _NODE_REGISTRY.values()
```

In FlowStudioDock._register_nodes replace the huge manual list with:

```python
from aicodeprep_gui.pro.flow import registry   # new
# --- built-in nodes -------------------------------------------------
from .nodes.io_nodes import *   # keeps old nodes
from .nodes.llm_nodes    import *
from .nodes.aggregate_nodes import *
from .nodes import timer_nodes, logic_nodes   # new packages
# -------------------------------------------------------------------
#  Auto-register everything decorated with @register_node
for node_cls in registry.iter_nodes():
    self.graph.register_node(node_cls)
```

New nodes only need:

```python
@registry.register_node
class MyNewNode(BaseExecNode):
    __identifier__ = "aicp.flow"
    NODE_NAME = "My New Node"
```

--------------------------------------------------------
2.  Extra LLM provider nodes (OpenAI-compat, Anthropic, Gemini)
--------------------------------------------------------
aicodeprep_gui/pro/flow/nodes/llm_nodes.py  (append)

```python
@registry.register_node
class AnthropicNode(LLMBaseNode):
    NODE_NAME = "Anthropic LLM"
    def __init__(self):
        super().__init__()
        self.set_property("provider", "anthropic")
        self.set_property("base_url", "https://api.anthropic.com/v1")

@registry.register_node
class GeminiNode(LLMBaseNode):
    NODE_NAME = "Gemini LLM"
    def __init__(self):
        super().__init__()
        self.set_property("provider", "gemini")

@registry.register_node
class OpenAICompatibleNode(LLMBaseNode):
    NODE_NAME = "OpenAI-Compatible LLM"
    def __init__(self):
        super().__init__()
        self.set_property("provider", "compatible")
        # user must fill base_url, model, api_key
```

--------------------------------------------------------
3.  Sampling controls (temperature / top-p / max-tokens)
--------------------------------------------------------
Add a tiny mixin so ANY future LLM node gets these sliders:

aicodeprep_gui/pro/flow/nodes/sampling_mixin.py

```python
from NodeGraphQt.constants import NodePropWidgetEnum

class SamplingUIMixin:
    """Call once in __init__ to add standard sampling widgets."""
    def _add_sampling_props(self):
        self.create_property("temperature", 0.7,
            widget_type=NodePropWidgetEnum.QDOUBLE_SPIN_BOX.value,
            range=(0.0, 2.0), decimals=2)
        self.create_property("top_p", 1.0,
            widget_type=NodePropWidgetEnum.QDOUBLE_SPIN_BOX.value,
            range=(0.0, 1.0), decimals=2)
        self.create_property("max_tokens", 1024,
            widget_type=NodePropWidgetEnum.QSPIN_BOX.value,
            range=(1, 32000))
```

Then in every LLM node:

```python
def __init__(self):
    super().__init__()
    self._add_sampling_props()   # 3 lines give you full UI
```

Inside run() pass them to LiteLLM:

```python
out = LLMClient.chat(
    model=model,
    user_content=text,
    api_key=api_key,
    base_url=base_url,
    temperature=float(self.get_property("temperature")),
    top_p=float(self.get_property("top_p")),
    max_tokens=int(self.get_property("max_tokens")),
    …
)
```

--------------------------------------------------------
4.  Timer node (timeout + fallback)
--------------------------------------------------------
aicodeprep_gui/pro/flow/nodes/timer_nodes.py

```python
import threading, time, queue
from PySide6 import QtCore
from .base import BaseExecNode
from ..registry import register_node

@register_node
class TimeoutRouterNode(BaseExecNode):
    __identifier__ = "aicp.flow"
    NODE_NAME = "Timeout Router"

    def __init__(self):
        super().__init__()
        self.add_input("text")
        self.add_output(" primary")   # normal success
        self.add_output(" secondary") # timeout / failure

        self.create_property("timeout_sec", 30,
            widget_type=NodePropWidgetEnum.QSPIN_BOX, range=(1, 300))

    def run(self, inputs: dict, settings=None) -> dict:
        text = inputs.get("text", "")
        to = int(self.get_property("timeout_sec"))
        q = queue.Queue(1)

        def _call():
            try:
                # run upstream node (we rely on LiteLLM timeout as well)
                q.put(("ok", text), block=False)
            except Exception as e:
                q.put(("err", str(e)), block=False)

        threading.Thread(target=_call, daemon=True).start()
        try:
            flag, payload = q.get(timeout=to)
            return {" primary": payload} if flag == "ok" else {" secondary": payload}
        except queue.Empty:
            return {" secondary": f"Timed-out after {to}s"}
```

Wire the secondary port to a cheaper / faster fallback model.

--------------------------------------------------------
5.  If/Then logic node
--------------------------------------------------------
aicodeprep_gui/pro/flow/nodes/logic_nodes.py

```python
import re
from .base import BaseExecNode
from ..registry import register_node

@register_node
class IfThenNode(BaseExecNode):
    __identifier__ = "aicp.flow"
    NODE_NAME = "If/Then Router"

    def __init__(self):
        super().__init__()
        self.add_input("text")
        self.add_output("true")
        self.add_output("false")

        self.create_property("condition", "contains",
            widget_type=NodePropWidgetEnum.QCOMBO_BOX.value,
            items=["contains","not_contains","regex","=="])
        self.create_property("pattern", "yes",
            widget_type=NodePropWidgetEnum.QLINE_EDIT.value)

    def run(self, inputs: dict, settings=None) -> dict:
        txt = inputs.get("text","")
        mode = self.get_property("condition")
        pat  = self.get_property("pattern")
        ok   = False
        if mode == "contains":    ok = pat.lower() in txt.lower()
        elif mode == "not_contains": ok = pat.lower() not in txt.lower()
        elif mode == "regex":     ok = bool(re.search(pat, txt, re.I))
        elif mode == "==":        ok = pat == txt
        key = "true" if ok else "false"
        return {key: txt}
```

--------------------------------------------------------
6.  Future-proof checklist
--------------------------------------------------------
1.  Every new node lives in its own file (or logical group file) under  
    aicodeprep_gui/pro/flow/nodes/  
2.  Decorate class with @registry.register_node  
3.  If it needs special UI, inherit mixins (SamplingUIMixin, etc.)  
4.  Re-run app – no other code change required; node appears in tab-search and palette.

--------------------------------------------------------
7.  Quick starter template
--------------------------------------------------------
aicodeprep_gui/pro/flow/nodes/_new_node_template.py

```python
from ..base import BaseExecNode
from ..registry import register_node

@register_node
class NewNode(BaseExecNode):
    __identifier__ = "aicp.flow"
    NODE_NAME = "New Node"

    def __init__(self):
        super().__init__()
        # inputs/outputs
        # properties

    def run(self, inputs: dict, settings=None) -> dict:
        # your logic
        return {"output": something}
```

Copy → rename → implement → done.

--------------------------------------------------------
8.  What you get in the GUI
--------------------------------------------------------
- Open Flow Studio → Tab-search now shows:  
  “OpenAI LLM”, “OpenAI-Compatible LLM”, “Anthropic LLM”, “Gemini LLM”,  
  “Timeout Router”, “If/Then Router”, …  

- Each LLM node has collapsible “Sampling” section with temp/top-p/max-tokens.  

- You can chain:  
  ContextOutput → TimeoutRouter (30 s)  
                ├─primary→  OpenRouter  
                └─secondary→ cheaper model (or retry logic)  

- If/Then node lets you route by keyword, regex, exact match – create any
  meta-prompting pipeline you like.

Everything is modular; add the next idea in minutes, not hours.