# Flow Studio: Node Labels & Creation Menu - Oct 12, 2025

## Changes Made

### 1. Fixed Node Label Display

**Problem:** Node labels weren't showing model names, file paths, or settings. Previous attempt used non-existent `add_label()` method.

**Solution:** Use compact single-line format in node name via `set_name()`:

#### LLM Nodes (OpenAI, OpenRouter, Gemini, OpenAI Compatible)

- Format: `NodeName: model-name (T0.8,P0.9)`
- Shows short model name (last part after `/`)
- Displays non-default temperature (T) and top_p (P) values
- Example: `OpenAI Node: gpt-4-turbo (T0.8)`
- Example: `OpenRouter Node: [random]`

#### I/O Nodes

- **Context Output**: `Context Output: fullcode.txt`
- **File Write**: `File Write: output.txt`
- Truncates long paths with `...` prefix

#### How It Works

- `_update_node_label()` method builds compact display string
- Called on node init (via `QTimer.singleShot`) and property changes
- Uses `BaseNode.get_property()` directly to avoid recursion
- Updates via `set_name()` which is NodeGraphQt's standard API

### 2. Added Node Creation Menu

**Problem:** No way to add nodes - users couldn't build flows!

**Solution:** Added Tab key / right-click context menu for creating nodes.

#### Menu Structure

```
LLM Providers:
  - OpenAI (Official)
  - OpenRouter
  - Gemini (Google)
  - OpenAI Compatible

Input/Output:
  - Context Output
  - File Write
  - Clipboard
  - Output Display

Utilities:
  - Best of N
```

#### How to Use

1. **Tab Key**: Press Tab anywhere in the graph canvas to open node creation menu
2. **Right Click**: Right-click on canvas and select "Create Node"
3. Navigate through categories to select node type
4. Node appears at cursor position

#### Implementation

- `_setup_node_creation_menu()` method called during init
- Uses NodeGraphQt's `set_context_menu()` API
- Menu structure maps display names to node identifiers (`aicp.flow.NodeName`)
- Nodes must be registered via `register_node()` before they appear in menu

## Files Modified

1. **aicodeprep_gui/pro/flow/nodes/llm_nodes.py**

   - Simplified `_update_node_label()` to use single-line format
   - Removed non-existent `add_label()` calls

2. **aicodeprep_gui/pro/flow/nodes/io_nodes.py**

   - Updated `_update_node_label()` for Context Output and File Write nodes
   - Compact file path display in node name

3. **aicodeprep_gui/pro/flow/flow_dock.py**
   - Added `_setup_node_creation_menu()` method
   - Called during `__init__` after node registration
   - Configures Tab key menu with all available node types

## Testing

1. **Launch the app**: `python -m aicodeprep_gui.main --pro`
2. **Open Flow Studio** dock
3. **Test node creation**:
   - Press Tab key → should show node menu
   - Select "LLM Providers" → "OpenAI (Official)"
   - Node should appear with name "OpenAI Node"
4. **Test label updates**:
   - Select node and view properties panel
   - Change model to "gpt-4-turbo"
   - Node name should update to "OpenAI Node: gpt-4-turbo"
   - Change temperature to 0.8
   - Node name should update to "OpenAI Node: gpt-4-turbo (T0.8)"
5. **Test file nodes**:
   - Create Context Output node
   - Should show "Context Output: fullcode.txt"
   - Change path in properties
   - Node name should update accordingly

## Node Types Available

### LLM Provider Nodes

All support:

- Model selection (manual or random mode)
- Temperature control (default 0.7)
- Top-P control (default 1.0)
- API key configuration
- Base URL override (for compatible endpoints)

1. **OpenAI Node**: Official OpenAI API (GPT-4, GPT-3.5, etc.)
2. **OpenRouter Node**: OpenRouter.ai aggregator service
3. **Gemini Node**: Google Gemini API
4. **OpenAI Compatible Node**: Any OpenAI-compatible endpoint

### I/O Nodes

1. **Context Output**: Writes to context file (default: fullcode.txt)
2. **File Write**: Writes to custom file path
3. **Clipboard Node**: Copies output to system clipboard
4. **Output Display**: Shows output in UI popup

### Utility Nodes

1. **Best of N Node**: Runs N parallel LLM calls, picks best result

## Technical Notes

- NodeGraphQt doesn't support multi-line node names
- Single-line format chosen for clarity and compatibility
- Text truncation ensures names fit within node width
- Label updates happen via Qt event loop (QTimer.singleShot)
- Property changes automatically trigger label refresh
- Menu config uses NodeGraphQt's native context menu system

## Next Steps

Potential improvements:

1. Add more node types (prompt templates, string manipulation, etc.)
2. Custom node colors by category
3. Node icons/badges for visual identification
4. Tooltip showing full model name and all settings
5. Quick actions in right-click menu (duplicate, delete, etc.)
