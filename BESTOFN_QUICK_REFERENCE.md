# BestOfNNode Dynamic Slots - Quick Reference

## 🎯 What Changed

The BestOfNNode now has a **`num_candidates` spinner control** that lets you specify how many candidate slots (1-10) to use. No more unused slots visible!

---

## 🎛️ How to Use It

### 1. **Load a Template**

```
Flow Menu → Load Built-in: Best-of-3 (Configured)
                          OR
           → Load Built-in: Best-of-5 (Configured)
```

### 2. **Adjust Slot Count (Optional)**

- Select the BestOfNNode in canvas
- Find `num_candidates` in Properties panel
- Click ↑ ↓ arrows or type a number (1-10)
- Default is 5, but templates auto-set to their value

### 3. **Connect Your Models**

```
Best-of-3: Connect to candidate1, candidate2, candidate3
Best-of-5: Connect to candidate1-5
Custom:    Connect to however many you set
```

### 4. **Run!**

```
Flow Menu → Run Current Flow
```

---

## 📊 Configuration Examples

| Use Case    | Setting | Models    | Speed | Quality    |
| ----------- | ------- | --------- | ----- | ---------- |
| Quick Draft | 2       | 2 models  | ⚡⚡  | ⭐⭐       |
| Balanced    | 3       | 3 models  | ⚡    | ⭐⭐⭐     |
| Standard    | 5       | 5 models  | 🔄    | ⭐⭐⭐⭐   |
| Thorough    | 7       | 7 models  | 🐌    | ⭐⭐⭐⭐⭐ |
| Complete    | 10      | 10 models | 🐢    | ⭐⭐⭐⭐⭐ |

---

## 🔧 Properties Reference

| Property         | Type      | Range                                  | Default                      | Notes                           |
| ---------------- | --------- | -------------------------------------- | ---------------------------- | ------------------------------- |
| `num_candidates` | Spinner   | 1-10                                   | 5                            | Controls active slot count      |
| `provider`       | Dropdown  | openrouter, openai, gemini, compatible | openrouter                   | Where to send synthesis request |
| `model`          | Text      | Any valid model ID                     | google/gemini-2.5-pro        | Model for synthesis             |
| `model_mode`     | Dropdown  | choose, random, random_free            | random_free                  | OpenRouter model selection      |
| `extra_prompt`   | Text Area | Any text                               | (system prompt)              | Custom synthesis instructions   |
| `api_key`        | Text      | API key                                | (auto-loaded)                | Authentication                  |
| `base_url`       | Text      | API endpoint                           | https://openrouter.ai/api/v1 | API endpoint                    |

---

## 🐛 Troubleshooting

### Q: I set num_candidates=5 but only connected 3 models

**A:** You'll see a warning dialog, but it continues with 3. Always connect as many models as you set num_candidates to.

### Q: Can I have more than 10 candidates?

**A:** Not currently. 10 covers all common use cases. Contact if you need more!

### Q: Does changing num_candidates affect saved flows?

**A:** Yes, the property is saved. When you reopen the flow, it remembers your setting.

### Q: Old flow shows num_candidates=0 or missing

**A:** Defaults to 5. Flows created before this feature work automatically at the default.

---

## ⚡ Tips & Tricks

✅ **Match num_candidates to connected models** for best results  
✅ **Use Best-of-3 for fast feedback** during development  
✅ **Use Best-of-5+ for final results** with more diversity  
✅ **Test with 2 models** to validate flow before expanding  
✅ **Collapse properties** if you don't need to adjust num_candidates

---

## 📂 Template Defaults

| Template               | num_candidates | Auto-Set?        |
| ---------------------- | -------------- | ---------------- |
| Best-of-5 (OpenRouter) | 5              | ✅ Yes           |
| Best-of-5 (Configured) | 5              | ✅ Yes           |
| Best-of-3 (Configured) | 3              | ✅ Yes           |
| Blank BestOfN Node     | 5              | ✅ Yes (default) |

---

## 🎓 Common Workflows

### Workflow: Testing with 2 Models

```
1. Create 2 LLM nodes
2. Select BestOfN node
3. Set num_candidates = 2
4. Connect both models
5. Run flow
→ Quick test, low API costs
```

### Workflow: Production Best-of-5

```
1. Load "Best-of-5 (Configured)" template
2. num_candidates auto-set to 5
3. All connections pre-configured
4. Just add API keys and run
→ Professional output, tested configuration
```

### Workflow: Scaling Up to 7

```
1. Start with Best-of-5 template
2. Add 2 more LLM nodes
3. Set num_candidates = 7
4. Connect new models to candidate6, candidate7
5. Run
→ More diversity, more complete analysis
```

---

## 🚀 Next Steps

1. **Load a template** and run your first synthesis
2. **Experiment with different num_candidates** (3, 5, 7)
3. **Measure synthesis time** vs. quality for your use case
4. **Create your optimal template** and save it

---

## 📞 Support

See detailed documentation:

- `BESTOFN_DYNAMIC_SLOTS_SUMMARY.md` - Full implementation details
- `BESTOFN_DYNAMIC_SLOTS_FEATURE.md` - Technical reference
- `BESTOFN_VISUAL_GUIDE.md` - Visual walkthroughs
