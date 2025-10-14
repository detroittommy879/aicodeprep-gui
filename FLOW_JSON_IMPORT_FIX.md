# Flow JSON Import Fix

## Date: October 14, 2025

## Issue

When loading the preconfigured Best-of-5 flow template, users received an error:

```
TypeError: the JSON object must be str, bytes or bytearray, not dict
```

## Root Cause

The `flow.json` file contained node properties in a format where:

- `custom` fields were stored as **dict/list objects**
- `subgraph_session` fields were stored as **dict/list objects**

However, NodeGraphQt's `load_session()` method expects these fields to be **JSON-encoded strings**, not raw Python objects. When NodeGraphQt tried to parse them with `json.loads()`, it failed because they were already parsed dictionaries.

## Solution

Added a normalization function `_normalize_node_data()` in `serializer.py` that:

1. **Detects dict/list fields** in `custom` and `subgraph_session`
2. **Converts them to JSON strings** using `json.dumps()`
3. **Creates a temporary normalized file** for NodeGraphQt to load
4. **Cleans up the temp file** after successful load

### Code Changes

#### File: `aicodeprep_gui/pro/flow/serializer.py`

**Added function:**

```python
def _normalize_node_data(data: dict) -> dict:
    """
    Normalize node data to ensure 'custom' and 'subgraph_session' fields are JSON strings.
    NodeGraphQt expects these to be JSON-encoded strings, not raw dicts/lists.
    """
    if "nodes" in data and isinstance(data["nodes"], dict):
        for node_id, node_data in data["nodes"].items():
            if isinstance(node_data, dict):
                # Convert 'custom' field to JSON string if it's a dict
                if "custom" in node_data and isinstance(node_data["custom"], (dict, list)):
                    node_data["custom"] = json.dumps(node_data["custom"])

                # Convert 'subgraph_session' field to JSON string if it's a dict
                if "subgraph_session" in node_data and isinstance(node_data["subgraph_session"], (dict, list)):
                    node_data["subgraph_session"] = json.dumps(node_data["subgraph_session"])

    return data
```

**Modified `load_session()` function:**

- Calls `_normalize_node_data()` after loading JSON
- Writes normalized data to a temp file
- Loads from the temp file
- Cleans up temp file after loading (or on error)

### Process Flow

#### Before Fix:

```
flow.json (dict objects)
  → NodeGraphQt.load_session()
  → json.loads(dict)
  → TypeError ❌
```

#### After Fix:

```
flow.json (dict objects)
  → Load as Python dict
  → _normalize_node_data() converts dicts to JSON strings
  → Write to temp file (JSON strings)
  → NodeGraphQt.load_session()
  → json.loads(string)
  → Success ✅
  → Cleanup temp file
```

## Technical Details

### Why This Happens

NodeGraphQt internally stores node properties in JSON format and uses `json.loads()` to deserialize them. When exporting, it properly converts everything to JSON strings. However, hand-crafted or externally generated flow.json files may have dict/list objects that haven't been stringified.

### Compatibility

This fix maintains compatibility with:

- ✅ Hand-crafted flow.json files (like our template)
- ✅ NodeGraphQt-exported files (already have JSON strings)
- ✅ Mixed formats (some strings, some objects)
- ✅ All Python versions (3.8+)

### Performance Impact

- Minimal: Only adds one extra pass through the nodes dict
- Temp file is small and cleaned up immediately
- No impact on normal operation

## Testing

### Test Cases

1. ✅ Load preconfigured Best-of-5 template
2. ✅ Load manually imported flow.json
3. ✅ Export and re-import flow
4. ✅ Error handling (cleanup on failure)

### Expected Behavior

- Template now loads successfully
- No more TypeError
- All nodes appear correctly
- Properties are preserved
- No temp files left behind

## User Impact

### Before:

- ❌ "Load Built-in: Best-of-5 (Configured)" failed
- Had to manually import the file
- Confusing error message

### After:

- ✅ Template loads instantly
- ✅ No user intervention needed
- ✅ Clear success message
- ✅ Ready to use immediately

## Related Issues

This also fixes any other flow.json files that have similar format issues, making the import more robust and forgiving of format variations.

## Future Improvements

Could add:

- Format validation before import
- Automatic format conversion on export
- Warning if format appears non-standard
- Schema validation for flow.json files
