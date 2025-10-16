# Visual Guide: BestOfNNode Dynamic Slots

## Node Appearance by Configuration

```
┌─────────────────────────────────────────────┐
│          BEST-OF-3 CONFIGURATION            │
│         (num_candidates = 3)                 │
├─────────────────────────────────────────────┤
│ Properties:                                 │
│   provider: openrouter                      │
│   model: google/gemini-2.5-pro              │
│   num_candidates: [3]  ↑↓                  │ ← SPINNER CONTROL
│   extra_prompt: [...]                       │
├─────────────────────────────────────────────┤
│ Canvas Node Display:                        │
│                                             │
│  ┌──────────────────────────┐               │
│  │ Best-of-N Synthesizer   │               │
│  ├──────────────────────────┤               │
│  │ context ●────────────────┤ (from Context)
│  │                          │               │
│  │ candidate1 ●─────────────┤ (LLM-1)      │
│  │ candidate2 ●─────────────┤ (LLM-2)      │
│  │ candidate3 ●─────────────┤ (LLM-3)      │
│  │ [---────────────────────]│ (collapsed)  │
│  │ [candidate4-10 hidden]   │              │
│  │ ────────────────────────→ text ●        │
│  └──────────────────────────┘               │
│                                             │
└─────────────────────────────────────────────┘


┌─────────────────────────────────────────────┐
│          BEST-OF-5 CONFIGURATION            │
│         (num_candidates = 5)                 │
├─────────────────────────────────────────────┤
│ Canvas Node Display:                        │
│                                             │
│  ┌──────────────────────────┐               │
│  │ Best-of-N Synthesizer   │               │
│  ├──────────────────────────┤               │
│  │ context ●────────────────┤              │
│  │                          │               │
│  │ candidate1 ●─────────────┤              │
│  │ candidate2 ●─────────────┤              │
│  │ candidate3 ●─────────────┤              │
│  │ candidate4 ●─────────────┤              │
│  │ candidate5 ●─────────────┤              │
│  │ [candidate6-10 hidden]   │              │
│  │ ────────────────────────→ text ●        │
│  └──────────────────────────┘               │
│                                             │
└─────────────────────────────────────────────┘


┌─────────────────────────────────────────────┐
│         BEST-OF-10 CONFIGURATION            │
│         (num_candidates = 10)                │
├─────────────────────────────────────────────┤
│ Canvas Node Display:                        │
│                                             │
│  ┌──────────────────────────┐               │
│  │ Best-of-N Synthesizer   │               │
│  ├──────────────────────────┤               │
│  │ context ●────────────────┤              │
│  │                          │               │
│  │ candidate1 ●─────────────┤              │
│  │ candidate2 ●─────────────┤              │
│  │ candidate3 ●─────────────┤              │
│  │ candidate4 ●─────────────┤              │
│  │ candidate5 ●─────────────┤              │
│  │ candidate6 ●─────────────┤              │
│  │ candidate7 ●─────────────┤              │
│  │ candidate8 ●─────────────┤              │
│  │ candidate9 ●─────────────┤              │
│  │ candidate10 ●────────────┤              │
│  │ ────────────────────────→ text ●        │
│  └──────────────────────────┘               │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Spinner Control Interaction

```
User sees in Properties Panel:
┌──────────────────────────────┐
│ num_candidates: [5]   ↑  ↓   │
└──────────────────────────────┘
           ↓ click ↑ arrow
┌──────────────────────────────┐
│ num_candidates: [6]   ↑  ↓   │
└──────────────────────────────┘
           ↓ click ↑ arrow
┌──────────────────────────────┐
│ num_candidates: [7]   ↑  ↓   │
└──────────────────────────────┘

OR triple-click and type:
┌──────────────────────────────┐
│ num_candidates: [__]  ↑  ↓   │ ← select all
└──────────────────────────────┘
           ↓ type "3"
┌──────────────────────────────┐
│ num_candidates: [3]   ↑  ↓   │
└──────────────────────────────┘
```

---

## Slot State Diagram

```
All 10 Candidate Slots Always Exist:

┌─────────────────────────────────────────────────────┐
│ Internal Node Structure (Always 10 slots)           │
├─────────────────────────────────────────────────────┤
│ candidate1  ●                                       │
│ candidate2  ●                                       │
│ candidate3  ●                                       │
│ candidate4  ●  ←─ Active if num_candidates >= 4    │
│ candidate5  ●  ←─ Active if num_candidates >= 5    │
│ candidate6  ●  ←─ Active if num_candidates >= 6    │
│ candidate7  ●  ←─ Active if num_candidates >= 7    │
│ candidate8  ●  ←─ Active if num_candidates >= 8    │
│ candidate9  ●  ←─ Active if num_candidates >= 9    │
│ candidate10 ●  ←─ Active if num_candidates = 10    │
└─────────────────────────────────────────────────────┘
                        ↓
            num_candidates property
               determines which
            slots are considered
             "active" in run()
