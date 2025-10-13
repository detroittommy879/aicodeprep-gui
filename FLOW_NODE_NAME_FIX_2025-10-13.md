# Flow Studio: Node Name Fix - Oct 13, 2025

## Problem

When clicking "➕ Add Node" → "OpenAI (Official)", got error:

```
ERROR - Failed to create node aicp.flow.OpenAI Node: Can't find node: "aicp.flow.OpenAI Node"
```

**Root Cause:** The node identifiers in the menu didn't match the actual `NODE_NAME` values defined in the node classes.

## Solution

Fixed all node identifiers in the "Add Node" menu to match the exact `NODE_NAME` class attributes.

## Corrections Made

### LLM Provider Nodes

| Menu Display      | Wrong Identifier                   | ✅ Correct Identifier             |
| ----------------- | ---------------------------------- | --------------------------------- |
| OpenAI (Official) | `aicp.flow.OpenAI Node`            | `aicp.flow.OpenAI LLM`            |
| OpenRouter        | `aicp.flow.OpenRouter Node`        | `aicp.flow.OpenRouter LLM`        |
| Gemini (Google)   | `aicp.flow.Gemini Node`            | `aicp.flow.Gemini LLM`            |
| OpenAI Compatible | `aicp.flow.OpenAI Compatible Node` | `aicp.flow.OpenAI-Compatible LLM` |

### I/O Nodes

| Menu Display   | Wrong Identifier              | ✅ Correct Identifier |
| -------------- | ----------------------------- | --------------------- |
| Context Output | ✅ `aicp.flow.Context Output` | ✅ (already correct)  |
| File Write     | ✅ `aicp.flow.File Write`     | ✅ (already correct)  |
| Clipboard      | `aicp.flow.Clipboard Node`    | `aicp.flow.Clipboard` |
| Output Display | ✅ `aicp.flow.Output Display` | ✅ (already correct)  |

### Utility Nodes

| Menu Display | Wrong Identifier           | ✅ Correct Identifier             |
| ------------ | -------------------------- | --------------------------------- |
| Best of N    | `aicp.flow.Best of N Node` | `aicp.flow.Best-of-N Synthesizer` |

## Technical Details

### Node Identifier Format

NodeGraphQt uses: `<__identifier__>.<NODE_NAME>`

Example from `llm_nodes.py`:

```python
class OpenAINode(LLMBaseNode):
    __identifier__ = "aicp.flow"
    NODE_NAME = "OpenAI LLM"  # ← This must match exactly!
```

Full identifier: `aicp.flow.OpenAI LLM`

### Why This Matters

When you call `graph.create_node('aicp.flow.OpenAI LLM')`, NodeGraphQt:

1. Splits by `.` → `['aicp', 'flow', 'OpenAI LLM']`
2. Looks for registered node with `__identifier__ = "aicp.flow"` and `NODE_NAME = "OpenAI LLM"`
3. If no match found → Error: "Can't find node"

**Case sensitive!** `"OpenAI Node"` ≠ `"OpenAI LLM"`

## Files Modified

1. **aicodeprep_gui/pro/flow/flow_dock.py**
   - Fixed `_create_toolbar()` method (toolbar menu)
   - Fixed `_setup_node_creation_menu()` method (Tab key menu)
   - Both now use correct NODE_NAME values

## Testing

Restart the app and try:

1. Click **"➕ Add Node" → 🤖 LLM Providers → OpenAI (Official)**

   - Should create node successfully
   - Node appears at center of viewport
   - Node is selected (properties panel shows)
   - No error message

2. Try each node type to verify all work:
   - ✅ OpenAI (Official) → `OpenAI LLM` node
   - ✅ OpenRouter → `OpenRouter LLM` node
   - ✅ Gemini (Google) → `Gemini LLM` node
   - ✅ OpenAI Compatible → `OpenAI-Compatible LLM` node
   - ✅ Context Output → `Context Output` node
   - ✅ File Write → `File Write` node
   - ✅ Clipboard → `Clipboard` node
   - ✅ Output Display → `Output Display` node
   - ✅ Best of N → `Best-of-N Synthesizer` node

## Verification Checklist

After restart, verify each node type:

- [ ] OpenAI (Official) creates without error
- [ ] OpenRouter creates without error
- [ ] Gemini (Google) creates without error
- [ ] OpenAI Compatible creates without error
- [ ] Context Output creates without error
- [ ] File Write creates without error
- [ ] Clipboard creates without error
- [ ] Output Display creates without error
- [ ] Best of N creates without error

## How to Find Correct Node Names

If adding new node types in the future:

1. **Open the node class file** (e.g., `llm_nodes.py`)
2. **Find the class definition**:
   ```python
   class MyNewNode(BaseNode):
       __identifier__ = "aicp.flow"
       NODE_NAME = "My New Node Name"  # ← Use this exactly!
   ```
3. **Use in menu**: `aicp.flow.My New Node Name`

### Quick Command

Search all node names:

```bash
grep -r "NODE_NAME = " aicodeprep_gui/pro/flow/nodes/
```

Output shows all available node names:

```
llm_nodes.py:    NODE_NAME = "OpenRouter LLM"
llm_nodes.py:    NODE_NAME = "OpenAI LLM"
llm_nodes.py:    NODE_NAME = "Gemini LLM"
llm_nodes.py:    NODE_NAME = "OpenAI-Compatible LLM"
io_nodes.py:     NODE_NAME = "Context Output"
io_nodes.py:     NODE_NAME = "Clipboard"
io_nodes.py:     NODE_NAME = "File Write"
io_nodes.py:     NODE_NAME = "Output Display"
aggregate_nodes.py: NODE_NAME = "Best-of-N Synthesizer"
```

## Common Mistakes to Avoid

❌ **Don't guess the node name** - always check the class definition  
❌ **Don't use display names** - use exact NODE_NAME value  
❌ **Don't add extra spaces** - `"OpenAI LLM"` not `"OpenAI  LLM"`  
❌ **Don't change capitalization** - `"OpenAI LLM"` not `"openai llm"`  
❌ **Don't forget hyphens** - `"OpenAI-Compatible LLM"` has hyphen

✅ **Always copy-paste** NODE_NAME from source code  
✅ **Test after adding** new node types to menu  
✅ **Check console logs** if creation fails - shows attempted identifier
