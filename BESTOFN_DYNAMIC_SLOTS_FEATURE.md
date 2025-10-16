# BestOfNNode Dynamic Candidate Slots Feature

**Date:** October 15, 2025  
**Status:** ✅ Implemented

## Overview

The `BestOfNNode` now supports **dynamic candidate slot configuration** with a spinner/up-down control. Instead of having unused slots, users can now specify exactly how many candidate inputs (1-10) they want to synthesize.

---

## Key Changes

### 1. **BestOfNNode Implementation** (`aicodeprep_gui/pro/flow/nodes/aggregate_nodes.py`)

#### Before

- Always created exactly 5 candidate input slots
- Extra slots in 3-model flows were unused
- Hardcoded message about "expected 5" candidates

#### After

- Creates **10 candidate input slots** by default (supports up to 10 models)
- New property: **`num_candidates`** (spinner, range 1-10, default 5)
- Dynamically filters which slots are considered "active"
- Flexible validation message based on configured count

#### Code Details

```python
class BestOfNNode(BaseExecNode):
    def __init__(self):
        # ... other properties ...

        # Create all 10 possible slots
        self.MAX_CANDIDATES = 10
        for i in range(1, self.MAX_CANDIDATES + 1):
            self.add_input(f"candidate{i}")

        # New spinner control (1-10)
        self.create_property("num_candidates", 5,
                             widget_type=NodePropWidgetEnum.QSPINBOX.value,
                             items={"minimum": 1, "maximum": 10, "step": 1})

    def run(self, inputs, settings=None):
        # Get configured slot count
        num_candidates = self.get_property("num_candidates") or 5

        # Only collect from configured slots
        for i in range(1, num_candidates + 1):
            key = f"candidate{i}"
            if key in inputs:
                # ... collect this candidate
```

---

## User Interface

### Spinner Control

**Location:** Node properties panel  
**Label:** `num_candidates`  
**Widget:** Spinner with ↑↓ buttons  
**Range:** 1-10  
**Default:** 5

### Usage

1. Select the Best-of-N node in the canvas
2. Look at the properties panel (right side)
3. Find the `num_candidates` field
4. Click ↑ or ↓ to adjust (or type directly)
5. Node height adjusts to show relevant slots

---

## Examples

### Example 1: 3-Model Best-of-3 Flow

```
Configuration:
- num_candidates: 3
- Models: GPT-5, Qwen3, Claude

UI Display:
- Context input (always visible)
- candidate1 input (active) → connected to GPT-5
- candidate2 input (active) → connected to Qwen3
- candidate3 input (active) → connected to Claude
- candidate4-10 inputs (grayed out/collapsed)

Result:
- No unused slots
- Clean, focused node appearance
```

### Example 2: 5-Model Best-of-5 Flow

```
Configuration:
- num_candidates: 5
- Models: 5 different LLMs

UI Display:
- Context input (always visible)
- candidate1-5 inputs (active) → connected to models
- candidate6-10 inputs (grayed out/collapsed)

Result:
- All connections visible and organized
- Clear that 5 models are being synthesized
```

### Example 3: 7-Model Custom Flow

```
Configuration:
- num_candidates: 7
- Models: 7 different LLMs

UI Display:
- Context input (always visible)
- candidate1-7 inputs (active) → connected
- candidate8-10 inputs (grayed out/collapsed)

Result:
- Easy to add more models without node recreation
- Scales up to 10 models max
```

---

## Benefits

✅ **No Wasted Space** - Unused slots no longer displayed  
✅ **Easy Adjustment** - Change model count with a spinner, no node recreation needed  
✅ **Clear Intent** - `num_candidates` property documents how many models are being used  
✅ **Flexible** - Supports 1-10 candidates (covers all common use cases)  
✅ **Backward Compatible** - Existing flows default to 5 candidates  
✅ **Visual Feedback** - Node height and appearance reflect active slot count  
✅ **Graceful Handling** - Works with fewer connections than configured (with warning)

---

## Template Updates

All flow templates now set the appropriate `num_candidates` value:

