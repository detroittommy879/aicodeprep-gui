# Flow Graph Properties Panel Implementation - Session Summary

## Date: October 5, 2025

## Original Goal

Make the Flow Studio feature production-ready with:

1. **Editable node properties** - Users should be able to click nodes and edit their settings
2. **Visual execution feedback** - Show which nodes are running/completed
3. **Parallel LLM execution** - Run multiple LLM nodes simultaneously instead of sequentially
4. **Working properties panel** - Display and allow editing of node properties like file paths, API keys, prompts, etc.

---

## What We Accomplished

### ✅ Phase 1: Visual Execution States & Parallel Execution

- Implemented color-coded node states (gray→orange→green/red) during execution
- Added parallel execution for independent LLM nodes using ThreadPoolExecutor
- Created FlowProgressDialog showing real-time node execution status

### ✅ Phase 2: Properties Panel Integration

- **Discovered** that `PropertiesBinWidget` must be instantiated separately, not retrieved from graph
- **Fixed** the import: `from NodeGraphQt import NodeGraph, PropertiesBinWidget`
- **Created** properties panel: `self.properties_bin = PropertiesBinWidget(node_graph=self.graph)`
- **Connected** single-click handler so properties show on click (not just double-click)

### ✅ Phase 3: Widget Type Enum Fix

- **Discovered** our nodes were using string widget types (`"text"`, `"list"`, `"text_multi"`)
- **Fixed** to use numeric enum values from `NodePropWidgetEnum`:
  - `"text"` → `NodePropWidgetEnum.QLINE_EDIT.value` (3)
  - `"text_multi"` → `NodePropWidgetEnum.QTEXT_EDIT.value` (4)
  - `"list"` → `NodePropWidgetEnum.QCOMBO_BOX.value` (5)
  - `"file_save"` → `NodePropWidgetEnum.FILE_SAVE.value` (14)

---

## Current Issues

### ⚠️ Issue 1: Default Flow Graph is Broken

**Symptom:** Built-in flow now shows only 2 unconnected boxes instead of the full graph

**Likely Cause:**

- The flow loading/serialization may have been corrupted
- Session file `.aicodeprep-flow.json` might be malformed
- Error in console: `[Flow Serializer] load_session failed: the JSON object must be str, bytes or bytearray, not dict`

**Files to Check:**

- `aicodeprep_gui/pro/flow/flow_dock.py` - Lines ~1200-1300 for `_load_default_flow_or_build()`
- `.aicodeprep-flow.json` - Session save file
- `aicodeprep_gui/pro/flow/serializer.py` - Flow save/load logic

### ⚠️ Issue 2: Properties Panel Shows Unwanted Properties

**Symptom:** Panel shows "lots of stuff" including colors, but relevant properties (text, system) are not editable

**Likely Causes:**

1. **Built-in properties showing**: NodeGraphQt automatically shows node built-in properties (color, border_color, text_color, disabled, id) in a "Node" tab
2. **Custom properties may be in wrong tab** or not showing properly
3. **Widget types might still be wrong** for some properties

**What Should Show (by node type):**

**ContextOutputNode:**

- `path` - text input for file path
- `use_latest_generated` - checkbox

**LLM Nodes (OpenRouter, OpenAI, etc.):**

- `provider` - dropdown (openai/openrouter/gemini/generic)
- `model_mode` - dropdown (choose/random/random_free)
- `model` - text input
- `api_key` - text input (sensitive!)
- `base_url` - text input

**BestOfNNode:**

- Same as LLM nodes PLUS:
- `extra_prompt` - multiline text area for synthesis instructions

**FileWriteNode:**

- `path` - file save browser

---

## Technical Context

### NodeGraphQt Properties System

- Properties are created with `node.create_property(name, value, widget_type=...)`
- `widget_type` MUST be a numeric value from `NodePropWidgetEnum`
- Properties appear in `PropertiesBinWidget` organized by tabs
- Default tab is "Properties", also "Ports" and "Node" tabs auto-created

### Current Code Structure

```
aicodeprep_gui/pro/flow/
├── flow_dock.py          # Main dock widget, properties panel integration
├── engine.py             # Flow execution with parallel processing
├── serializer.py         # Flow save/load (JSON)
├── progress_dialog.py    # Execution progress window
└── nodes/
    ├── base.py           # BaseExecNode with run() method
    ├── io_nodes.py       # ContextOutputNode, FileWriteNode, ClipboardNode
    ├── llm_nodes.py      # LLMBaseNode, OpenRouterNode, OpenAINode, etc.
    └── aggregate_nodes.py # BestOfNNode
```

### Properties Implementation in Nodes

Each node defines properties in `__init__()`:

```python
from NodeGraphQt.constants import NodePropWidgetEnum

self.create_property(
    "model",
    "",  # default value
    widget_type=NodePropWidgetEnum.QLINE_EDIT.value,  # Must use .value!
    tab="Properties"  # Optional tab name
)
```

---

## Next Steps to Fix Current Issues

### 1. Fix Broken Flow Graph

**Check serialization:**

```python
# In flow_dock.py, _load_default_flow_or_build()
# The error suggests we're passing a dict instead of a JSON string
```

**Look for:**

- Is `load_session()` being called with wrong parameter type?
- Is the JSON file corrupted?
- Should we rebuild the default flow from scratch?

### 2. Clean Up Properties Display

**Options:**

**A) Hide built-in properties** - Use `widget_type=NodePropWidgetEnum.HIDDEN.value` for properties we don't want shown

