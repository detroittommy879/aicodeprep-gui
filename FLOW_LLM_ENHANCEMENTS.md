# Flow Studio LLM Node Enhancements

## Changes Made

### 1. Temperature and Top-P Properties

All LLM nodes now have two new properties to control the creativity and randomness of AI responses:

- **temperature** (default: 0.7)

  - Range: 0.0 to 2.0
  - Lower values (0.0-0.5): More focused, deterministic, and conservative
  - Medium values (0.6-0.9): Balanced creativity and coherence
  - Higher values (1.0-2.0): More creative, random, and diverse

- **top_p** (default: 1.0)
  - Range: 0.0 to 1.0
  - Controls nucleus sampling
  - Lower values: More focused on likely tokens
  - Higher values: Considers more token possibilities

### 2. Dynamic Node Display

All nodes now display key information directly on the node in a compact format:

**LLM Node Display:**

```
OpenRouter LLM
gpt-4-turbo
(T:0.9 P:0.95)
```

**I/O Node Display:**

```
Context Output
📄 fullcode.txt

File Write
📝 best_of_n.txt
```

**What's shown:**

- Base node name (e.g., "OpenRouter LLM", "File Write")
- Model name or file path (truncated to max 18 chars per line to prevent overflow)
  - For "choose" mode: displays the actual model name
  - For "random"/"random_free" modes: displays "[random]" or "[random_free]"
- Temperature and Top-P (only shown if different from defaults)
- File icons: 📄 for Context Output, 📝 for File Write

**Example Displays:**

- `OpenRouter LLM\ngpt-4-turbo\n(T:0.9)`
- `OpenAI LLM\n[random_free]`
- `Context Output\n📄 fullcode.txt`
- `File Write\n📝 ...ts/result.txt` (long paths truncated with ellipsis)

### 3. Real-time Updates

The node display updates automatically when you:

- **LLM Nodes:** Change model, model_mode, temperature, or top_p values
- **I/O Nodes:** Change the file path property
- Connect or disconnect ports

### 4. How to Use

1. **Add an LLM node** to your flow (OpenRouter, OpenAI, Gemini, or OpenAI-Compatible)

2. **Configure the model** via the properties panel:

   - Set `model_mode` to "choose" and specify a model, OR
   - Set `model_mode` to "random" or "random_free" for automatic selection

3. **Adjust creativity** (optional):

   - Lower `temperature` (e.g., 0.3) for more focused, consistent outputs
   - Raise `temperature` (e.g., 1.2) for more creative, varied outputs
   - Adjust `top_p` for fine-grained control over token sampling

4. **See the settings** displayed directly on the node in the graph

### 5. Technical Details

- Temperature and top_p are passed to the LiteLLM client
- Invalid values (non-numeric) are caught and logged with a warning
- The node label uses `\n` for multi-line display
- Text is truncated to prevent overflow:
  - Model names: max 18 chars per line (truncated with "...")
  - File paths: max 20 chars total (long paths show "..." + last 17 chars)
- Unicode icons (📄, 📝) help visually identify I/O nodes
- All nodes override `set_property()` to update display when key properties change

## Examples

### Conservative Code Generation

```
temperature: 0.2
top_p: 0.8
```

### Balanced General Purpose

```
temperature: 0.7 (default)
top_p: 1.0 (default)
```

### Creative Writing

```
temperature: 1.2
top_p: 0.95
```

### Very Creative/Experimental

```
temperature: 1.8
top_p: 1.0
```
