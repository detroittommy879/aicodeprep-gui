Here’s a roadmap for extending Flow Studio with your new nodes and keeping everything clean, modular and future-proof.

1. Organize your new nodes in pro/flow/nodes  
   • Create e.g.  
     – llm_nodes.py → OpenAI, OpenAI-compatible, Anthropic, Gemini  
     – control_nodes.py → Compare/Regex, If/Then, Switch, Timer, Race/Fallback  
   • Keep each node in its own class inheriting from BaseExecNode.

2. Define a common LLM base so all provider nodes share the same properties.  
   In llm_nodes.py:
   ```python
   from NodeGraphQt.constants import NodePropWidgetEnum
   from .base import BaseExecNode
   from aicodeprep_gui.pro.llm.litellm_client import LLMClient, LLMError

   class LLMProviderNode(BaseExecNode):
     NODE_NAME = "Generic LLM"
     def __init__(self):
       super().__init__()
       self.add_input("text")
       self.add_output("text")
       # common properties
       self.create_property("api_key", "", widget_type=NodePropWidgetEnum.QLINE_EDIT.value)
       self.create_property("base_url", "", widget_type=NodePropWidgetEnum.QLINE_EDIT.value)
       self.create_property("model", "", widget_type=NodePropWidgetEnum.QCOMBO_BOX.value, items=[])
       self.create_property("temperature", 0.7, widget_type=NodePropWidgetEnum.QLINE_EDIT.value)
       self.create_property("top_p", 1.0, widget_type=NodePropWidgetEnum.QLINE_EDIT.value)
       self.create_property("timeout", 60, widget_type=NodePropWidgetEnum.QLINE_EDIT.value)
     def run(self, inputs, settings=None):
       text = inputs.get("text","")
       api_key = self.get_property("api_key")
       base_url = self.get_property("base_url")
       model    = self.get_property("model")
       temp     = float(self.get_property("temperature") or 0)
       top_p    = float(self.get_property("top_p") or 1)
       to       = int(self.get_property("timeout") or 60)
       try:
         resp = LLMClient.chat(
           model=model,
           user_content=text,
           api_key=api_key,
           base_url=base_url or None,
           extra_headers=None,
           system_content=None,
           timeout=to,
           temperature=temp,
           top_p=top_p
         )
         return {"text": resp}
       except LLMError:
         # propagate empty to trigger fallback logic
         return {}
   ```
   Then subclass it for each provider with sensible defaults:  
   ```python
   class OpenAINode(LLMProviderNode):
     NODE_NAME = "OpenAI (official)"
     def __init__(self):
       super().__init__()
       self.set_property("base_url","")  # official
       # you can fetch available models dynamically later
   ```

3. Add logic/control nodes in control_nodes.py  
   a) Compare/Regex node  
   ```python
   class RegexMatchNode(BaseExecNode):
     NODE_NAME = "Regex Match"
     def __init__(self):
       super().__init__()
       self.add_input("text")
       self.add_output("result")    # bool
       self.create_property("pattern","", widget_type=NodePropWidgetEnum.QLINE_EDIT.value)
     def run(self, inputs, _=None):
       import re
       txt = inputs.get("text","")
       pat = self.get_property("pattern") or ""
       return {"result": bool(re.search(pat, txt))}
   ```
   b) If/Then node  
   ```python
   class IfNode(BaseExecNode):
     NODE_NAME = "If / Then"
     def __init__(self):
       super().__init__()
       self.add_input("cond")      # bool
       self.add_input("payload")   # any
       self.add_output("true")
       self.add_output("false")
     def run(self, inputs, _=None):
       c = inputs.get("cond",False)
       p = inputs.get("payload",None)
       return {"true": p if c else "", "false": p if not c else ""}
   ```
   c) Fallback/Race node  
   ```python
   class RaceNode(BaseExecNode):
     NODE_NAME = "Race / Fallback"
     def __init__(self):
       super().__init__()
       # assume up to N inputs: in1, in2, in3...
       for i in range(1,5):
         self.add_input(f"in{i}")
       self.add_output("winner")
     def run(self, inputs, _=None):
       for i in range(1,5):
         t = inputs.get(f"in{i}")
         if t:
           return {"winner":t}
       return {}
   ```
   d) Timer / Delay node  
   ```python
   from PySide6.QtCore import QTimer, QEventLoop
   class TimerNode(BaseExecNode):
     NODE_NAME = "Timer"
     def __init__(self):
       super().__init__()
       self.create_property("ms",1000, widget_type=NodePropWidgetEnum.QLINE_EDIT.value)
       self.add_output("timeout")
     def run(self, inputs,_=None):
       loop=QEventLoop()
       QTimer.singleShot(int(self.get_property("ms") or 0), loop.quit)
       loop.exec()
       return {"timeout":True}
   ```

4. Register your new nodes  
   In FlowStudioDock._register_nodes (pro/flow/flow_dock.py), add:
   ```python
   from .nodes.llm_nodes      import OpenAINode, OpenAICompatibleNode, AnthropicNode, GeminiNode
   from .nodes.control_nodes  import RegexMatchNode, IfNode, RaceNode, TimerNode
   self.graph.register_node(OpenAINode)
   ...
   self.graph.register_node(RegexMatchNode)
   ...
   ```

5. Wire them up in the UI  
   – In Flow menu or toolbar, add actions or templates to drop multiple provider nodes at once.  
   – Provide a “Add Node…” palette (NodeGraphQt already has this) so users can drag & drop.

6. Future-proofing & extensibility  
   •  Keep all your nodes in a single directory and register them by introspection:
   ```python
   import pkgutil, inspect
   from .nodes import llm_nodes, control_nodes
   for mod in (llm_nodes, control_nodes):
     for _, name, _ in pkgutil.iter_modules(mod.__path__):
       m = __import__(f"aicodeprep_gui.pro.flow.nodes.{name}",fromlist=[name])
       for _, cls in inspect.getmembers(m, inspect.isclass):
         if issubclass(cls, BaseExecNode) and cls is not BaseExecNode:
           self.graph.register_node(cls)
   ```
   •  Use NodePropWidgetEnum to pick the most appropriate editor: QSLIDER for top_p/temperature, QSPINBOX for timeout.  
   •  Optionally expose an entry-point group (in setup.py) so third-party plugins can contribute nodes without touching your code.

7. Example flow for “try first, then fallback”:  
   – ContextOutput → OpenAI Node → RegexMatchNode (checks empty/timeout?) → IfNode →  
     • true → use OpenAI output  
     • false → Anthropic Node → …  

By following these patterns, anyone can drop new files under pro/flow/nodes/, subclass BaseExecNode, define inputs/outputs and properties, and they’ll automatically show up in the Flow Studio palette—keeping your platform modular, maintainable, and ready for future nodes.