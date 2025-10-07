# Flow Graph - Model Naming Guide

## ⚠️ Important: How to Enter OpenRouter Model Names

### ❌ WRONG - Do NOT include the "openrouter/" prefix:

```
openrouter/google/gemini-2.5-flash-preview-09-2025
openrouter/anthropic/claude-3-5-sonnet
openrouter/x-ai/grok-4-fast
```

### ✅ CORRECT - Enter just the model path:

```
google/gemini-2.5-flash-preview-09-2025
anthropic/claude-3-5-sonnet
x-ai/grok-4-fast
deepseek/deepseek-v3.2-exp
mistralai/codestral-2508
```

## Why?

The code **automatically adds** the `openrouter/` prefix for you. If you include it yourself, you'll end up with `openrouter/openrouter/model-name` which won't work (though the latest version now detects and fixes this).

## Finding Model Names

1. Go to https://openrouter.ai/models
2. Click on a model
3. Copy the model ID (e.g., `google/gemini-2.5-flash-preview-09-2025`)
4. Paste it into the Flow node's "model" field **without** the `openrouter/` prefix

## Debugging Flow Execution

The latest version now includes detailed logging:

### What to Check in Logs:

1. **Model names being used**:

   ```
   [OpenRouter LLM] Making LLM call with model: openrouter/google/gemini-2.5-flash-preview-09-2025
   ```

   - Should have exactly ONE `openrouter/` prefix

2. **API call details**:

   ```
   [OpenRouter LLM] API details - provider: openrouter, base_url: https://openrouter.ai/api/v1, input_length: 526591
   ```

3. **Response status**:

   ```
   [OpenRouter LLM] LLM call successful, response length: 1234
   ```

   - If response length is 0, the API returned empty (check API key/model availability)

4. **Best-of-N candidates**:
   ```
   [Best-of-N Synthesizer] Received 5 candidate(s), context length: 526591
   [Best-of-N Synthesizer] Candidate 1 length: 1234
   ```
   - All candidates should have non-zero length
   - If any are 0, that LLM node failed silently

## Common Issues

### Issue: "No candidate inputs provided"

**Causes:**

1. LLM nodes completed but returned empty responses
2. API calls failed silently (invalid API key, rate limits, model not available)
3. Model names were incorrect

**Solution:**

1. Check the console logs for error messages
2. Verify your OpenRouter API key in `api-keys.toml`
3. Check that model names don't have the `openrouter/` prefix
4. Visit your OpenRouter dashboard to see if requests are being received
5. Try using "random_free" mode to let the system pick a working free model

### Issue: Flow completes instantly

**Causes:**

1. Nodes are skipping execution due to errors
2. Model names are malformed (double prefix)

**Solution:**

1. Check logs for "Removed duplicate openrouter prefix" messages
2. Re-enter model names without the `openrouter/` prefix
3. Use the logging to see what's actually being sent to the API

## Testing with Free Models

Set model_mode to "random_free" to automatically use free OpenRouter models:

1. Select your LLM nodes
2. Click "Set Models..." in the toolbar
3. Choose "random_free" mode
4. Run the flow

This will pick from available free models on OpenRouter.

## Viewing API Activity

To confirm requests are reaching OpenRouter:

1. Go to https://openrouter.ai/activity
2. Run your flow
3. You should see new requests appear within seconds
4. If no requests appear, check your API key and model names
