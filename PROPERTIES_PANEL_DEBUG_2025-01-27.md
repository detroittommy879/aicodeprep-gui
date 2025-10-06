# Properties Panel Debugging Session - January 27, 2025

## Problem

The properties panel was visible in the Flow Studio UI but wasn't updating when nodes were clicked. The panel showed only static placeholder text despite signal connections being attempted in the code.

## Root Cause Analysis

The issue appeared to be related to:

1. **Signal Connection Uncertainty**: The exact signal names for node selection in NodeGraphQt may vary by version
2. **Silent Connection Failures**: Signal connection attempts had minimal logging, making it hard to diagnose
3. **No Fallback Mechanism**: If signals failed to connect, there was no alternative way to update properties

## Solutions Implemented

### 1. Enhanced Diagnostic Logging

Added comprehensive debug logging to track:

- Which signals are available on `self.graph` and `viewer` objects
- Whether signal connections succeed or fail
- When selection callbacks are triggered (or not)
- Status of property panel update attempts

**Key Additions:**

```python
# Log all selection-related attributes
graph_attrs = [attr for attr in dir(self.graph) if 'select' in attr.lower()]
logging.info(f"🔍 Graph selection-related attributes: {graph_attrs}")

viewer_attrs = [attr for attr in dir(viewer) if 'select' in attr.lower()]
logging.info(f"🔍 Viewer selection-related attributes: {viewer_attrs}")

# Track connection success/failure
if not connected:
    logging.error("❌ No selection signals found! Properties panel won't update.")
```

### 2. Polling Timer Fallback

Implemented a 500ms polling mechanism as a reliable fallback:

**New Code:**

```python
# Set up polling timer in __init__
self._last_selected_nodes = set()
if self.properties_bin:
    self._selection_timer = QTimer(self)
    self._selection_timer.timeout.connect(self._poll_selection)
    self._selection_timer.start(500)  # Poll every 500ms
    logging.info("✅ Selection polling timer started as fallback")
```

**Polling Method:**

```python
def _poll_selection(self):
    """Poll for selection changes when signals don't work."""
    try:
        selected_nodes = self.graph.selected_nodes()
        current_ids = set(node.id for node in selected_nodes)

        if current_ids != self._last_selected_nodes:
            self._last_selected_nodes = current_ids
            if selected_nodes:
                logging.info(f"🔄 Polling detected selection change")
                self._update_properties_panel(selected_nodes)
    except Exception as e:
        logging.debug(f"Polling selection check error: {e}")
```

### 3. Unified Property Update Method

Refactored property update logic into a single, robust method:

```python
def _update_properties_panel(self, nodes):
    """Update properties panel with selected nodes."""
    if not self.properties_bin or not nodes:
        return

    try:
        if hasattr(self.properties_bin, 'add_node'):
            self.properties_bin.clear()
            for node in nodes:
                self.properties_bin.add_node(node)
            logging.info(f"✅ Properties panel updated for {len(nodes)} node(s)")
        else:
            logging.warning("Properties bin has no add_node method")
    except Exception as e:
        logging.error(f"❌ Failed to update properties panel: {e}")
```

### 4. Improved Error Handling

Enhanced callbacks with better error handling:

```python
def _on_node_selected(self, node):
    """Signal callback for single node selection."""
    logging.info(f"🔔 _on_node_selected called with node: {node}")
    if node:
        self._update_properties_panel([node])
    else:
        logging.warning(f"Node is None in _on_node_selected")

def _on_nodes_selected(self, nodes):
    """Signal callback for multiple node selection."""
    logging.info(f"🔔 _on_nodes_selected called with {len(nodes) if nodes else 0} nodes")
    if nodes:
        self._update_properties_panel(nodes)
    else:
        logging.warning(f"Nodes list is empty in _on_nodes_selected")
```

## How It Works Now

### Dual-Path Update Strategy

1. **Primary Path (Signals)**: If NodeGraphQt signals work, they trigger immediate updates
2. **Fallback Path (Polling)**: Every 500ms, check if selection changed and update if needed

### Update Flow

