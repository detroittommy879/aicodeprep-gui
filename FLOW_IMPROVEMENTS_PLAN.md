# Flow Execution Improvements Plan

**Date:** October 6, 2025

## Current Issues

### 1. **UI Freezing During Flow Execution**

- **Problem:** The main UI thread blocks while executing the flow graph
- **Impact:** Application appears frozen, no feedback to user about progress
- **Root Cause:** Flow execution runs in the main thread

### 2. **LLM Node Timeout/Hanging**

- **Problem:** Flow stops mid-execution when LLM calls take too long
- **Impact:** Incomplete results, wasted API calls
- **Root Cause:** Default 5-minute timeout may be insufficient for large inputs

### 3. **Lack of Partial Success Handling**

- **Problem:** If 1 out of 5 LLMs fails, entire flow fails
- **Impact:** Lose results from successful LLM calls
- **Root Cause:** Best-of-N node requires all inputs

### 4. **No Intermediate Result Visibility**

- **Problem:** Can't see LLM responses until entire flow completes
- **Impact:** Difficult to debug, unclear if progress is being made
- **Root Cause:** Results only stored in memory

## Immediate Fixes (Completed)

### ✅ Fix 1: Fixed UnboundLocalError in Best-of-N Node

- **File:** `aicodeprep_gui/pro/flow/nodes/aggregate_nodes.py`
- **Change:** Removed redundant `LLMClient` import inside conditional
- **Status:** COMPLETED

### ✅ Fix 2: Added Output File Writing to LLM Nodes

- **File:** `aicodeprep_gui/pro/flow/nodes/llm_nodes.py`
- **Change:** Added `output_file` property that writes LLM response to disk
- **Usage:** Set property to `llm1.md`, `llm2.md`, etc. to watch progress
- **Status:** COMPLETED

### ✅ Fix 3: Graceful Handling of Partial Failures

- **File:** `aicodeprep_gui/pro/flow/nodes/aggregate_nodes.py`
- **Change:** Best-of-N now warns but continues with <5 candidates
- **Status:** COMPLETED

### ✅ Fix 4: Extended Timeout for LLM Calls

- **File:** `aicodeprep_gui/pro/flow/engine.py`
- **Change:** Increased timeout from 5 minutes to 10 minutes
- **Status:** COMPLETED

## Short-Term Improvements (Next Steps)

### 🔄 Improvement 1: Background Execution with Progress Window

**Priority:** HIGH

**Goal:** Execute flow in background thread with real-time progress updates

**Implementation:**

1. Create `BackgroundFlowExecutor` class that runs in QThread
2. Use Qt signals/slots to communicate progress to UI
3. Show non-modal progress dialog that allows cancellation
4. Update progress bar and node statuses in real-time

**Files to Modify:**

- `aicodeprep_gui/pro/flow/engine.py` - Add QThread-based executor
- `aicodeprep_gui/pro/flow/progress_dialog.py` - Make non-modal
- `aicodeprep_gui/pro/flow_studio_widget.py` - Use background executor

**Pseudocode:**

```python
class BackgroundFlowExecutor(QThread):
    progress_updated = Signal(str, str, str)  # node_name, status, color
    execution_complete = Signal(bool, dict)   # success, results

    def run(self):
        # Execute flow in background
        for level in levels:
            for node in level:
                self.progress_updated.emit(node_name, "Running", "orange")
                result = node.run(inputs)
                self.progress_updated.emit(node_name, "Complete", "green")
```

### 🔄 Improvement 2: Retry Failed Nodes with Timeout

**Priority:** MEDIUM

**Goal:** Give user option to skip/retry failed nodes

**Implementation:**

1. When node fails, show dialog: "Retry", "Skip", "Cancel Flow"
2. Track which nodes succeeded/failed
3. Allow continuing with partial results

**User Experience:**

```
Node "OpenRouter LLM 4" timed out after 10 minutes.

[Retry]  [Skip & Continue]  [Cancel Flow]

Note: Best-of-N can work with 4/5 successful responses
```

### 🔄 Improvement 3: Streaming Progress for Long-Running Nodes

**Priority:** MEDIUM

**Goal:** Show real-time updates during LLM calls

**Implementation:**

1. Add streaming support to `LiteLLM` client
2. Update progress dialog with partial responses
3. Show "tokens received" counter

**Display:**

```
OpenRouter LLM 1: Running...
  Model: gpt-5-codex
  Tokens: 1,247 / ~2,000 estimated
  Time: 23s / 600s timeout
  [View Partial Response]
```