**B) Organize into tabs** - Pass `tab="Settings"` parameter to group related properties

**C) Check property definitions** - Verify all our custom properties have correct widget types

**Specific checks needed:**

```python
# In io_nodes.py, llm_nodes.py, aggregate_nodes.py
# Look for any properties missing widget_type parameter
# Look for properties that should be hidden
```

### 3. Debug "text" and "system" Properties

**These sound like input ports, not properties!**

Ports (node inputs/outputs) are NOT editable in the properties panel - they're the connection points.

**Verify:**

- Are we confusing ports with properties?
- Should these be actual editable properties instead of ports?
- Check if LLM nodes have a "system prompt" property that should be editable

---

## Key Files Reference

### Properties Panel Integration

**File:** `aicodeprep_gui/pro/flow/flow_dock.py`
**Lines:** ~400-450

```python
# Create PropertiesBinWidget
self.properties_bin = PropertiesBinWidget(node_graph=self.graph)

# Connect single-click handler
if hasattr(self.graph, 'node_selected'):
    self.graph.node_selected.connect(
        lambda node: self.properties_bin.add_node(node))
```

### Widget Type Definitions

**Files:**

- `aicodeprep_gui/pro/flow/nodes/io_nodes.py`
- `aicodeprep_gui/pro/flow/nodes/llm_nodes.py`
- `aicodeprep_gui/pro/flow/nodes/aggregate_nodes.py`

**Pattern:**

```python
from NodeGraphQt.constants import NodePropWidgetEnum

# In __init__():
self.create_property("name", "default",
    widget_type=NodePropWidgetEnum.QLINE_EDIT.value)
```

### Default Flow Creation

**File:** `aicodeprep_gui/pro/flow/flow_dock.py`
**Method:** `_load_default_flow_or_build()`
**Lines:** ~1200-1300

This builds the default 5-LLM → BestOfN → Output graph

---

## Questions for Next Session

1. **What's the actual error in console?** - Look for flow serialization errors
2. **What properties are showing?** - List exactly what's in the properties panel
3. **Which node type is clicked?** - Different nodes have different properties
4. **Are tabs visible?** - Properties should be organized into tabs (Properties, Ports, Node)
5. **Can you screenshot?** - Visual would help identify the issue

---

## Documentation Created This Session

1. **PROPERTIES_PANEL_DEBUG_2025-01-27.md** - Initial debugging with polling fallback
2. **PROPERTIES_PANEL_FIX_2025-10-05.md** - PropertiesBinWidget instantiation fix
3. **WIDGET_TYPE_FIX_2025-10-05.md** - Enum value fix for widget types
4. **FLOW_IMPROVEMENTS_2025-01-27.md** - Overall flow enhancements
5. **MCP_FLOW_SERVER_PLAN.md** - Future MCP server architecture

---

## Important Discoveries

1. **PropertiesBinWidget is not an attribute** - Must be instantiated with `PropertiesBinWidget(node_graph=graph)`
2. **Widget types must be numeric** - String names like `"text"` don't work, must use `NodePropWidgetEnum.QLINE_EDIT.value`
3. **Properties vs Ports** - Ports are connections, properties are settings. Don't confuse them!
4. **Built-in properties** - Every node has color, border_color, text_color, disabled, id properties by default
5. **Signal connections** - PropertiesBinWidget auto-connects to `node_double_clicked`, we added `node_selected` for single-click

---

## Testing Checklist

When properties panel is working:

- [ ] Click ContextOutput → see path, use_latest_generated
- [ ] Click OpenRouter LLM → see provider, model, api_key, model_mode dropdowns
- [ ] Click BestOfN → see extra_prompt multiline text
- [ ] Click FileWrite → see path with file browser button
- [ ] Edit text field → value persists
- [ ] Select dropdown → value changes
- [ ] Click file browser → dialog opens
- [ ] Run flow → edited properties are used in execution

---

## Console Logs to Check

Look for these in the terminal output:

```
✅ PropertiesBinWidget created successfully
✅ Connected node_selected to show properties on single click
✅ Properties panel added to layout
```

And watch for errors like:

```
[Flow Serializer] load_session failed: the JSON object must be str, bytes or bytearray, not dict
AttributeError: 'NoneType' object has no attribute 'set_name'
```

---

## Quick Diagnostic Commands

```powershell
# Check NodeGraphQt version
python -c "import NodeGraphQt; print(NodeGraphQt.__version__)"

# Check available widget types
python -c "from NodeGraphQt.constants import NodePropWidgetEnum; print([e.name for e in NodePropWidgetEnum])"

# Verify imports work
python -c "from NodeGraphQt import NodeGraph, PropertiesBinWidget; print('OK')"
```

---

## Summary for AI Agent

**We're implementing an editable properties panel for a node-based flow graph UI.** The panel should display node-specific settings (file paths, API keys, model selections, prompts) in a sidebar when users click on nodes.

**Progress:** Panel now appears and attempts to show properties, but:

1. Default flow graph is broken (only 2 unconnected boxes)
2. Properties panel shows wrong/too many properties (colors instead of settings)

**Root issue likely:** Either the flow serialization is corrupted OR our property definitions still have issues with visibility/organization.

**Need to investigate:**

1. Why default flow isn't loading correctly
2. Why built-in properties (colors) are prominent but custom properties (model, api_key) aren't usable
3. Whether we need to hide certain properties or reorganize into tabs
