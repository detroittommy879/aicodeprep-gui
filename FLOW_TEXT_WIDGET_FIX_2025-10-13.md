# Flow Studio: Node Info Display Fix - Oct 13, 2025

## Problem

Node labels were displaying as a single long line that ran off the edge of the node boxes. The text content was correct (model names, file paths, settings) but the formatting made it unreadable.

**Root Cause:** NodeGraphQt's `set_name()` method only supports single-line node titles, and node title area is narrow/fixed height.

## Solution

Added **internal text widgets** inside each node body to display the information properly, instead of trying to cram everything into the node title.

### Implementation

#### 1. LLM Nodes (OpenAI, OpenRouter, Gemini, OpenAI Compatible)

**Added:**

- Read-only `QLineEdit` widget named `_info_display` inside node body
- Styled as transparent/borderless so it blends in naturally
- Displays: `Model: gpt-4-turbo | Temp: 0.8 | TopP: 0.95`

**Node Title (compact):** `OpenAI Node: gpt-4-turbo (T0.8,P0.95)`  
**Info Widget (detailed):** `Model: gpt-4-turbo | Temp: 0.8 | TopP: 0.95`

**Code:**

```python
# In __init__:
self.add_text_input('_info_display', '', multi_line=False, tab=None)
widget = self.get_widget('_info_display')
qt_widget = widget.get_custom_widget()
qt_widget.setReadOnly(True)
qt_widget.setStyleSheet("background: transparent; border: none;")

# In _update_node_label():
info_parts = []
if model:
    info_parts.append(f"Model: {model}")
if temperature != 0.7:
    info_parts.append(f"Temp: {temperature}")
if top_p != 1.0:
    info_parts.append(f"TopP: {top_p}")

info_text = " | ".join(info_parts)
NGBaseNode.set_property(self, '_info_display', info_text, push_undo=False)
```

#### 2. Context Output Node

**Added:**

- Read-only widget named `_file_display`
- Shows file icon and full path: `📄 fullcode.txt`

**Node Title:** `Context Output: fullcode.txt`  
**Info Widget:** `📄 fullcode.txt`

#### 3. File Write Node

**Added:**

- Read-only widget named `_file_display`
- Shows file icon and full path: `📝 output.txt`

**Node Title:** `File Write: output.txt`  
**Info Widget:** `📝 output.txt`

### Why This Works

1. **Text Widgets Have More Space:** Node body area is taller and can accommodate text widgets properly
2. **Read-Only Display:** `setReadOnly(True)` prevents user edits while showing information
3. **Transparent Styling:** Borderless/transparent background makes it look like native node text
4. **Dual Display:** Node title shows compact version, widget shows detailed version
5. **Auto-Updates:** Widget updates automatically when properties change (via `set_property` override)

### Technical Details

- **Widget Creation:** `add_text_input()` creates a `QLineEdit` widget inside the node
- **Widget Access:** `get_widget()` returns NodeGraphQt widget wrapper
- **Qt Widget:** `get_custom_widget()` returns underlying Qt widget for styling
- **Styling:** CSS-like `setStyleSheet()` for transparency and borderless appearance
- **Updates:** `BaseNode.set_property()` used directly to avoid recursion
- **Timing:** `QTimer.singleShot(0, ...)` ensures widgets exist before first update

### Property Update Flow

```
User changes property → set_property() override triggered
                      ↓
                _update_node_label() called
                      ↓
            ┌─────────┴─────────┐
            ↓                   ↓
     set_name(compact)    set_property('_info_display', detailed)
            ↓                   ↓
     Node title updates    Widget text updates
```

## Files Modified

1. **aicodeprep_gui/pro/flow/nodes/llm_nodes.py**

   - Added `_info_display` widget in `__init__`
   - Updated `_update_node_label()` to populate widget
   - Widget shows: Model + Temperature + Top-P

2. **aicodeprep_gui/pro/flow/nodes/io_nodes.py**
   - Added `_file_display` widgets to Context Output and File Write nodes
   - Widgets show file icon + full file path
   - Gray color (#888) for subtle appearance

## Testing

Launch the app and verify:

1. **Create LLM Node** (Tab → LLM Providers → OpenAI)

   - Should see node title: `OpenAI Node`
   - Should see widget inside node body (initially empty)

2. **Set Model** in properties panel:

   - Change model to `gpt-4-turbo`
   - Node title should update to: `OpenAI Node: gpt-4-turbo`
   - Widget should show: `Model: gpt-4-turbo`

3. **Set Temperature** to 0.8:

   - Node title: `OpenAI Node: gpt-4-turbo (T0.8)`
   - Widget: `Model: gpt-4-turbo | Temp: 0.8`

4. **Create Context Output Node**:

   - Node title: `Context Output: fullcode.txt`
   - Widget: `📄 fullcode.txt`
   - Change path property → both should update

5. **Create File Write Node**:
   - Node title: `File Write: output.txt`
   - Widget: `📝 output.txt`

## Visual Layout

```
┌─────────────────────────────┐
│  OpenAI Node: gpt-4-turbo   │ ← Node Title (compact)
├─────────────────────────────┤
│ ⚫ text                      │
│ ⚫ system                    │
│                             │
│ Model: gpt-4-turbo |...     │ ← Info Widget (detailed)
│                             │
│ ⚪ text                      │
└─────────────────────────────┘
```

## Benefits

✅ **Readable:** Text properly contained within node boundaries  
✅ **Informative:** Shows full details without truncation  
✅ **Clean:** Transparent styling blends with node design  
✅ **Automatic:** Updates when properties change  
✅ **Dual Display:** Compact title + detailed widget  
✅ **Non-Intrusive:** Read-only prevents accidental edits

## Alternative Approaches Tried

❌ **Multi-line node names** - NodeGraphQt doesn't support `\n` in names  
❌ **HTML in names** - Not rendered, shows as plain text  
❌ **Custom painting** - Too complex, requires view class modification  
❌ **add_label()** - Method doesn't exist in NodeGraphQt  
✅ **Text input widgets** - Works perfectly! (current solution)

## Next Steps

If widgets don't appear or text is still clipped:

1. Check if NodeGraphQt version supports `add_text_input`
2. Verify widgets are created (check `get_widgets()` output)
3. Increase node height in NodeGraphQt settings if needed
4. Try `multi_line=True` for longer text
5. Check console logs for widget creation errors
