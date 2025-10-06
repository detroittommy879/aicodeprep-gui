# Widget Type Fix - October 5, 2025

## Problem

Properties panel was displaying but crashed with `AttributeError: 'NoneType' object has no attribute 'set_name'` when clicking nodes.

## Root Cause

Our node properties were using **string widget type names** like `"text"`, `"list"`, `"text_multi"`, but NodeGraphQt expects **numeric enum values** from `NodePropWidgetEnum`.

When NodeGraphQt's property widget factory tried to create widgets for our properties, it returned `None` for unrecognized widget types, causing the crash.

## Solution

Updated all node property declarations to use the correct `NodePropWidgetEnum` values:

### Widget Type Mapping

| Old String Value | Correct Enum                    | Value |
| ---------------- | ------------------------------- | ----- |
| `"text"`         | `NodePropWidgetEnum.QLINE_EDIT` | 3     |
| `"text_multi"`   | `NodePropWidgetEnum.QTEXT_EDIT` | 4     |
| `"list"`         | `NodePropWidgetEnum.QCOMBO_BOX` | 5     |
| `"file_save"`    | `NodePropWidgetEnum.FILE_SAVE`  | 14    |

### Files Modified

**io_nodes.py:**

- Added `NodePropWidgetEnum` import
- Changed `widget_type="file_save"` → `widget_type=NodePropWidgetEnum.FILE_SAVE.value`

**llm_nodes.py:**

- Added `NodePropWidgetEnum` import
- Changed `widget_type="text"` → `widget_type=NodePropWidgetEnum.QLINE_EDIT.value`
- Changed `widget_type="list"` → `widget_type=NodePropWidgetEnum.QCOMBO_BOX.value`

**aggregate_nodes.py:**

- Added `NodePropWidgetEnum` import
- Changed `widget_type="text"` → `widget_type=NodePropWidgetEnum.QLINE_EDIT.value`
- Changed `widget_type="list"` → `widget_type=NodePropWidgetEnum.QCOMBO_BOX.value`
- Changed `widget_type="text_multi"` → `widget_type=NodePropWidgetEnum.QTEXT_EDIT.value`

## Code Changes Example

### Before (Incorrect)

```python
self.create_property("model", "", widget_type="text")
self.create_property("model_mode", "choose", widget_type="list",
                     items=["choose", "random", "random_free"])
self.create_property("extra_prompt", DEFAULT_PROMPT, widget_type="text_multi")
```

### After (Correct)

```python
from NodeGraphQt.constants import NodePropWidgetEnum

self.create_property("model", "", widget_type=NodePropWidgetEnum.QLINE_EDIT.value)
self.create_property("model_mode", "choose", widget_type=NodePropWidgetEnum.QCOMBO_BOX.value,
                     items=["choose", "random", "random_free"])
self.create_property("extra_prompt", DEFAULT_PROMPT, widget_type=NodePropWidgetEnum.QTEXT_EDIT.value)
```

## Import Guard Pattern

Added safe import with fallback stub for environments without NodeGraphQt:

```python
try:
    from NodeGraphQt.constants import NodePropWidgetEnum
except ImportError:
    class NodePropWidgetEnum:
        QLINE_EDIT = 3
        QTEXT_EDIT = 4
        QCOMBO_BOX = 5
        FILE_SAVE = 14
```

## Available Widget Types

Complete list from `NodePropWidgetEnum`:

```python
HIDDEN = 0           # Property hidden from properties panel
QLABEL = 2           # Read-only label
QLINE_EDIT = 3       # Single-line text input
QTEXT_EDIT = 4       # Multi-line text input
QCOMBO_BOX = 5       # Dropdown selection
QCHECK_BOX = 6       # Boolean checkbox
QSPIN_BOX = 7        # Integer spinner
QDOUBLESPIN_BOX = 8  # Float spinner
COLOR_PICKER = 9     # RGB color picker
COLOR4_PICKER = 10   # RGBA color picker
SLIDER = 11          # Integer slider
DOUBLE_SLIDER = 12   # Float slider
FILE_OPEN = 13       # File open dialog button
FILE_SAVE = 14       # File save dialog button
VECTOR2 = 15         # Two-component vector (x, y)
VECTOR3 = 16         # Three-component vector (x, y, z)
VECTOR4 = 17         # Four-component vector (r, g, b, a)
FLOAT = 18           # Float value edit
INT = 19             # Integer value edit
BUTTON = 20          # Custom button widget
```

## Expected Behavior After Fix

### Properties Panel Should Display:

✅ **ContextOutputNode:**

- `path` (text input)
- `use_latest_generated` (checkbox)

✅ **LLM Nodes (OpenRouter, OpenAI, Gemini, Compatible):**

- `provider` (dropdown)
- `model_mode` (dropdown: choose/random/random_free)
- `model` (text input)
- `api_key` (text input)
- `base_url` (text input)

✅ **BestOfNNode:**

- `provider` (dropdown)
- `model_mode` (dropdown)
- `model` (text input)
- `api_key` (text input)
- `base_url` (text input)
- `extra_prompt` (multiline text area)

✅ **FileWriteNode:**

- `path` (file save dialog)

### Interaction Tests:

1. Click any node → properties appear without error
2. Edit text field → value updates
3. Select dropdown → value changes
4. Click file browser → file dialog opens
5. Edit multiline text → scrollable text area

## Testing Instructions

1. **Restart application**

   ```powershell
   python -m aicodeprep_gui.main
   ```

2. **Open Flow Studio** (Tools → Flow Studio)

3. **Click on each node type:**

   - Context Output
   - OpenRouter LLM nodes
   - Best-of-N Synthesizer
   - File Write
   - Clipboard

4. **Verify properties display** in right panel

5. **Test editing:**

   - Change text fields
   - Select dropdown values
   - Edit multiline prompt
   - Browse for file path

6. **Run the flow** to verify edited properties are used

## Error Resolution

### Previous Error:

```
AttributeError: 'NoneType' object has no attribute 'set_name'
  File "node_property_widgets.py", line 436, in _read_node
    widget.set_name(prop_name)
```

### Cause:

```python
widget = widget_factory.get_widget(wid_type)  # Returns None for unknown types
widget.set_name(prop_name)  # Crashes because widget is None
```

### Fix:

Using correct enum values ensures `get_widget()` returns proper widget instances.

## Related Files

- **PROPERTIES_PANEL_FIX_2025-10-05.md**: Initial properties panel implementation
- **FLOW_PROPERTIES_GUIDE.md**: User guide for property editing
- **NodeGraphQt constants.py**: Widget type enum definitions

## NodeGraphQt Documentation References

- Widget types: `NodeGraphQt.constants.NodePropWidgetEnum`
- Property creation: `NodeObject.create_property()`
- Properties panel: `PropertiesBinWidget`
- Property widgets: `NodeGraphQt.custom_widgets.properties_bin.*`

## Lessons Learned

1. **Always check enum values** when working with library constants
2. **Use MCP/GitHub search** to find actual implementation examples
3. **Inspect widget_factory** to understand what widget types are supported
4. **Add fallback stubs** for optional imports to avoid breaking non-flow environments
5. **Test with actual data** - the properties panel only reveals issues when nodes are clicked

## Next Steps

✅ Test all node types display properties correctly
✅ Verify property editing persists values
✅ Test file browser dialog
✅ Verify multiline text editing
✅ Test dropdown selections
✅ Run flow to confirm edited properties affect execution