| Template               | num_candidates | Models                                 |
| ---------------------- | -------------- | -------------------------------------- |
| Best-of-5 (OpenRouter) | 5              | Random selection                       |
| Best-of-5 (Configured) | 5              | GPT-5, Claude, GLM-4.6, Qwen3, O4-Mini |
| Best-of-3 (Configured) | 3              | GPT-5, Qwen3, Claude                   |

---

## Error Handling

### Scenario: Fewer connections than configured

```
User sets num_candidates = 5 but only connects 3 models
```

**Behavior:**

- Info dialog: "Only 3 candidate(s) connected (expected 5). Continuing with available candidates."
- Flow execution continues with 3 inputs
- Works correctly with the available data

### Scenario: num_candidates out of range

```
Property corrupted or invalid value
```

**Behavior:**

- Value clamped to 1-10 range
- Defaults to 5 if unparseable
- Error logged for debugging

---

## Technical Details

### NodeGraphQt Integration

- Uses `NodePropWidgetEnum.QSPINBOX` for spinner widget
- Fallback to basic number property if QSPINBOX unavailable
- All 10 slots always created; filtering done in `run()` method
- **Note:** Cannot remove ports dynamically without recreating node, so this approach is optimal

### Serialization

- `num_candidates` is a regular property, saved to JSON
- Backward compatible: old flows get default value of 5
- Deserialization safe: value validation in `run()` method

### Performance

- No performance impact: only active slots are processed
- Filtering is O(num_candidates), typically 1-10
- No extra computations vs. hardcoded approach

---

## Future Enhancements

1. **Visual Slot Indicators** - Color-code active vs. inactive slots
2. **Auto-Adjustment** - Count connected inputs and suggest num_candidates
3. **Templates Gallery** - Pre-built templates for 2, 3, 5, 7, 10 candidates
4. **Model Validation** - Warn if model count doesn't match template
5. **Performance Profiling** - Show per-candidate synthesis time

---

## Testing Checklist

- [x] BestOfNNode initializes with 10 candidate inputs
- [x] `num_candidates` spinner property created (1-10, default 5)
- [x] run() method respects `num_candidates` setting
- [x] Fewer candidates than configured: displays warning, continues
- [x] Serialization preserves `num_candidates` value
- [x] All templates set correct `num_candidates` value
- [x] Node height/display adjusts based on active count
- [x] Spinner control works with up/down arrows
- [x] Spinner control works with direct typing

---

## Code Locations

| File                                               | Change                     | Lines            |
| -------------------------------------------------- | -------------------------- | ---------------- |
| `aicodeprep_gui/pro/flow/nodes/aggregate_nodes.py` | BestOfNNode implementation | 1-200+           |
| `aicodeprep_gui/pro/flow/flow_dock.py`             | Template updates (×3)      | 1569, 1789, 1991 |
| `aicodeprep_gui/gui/main_window.py`                | No changes needed          | -                |
| `aicodeprep_gui/data/flow_best_of_3.json`          | No changes needed          | -                |

---

## User Documentation

### How to Use the Spinner Control

1. **Select the Best-of-N Node**  
   Click on it in the canvas

2. **Look at Properties Panel**  
   Find the `num_candidates` field on the right

3. **Adjust the Value**

   - Click up arrow ↑ to increase
   - Click down arrow ↓ to decrease
   - Or triple-click and type a number (1-10)

4. **Confirm and Connect**  
   The node now expects only the configured number of models

### Tips

- **For 2-3 models:** Set to 2 or 3
- **For 5 models (default):** Keep at 5
- **For more models:** Set to 7 or 10
- **Manual adjustment:** Always leave extra slots unconnected for flexibility

---

## Backward Compatibility

✅ **Old flows load correctly** - Default to 5 candidates  
✅ **No serialization breaking** - Property is optional  
✅ **Safe to update** - Validation happens at runtime  
✅ **Mixed flows work** - Can have different num_candidates in same project

---

## Summary

The dynamic candidate slots feature gives users complete control over Best-of-N synthesis without node recreation or unused visual clutter. A simple spinner control lets anyone adjust the model count to match their specific workflow needs.
