# Flow Studio Pan/Navigation Fix - October 12, 2025

## Issue

The hand button, spacebar, and arrow keys were not working properly to pan/move the flow graph canvas. Users could zoom with the mouse wheel, but couldn't move the canvas around to view different areas.

## Root Cause

NodeGraphQt's `NodeViewer` has its own internal pan handling mechanism (`_set_viewer_pan`) that was not being used. The code was trying to use standard QGraphicsView methods (`setDragMode`) which were being overridden or not properly respected by NodeGraphQt's custom viewer implementation.

Additionally, the viewer was missing critical interactive flags that are required for proper mouse event handling and panning.

## Solution

### 1. Enable Interactive Mode

Added proper initialization in `_configure_viewer()`:

- `setInteractive(True)` - Critical for enabling mouse interactions
- `setTransformationAnchor(AnchorUnderMouse)` - Better pan/zoom behavior
- `setResizeAnchor(AnchorViewCenter)` - Proper resizing behavior

### 2. Use NodeGraphQt's Internal Pan Method

Updated pan toggle methods to prioritize NodeGraphQt's internal `_set_viewer_pan()` method:

- **Hand Button Toggle** (`_toggle_pan_mode`): Now tries `_set_viewer_pan` first
- **Spacebar Press/Release** (`_PanEventFilter`): Now uses `_set_viewer_pan` first
- Falls back to standard QGraphicsView methods if internal method isn't available

### 3. Method Priority Order

For enabling pan mode:

1. `viewer._set_viewer_pan(True)` - NodeGraphQt's internal method (most reliable)
2. `viewer.setDragMode(QGraphicsView.ScrollHandDrag)` - Standard Qt method
3. `viewer.set_pan_mode(True)` - NodeGraphQt's public API fallback

For disabling pan mode (selection):

1. `viewer._set_viewer_pan(False)` - NodeGraphQt's internal method (most reliable)
2. `viewer.setDragMode(QGraphicsView.RubberBandDrag)` - Standard Qt method
3. `viewer.set_pan_mode(False)` - NodeGraphQt's public API fallback

## Files Modified

- `aicodeprep_gui/pro/flow/flow_dock.py`
  - Updated `_configure_viewer()` to enable interactive mode and set transformation anchors
  - Updated `_toggle_pan_mode()` to use `_set_viewer_pan()` first
  - Updated `_PanEventFilter.eventFilter()` spacebar handling to use `_set_viewer_pan()` first

## Testing Instructions

1. Enable Flow Studio from the main window checkbox
2. Test the following pan methods:
   - **Hand Button**: Click the ✋ button in toolbar, then drag with left mouse button
   - **Spacebar**: Hold spacebar while dragging with left mouse button
   - **Arrow Keys**: Use ↑↓←→ keys to pan in that direction
   - **Arrow Buttons**: Click the ↑↓←→ buttons in toolbar
3. Verify zoom still works (mouse wheel)
4. Verify fit button (⊡) still works

## Expected Behavior

- ✅ Hand button toggles pan mode on/off
- ✅ Spacebar temporarily enables pan mode while held
- ✅ Arrow keys pan the canvas
- ✅ Arrow toolbar buttons pan the canvas
- ✅ Mouse drag works when pan mode is active
- ✅ Cursor changes to open hand when pan mode is active
- ✅ Zoom with mouse wheel still works
- ✅ Fit button centers all nodes in view

## Technical Notes

- NodeGraphQt's `NodeViewer` is a custom subclass of QGraphicsView
- It has internal state management that can override standard QGraphicsView drag modes
- Using the internal `_set_viewer_pan()` method ensures proper state synchronization
- The viewer must be set to interactive mode for mouse events to be processed
- Setting transformation anchors improves the user experience during pan/zoom operations