```

---

## Connection Flow Diagram

```
BEST-OF-3 FLOW:
═════════════════════════════════════════════════════

Context Output        LLM Nodes             Synthesizer
    │                    │                       │
    ├──fullcode.txt──┬───┤ GPT-5 ──┐
    │                │   │          │
    │                ├───┤ Qwen3 ──┼──► Best-of-N  ◄─ num_candidates=3
    │                │   │          │    (3 slots
    │                └───┤ Claude ─┘     active)
    │                    │
    │                    X (no connection needed
    │                    X  for candidate4-10)
    │                    │
    └────────────────────┴──► context
```

---

## State Management

```
User Action: Change spinner from 5 to 3
                        ↓
        Property value num_candidates = 3
                        ↓
         On next flow run():
                        ↓
    for i in range(1, 4):  # Only checks 1-3
        collect candidate[i]
                        ↓
    Processes only 3 candidates (not 4-5)
                        ↓
    Result: "Best of 3" synthesis
```

---

## Best Practices

### For End Users

```
┌─────────────────────────────────────────┐
│  ✅ DO: Match num_candidates to models  │
│                                         │
│  num_candidates = 3                     │
│  candidate1 ← Model A                   │
│  candidate2 ← Model B                   │
│  candidate3 ← Model C                   │
│  candidate4 [not used]                  │
│  candidate5 [not used]                  │
│                                         │
├─────────────────────────────────────────┤
│  ❌ DON'T: Mismatch settings and data   │
│                                         │
│  num_candidates = 5                     │
│  candidate1 ← Model A                   │
│  candidate2 ← Model B                   │
│  candidate3 ← Model C                   │
│  candidate4 [nothing connected]         │
│  candidate5 [nothing connected]         │
│  → Results in warning, uses only 3      │
│                                         │
└─────────────────────────────────────────┘
```

---

## Template Comparison Table

```
┌──────────────────────────────────────────────────────┐
│ Flow Template Configurations                          │
├─────────────────────┬──────────┬─────────────────────┤
│ Template Name       │ num_cand │ Models              │
├─────────────────────┼──────────┼─────────────────────┤
│ Best-of-5           │    5     │ OpenRouter random   │
│ (OpenRouter)        │          │ selection           │
├─────────────────────┼──────────┼─────────────────────┤
│ Best-of-5           │    5     │ • GPT-5 Codex      │
│ (Configured)        │          │ • Claude Sonnet    │
│                     │          │ • GLM-4.6          │
│                     │          │ • Qwen3            │
│                     │          │ • O4-Mini          │
├─────────────────────┼──────────┼─────────────────────┤
│ Best-of-3           │    3     │ • GPT-5 Codex      │
│ (Configured)        │          │ • Qwen3            │
│                     │          │ • Claude Sonnet    │
└─────────────────────┴──────────┴─────────────────────┘
```

---

## Execution Timeline

```
┌──────────────────────────────────────────┐
│     Flow Execution with num_candidates   │
├──────────────────────────────────────────┤
│ 1. User opens Best-of-3 template         │
│    → num_candidates automatically = 3    │
│                                          │
│ 2. User connects 3 LLM nodes to          │
│    candidate1, candidate2, candidate3    │
│                                          │
│ 3. User clicks "Run Current Flow"        │
│                                          │
│ 4. Context node generates fullcode.txt   │
│                                          │
│ 5. Each LLM processes (parallel):        │
│    - candidate1 input → LLM-1 output     │
│    - candidate2 input → LLM-2 output     │
│    - candidate3 input → LLM-3 output     │
│    (candidate4-10 ignored)               │
│                                          │
│ 6. BestOfN runs():                       │
│    - Gets num_candidates = 3             │
│    - Collects 3 candidates only          │
│    - Sends to Gemini: synthesize 3       │
│                                          │
│ 7. Result → Clipboard + File + Display   │
│                                          │
└──────────────────────────────────────────┘
```

---

## Summary: The Feature in Action

```
BEFORE (Unused Slots):
┌──────────────────────────────┐
│ Best-of-N Synthesizer        │
│ context ●                    │
│ candidate1 ●                 │
│ candidate2 ●                 │
│ candidate3 ●                 │
│ candidate4 ● [unused]        │ ← Visual clutter!
│ candidate5 ● [unused]        │
│ → text ●                     │
└──────────────────────────────┘

AFTER (Configurable):
┌──────────────────────────────┐
│ Best-of-N Synthesizer        │
│ [num_candidates: 3] ↑ ↓      │ ← User control!
├──────────────────────────────┤
│ context ●                    │
│ candidate1 ●                 │
│ candidate2 ●                 │
│ candidate3 ●                 │ ← Clean UI!
│ [candidate4-10 hidden]       │
│ → text ●                     │
└──────────────────────────────┘
```