## Medium-Term: Ember v2 Integration

### 📋 Option A: Replace Flow Engine with Ember v2

**Evaluation Status:** TESTING

**Pros:**

- ✅ Built-in parallel execution with automatic optimization
- ✅ Native ensemble/Best-of-N support
- ✅ Production-ready error handling and retries
- ✅ Built-in MCP server for external integration
- ✅ Cost tracking and usage metrics

**Cons:**

- ❌ Requires rewriting existing flow nodes
- ❌ May not integrate well with NodeGraphQt visual editor
- ❌ Additional dependency to maintain
- ❌ Learning curve for new framework

**Test Plan:**

1. ✅ Created `test_ember_v2.py` - standalone test script
2. 🔄 Install Ember: `pip install ember-ai[mcp]`
3. 🔄 Test parallel LLM execution with 5 models
4. 🔄 Test ensemble/Best-of-N synthesis
5. 🔄 Test MCP server integration
6. 🔄 Evaluate performance vs. current implementation

**Decision Point:** After testing, decide whether to:

- **Option A1:** Replace entire flow engine with Ember
- **Option A2:** Use Ember only for parallel LLM execution
- **Option A3:** Keep current implementation with improvements

### 📋 Option B: Hybrid Approach

**Description:** Keep NodeGraphQt visual editor, use Ember for execution

**Architecture:**

```
User creates flow in NodeGraphQt UI
    ↓
Export flow to Ember-compatible format
    ↓
Execute using Ember's parallel engine
    ↓
Import results back to NodeGraphQt
```

**Pros:**

- ✅ Keep existing visual editor
- ✅ Leverage Ember's execution capabilities
- ✅ Best of both worlds

**Cons:**

- ❌ Complex integration layer
- ❌ Two systems to maintain

## Long-Term: Advanced Features

### 🔮 Feature 1: Distributed Execution

Run flow nodes across multiple machines

### 🔮 Feature 2: Flow Templates & Marketplace

Share and reuse common flow patterns

### 🔮 Feature 3: Real-Time Collaboration

Multiple users editing same flow

### 🔮 Feature 4: Auto-Optimization

Learn which models work best for which tasks

## Testing Instructions

### Test Current Improvements

1. Open Flow Studio
2. Load a flow with 5 LLM nodes
3. Set `output_file` property on each node:
   - LLM 1: `llm1.md`
   - LLM 2: `llm2.md`
   - LLM 3: `llm3.md`
   - LLM 4: `llm4.md`
   - LLM 5: `llm5.md`
4. Run flow and watch files appear in project directory
5. Verify that flow completes even if 1-2 LLMs fail

### Test Ember v2

```bash
# Install Ember
pip install ember-ai[mcp]

# Run test script
python test_ember_v2.py

# Check output files
ls ember_test_llm*.md
```

## Success Criteria

### Phase 1 (Immediate Fixes) ✅

- [x] Flow executes without crashing
- [x] Best-of-N works with partial results
- [x] Intermediate results saved to files
- [x] Longer timeout for LLM calls

### Phase 2 (Background Execution)

- [ ] UI remains responsive during flow execution
- [ ] Real-time progress updates visible
- [ ] Can cancel flow mid-execution
- [ ] Error messages shown in progress dialog

### Phase 3 (Ember Integration)

- [ ] Parallel execution faster than current implementation
- [ ] Better error handling and retries
- [ ] Easy to add new LLM providers
- [ ] Production-ready for heavy use

## Next Actions

1. **IMMEDIATE:** Test current fixes with real flow

   - Action: Run flow with 5 LLMs and output files
   - Expected: Files appear, flow completes with 3-5/5 successes

2. **TODAY:** Test Ember v2 standalone

   - Action: Run `python test_ember_v2.py`
   - Expected: See parallel execution working

3. **THIS WEEK:** Implement background execution

   - Action: Create `BackgroundFlowExecutor` class
   - Expected: UI responsive during flow

4. **NEXT WEEK:** Decide on Ember integration
   - Action: Review test results, make architecture decision
   - Expected: Clear path forward

## Notes

- Keep existing code - don't delete anything yet
- All changes should be additive/optional
- Always provide fallback to current implementation
- Focus on user experience and reliability

## Resources

- Ember v2 Documentation: (included in `ember-v2.md`)
- Current Flow Engine: `aicodeprep_gui/pro/flow/engine.py`
- LLM Nodes: `aicodeprep_gui/pro/flow/nodes/llm_nodes.py`
- Best-of-N: `aicodeprep_gui/pro/flow/nodes/aggregate_nodes.py`