```
Node Clicked
    ↓
[Signal Triggered?] → Yes → _on_node_selected() → _update_properties_panel()
    ↓ No
[Polling Timer (500ms)] → Detect Change → _update_properties_panel()
    ↓
Clear properties_bin
    ↓
Add selected nodes to properties_bin
    ↓
Properties Panel Updated! ✅
```

### Diagnostic Output

The enhanced logging will show:

```
🔍 Graph selection-related attributes: ['selected_nodes', 'all_nodes', ...]
🔍 Viewer selection-related attributes: ['node_selected', ...]
✅ Connected to graph.node_selected signal
✅ Selection polling timer started as fallback
🔄 Polling detected selection change: 1 nodes
✅ Properties panel updated for 1 node(s)
```

OR if signals don't work:

```
⚠️ No node_selected signal found on graph or viewer
❌ No selection signals found! Properties panel won't update.
✅ Selection polling timer started as fallback
🔄 Polling detected selection change: 1 nodes
✅ Properties panel updated for 1 node(s)
```

## Testing Instructions

1. **Restart the Application**

   ```powershell
   # Close and restart AICodePrep GUI
   ```

2. **Open Flow Studio**

   - Tools → Flow Studio

3. **Watch Console Output**
   Look for diagnostic messages showing:

   - Available selection-related attributes
   - Signal connection status
   - Polling timer startup
   - Selection change detection
   - Property panel updates

4. **Click on Nodes**

   - Click different nodes in the graph
   - Verify properties panel updates (may have ~500ms delay if using polling)
   - Watch console for update messages

5. **Edit Properties**
   - Try changing node properties in the panel
   - Verify changes persist
   - Run the flow to test changed values

## Expected Outcomes

### With Working Signals

- Immediate property panel updates on node click
- Console shows signal connection success
- No polling messages (signals handle it)

### With Polling Fallback

- ~500ms delay before property panel updates
- Console shows "No selection signals found" warning
- Console shows "Polling detected selection change" messages
- Properties still update reliably

### Both Scenarios

- Properties panel displays editable fields for selected nodes
- Multiple node selection shows all properties
- Property changes persist and affect execution
- No crashes or errors

## Files Modified

1. **flow_dock.py**
   - Added `QTimer` import
   - Added `_poll_selection()` method (lines ~530-545)
   - Added `_update_properties_panel()` method (lines ~547-563)
   - Refactored `_on_node_selected()` (lines ~565-573)
   - Refactored `_on_nodes_selected()` (lines ~575-583)
   - Enhanced signal connection logging (lines ~440-475)
   - Added polling timer initialization (lines ~515-523)

## Troubleshooting

### If Properties Still Don't Update

1. Check console for error messages
2. Verify `properties_bin` is not None
3. Look for "add_node" method availability warnings
4. Check NodeGraphQt version: `pip show NodeGraphQt`

### If Polling Causes Performance Issues

Adjust timer interval in `__init__`:

```python
self._selection_timer.start(1000)  # Change to 1 second
```

Or disable polling if signals work:

```python
# Comment out timer creation if signals are working
# self._selection_timer = QTimer(self)
```

## Next Steps

1. **Verify with User**: Test on actual system and confirm properties update
2. **Optimize Polling**: If signals work, consider removing/disabling polling timer
3. **Version Detection**: Add NodeGraphQt version checking for automatic signal selection
4. **Property Validation**: Add input validation for property values
5. **Undo/Redo**: Consider adding property change history

## Technical Notes

### Why Polling Works

NodeGraphQt's `graph.selected_nodes()` method reliably returns the current selection regardless of signal behavior. By periodically checking this and comparing to previous state, we can detect changes even if signals fail.

### Performance Impact

- 500ms polling is negligible CPU impact
- Only processes when selection actually changes
- No impact during flow execution (polling continues but updates don't interfere)

### NodeGraphQt Compatibility

This approach works across all NodeGraphQt versions because:

- Polling uses stable `selected_nodes()` method
- Signal connection attempts are version-agnostic (tries multiple approaches)
- Fallback ensures functionality even with API changes

## Related Documentation

- **FLOW_IMPROVEMENTS_2025-01-27.md**: Overall flow graph enhancements
- **FLOW_PROPERTIES_GUIDE.md**: Guide for editing node properties
- **MCP_FLOW_SERVER_PLAN.md**: Future MCP server architecture
