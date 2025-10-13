Short version / TL;DR
- Add new provider nodes (OpenAI official, OpenAI-compatible, Anthropic, Gemini) as small subclasses of your existing LLMBaseNode (or new provider adapter classes) and register them in FlowStudioDock._register_nodes.
- Add standard LLM properties (temperature, top_p, max_tokens, n, stop, timeout_seconds, priority, fallback_providers/retries) to the LLM node base so every provider node inherits them.
- Implement per-node timeout + fallback behavior in the flow engine (execute_graph): read node timeout property and use future.result(timeout=timeout). On timeout/error trigger fallback attempts (secondary provider/model) or return an error code in the node output.
- Add logic nodes (IfThen, RegexMatch/Switch) that produce true/false or route outputs to different ports; these are small nodes that examine upstream text and emit a boolean or which-branch token.
- Keep it modular: create a provider-adapter interface, provider plugins (AnthropicAdapter, OpenAIAdapter, GeminiAdapter) and a simple factory. Node.run uses adapter via factory. Store API keys in config (aicodeprep_gui.config) and allow per-node override.
- UI: expose temperature/top_p sliders and timeout fields in node properties and the LLMModelConfigDialog.

Concrete guidance and examples

1) Make nodes small and composable (recommended structure)
- Keep a single LLMBaseNode with common IO and properties (you already have LLMBaseNode). Extend it:
  - add properties: temperature, top_p, max_tokens, top_k (optional), n, stop, timeout_seconds, priority, retry_attempts, retry_delay, fallback_provider/model list.
  - ensure resolve_api_key() and resolve_base_url() prefer node props then config file.

- Provider adapters:
  - Create a.aicodeprep_gui.pro.llm.adapters module with a ProviderAdapter abstract base class:
    - list_models(api_key, base_url) -> list
    - chat(model, messages, api_key, base_url, extra) -> str
  - Implement OpenAIAdapter, AnthropicAdapter, GeminiAdapter, OpenRouterAdapter, GenericAdapter. LLMClient can become a thin wrapper that delegates to the configured adapter.

Why adapters?
- Keeps Node code provider-agnostic.
- Adding new providers means adding one file/class and registering it with the factory → future proof.

2) Node properties to add (recommended canonical names)
- provider (openai | openrouter | gemini | anthropic | compatible | custom)
- api_key (string or blank)
- base_url (string)
- model (string)
- model_mode (choose/random/random_free)
- temperature (float 0.0–2.0)        ← creativity
- top_p (float 0.0–1.0)             ← nucleus sampling
- top_k (int)                       ← optional
- max_tokens (int)
- n (int)                           ← number of completions
- stop (string or newline-separated)
- timeout_seconds (int)             ← per-node timeout
- retry_attempts (int)
- retry_delay (secs)
- fallback_providers (comma-separated list or JSON array)
- output_file (string)              

Use NodePropWidgetEnum.QLINE_EDIT for numeric/text fields and QTEXT_EDIT for multiline.

3) Per-node timeout and fallback in the engine
- Your engine already uses ThreadPoolExecutor and uses future.result(timeout=600) for the parallel path. Replace the hard-coded 600 with a node-specific timeout:
  - read timeout = getattr(node, 'get_property')('timeout_seconds') or default (e.g., 120)
  - call future.result(timeout=timeout)
- On TimeoutError or LLMError:
  - look at node.get_property('fallback_providers') (list)
  - loop fallback providers/models and re-run the call with adjusted provider/model until success or exhausted
  - update node state and progress UI appropriately

Simple pseudo-change in execute_graph parallel branch:
- For each future, when you call future.result(...), pass per-node timeout (read from node property).
- If it raises concurrent.futures.TimeoutError:
    - call node.run_fallback(...) or drive fallback attempts in the engine: use provider list to make an alternative call (via the same LLMClient/adapter).
    - store result or error accordingly.

Alternative: implement a SupervisorNode (below) that handles retries/fallbacks itself so engine needs no changes. But engine change is cleaner (single place for enforcing timeouts).

4) Example of adding an Anthropic provider node (simple)
- Create a new node class file aicodeprep_gui/pro/flow/nodes/anthropic_node.py (or extend llm_nodes.py):

Example (concise):

class AnthropicNode(LLMBaseNode):
    __identifier__ = "aicp.flow"
    NODE_NAME = "Anthropic LLM"

    def __init__(self):
        super().__init__()
        self.set_property("provider", "anthropic")
        # defaults if desired:
        self.set_property("base_url", "")  # allow configuring custom Anthropic endpoints

    def default_provider(self):
        return "anthropic"

- Register it in FlowStudioDock._register_nodes like the others.

Implement an adapter aicodeprep_gui/pro/llm/adapters/anthropic.py that maps chat signature to Anthropic API calls (or through litellm if supported).

5) Logic nodes (If/Then / Switch)
- Add nodes that inspect a string and set outputs or booleans:

IfThenNode:
- Inputs: text
- Properties: condition_type (contains / equals / startswith / regex), condition_value (string)
- Outputs: true (text), false (text)
- run: examine text, if true -> return {"true": text} else -> {"false": text}

SwitchNode:
- Properties: mapping in JSON like {"yes":"node_a", "no":"node_b"} OR expose ports for multiple branches.

This is straightforward and keeps graph logic visually obvious.

6) Timer / Watchdog node patterns
Two approaches:

A) Engine-level timeouts + fallback (recommended)
- Engine enforces per-node timeout and deals with fallback automatically (less node UI to configure runtime behavior; centralizes rules).
- Node properties control behavior.

B) Node wrapper / Supervisor node
- TimeoutWrapperNode:
  - inputs: text
  - properties: timeout_seconds, primary_provider/model props, fallback_provider/model(s)
  - run: spawn the LLM call in a background thread, wait timeout, if no result cancel (or ignore) and call fallback provider(s); returns the first successful response
- Advantage: no engine changes; encapsulates logic as a node. Disadvantage: duplicated logic if many nodes need it.

Either approach is valid; engine changes give global consistency.

7) Example node implementing timeout + fallback inside run()
Below is compact example pseudocode you can adapt into LLMBaseNode subclass:

def run(self, inputs, settings=None):
    text = inputs.get("text","")
    api_key = self.resolve_api_key()
    base_url = self.resolve_base_url()
    model = self.resolve_model(api_key)
    temp = float(self.get_property("temperature") or 0.7)
    top_p = float(self.get_property("top_p") or 1.0)
    timeout = int(self.get_property("timeout_seconds") or 120)
    fallbacks = parse_list(self.get_property("fallback_providers") or "")
    attempts = 0
    providers_to_try = [(self.get_property("provider"), model, api_key, base_url)] + fallbacks
    for provider, model, ak, bu in providers_to_try:
        attempts += 1
        try:
            out = LLMClient.chat(model=model, user_content=text,
                                 api_key=ak, base_url=bu,
                                 extra_headers=self._extra_headers_for_provider(provider),
                                 system_content=None,
                                 temperature=temp, top_p=top_p,
                                 timeout=timeout)
            return {"text": out}
        except LLMError as e:
            logging.warning(f"Provider {provider} failed: {e}")
            continue
    return {}

Note: adapt LLMClient.chat signature to accept temperature/top_p or pass via extra headers or provider adapter.

8) Add UI controls
- Add temperature / top_p inputs to LLMModelConfigDialog and to node properties panel (PropertiesBinWidget will pick up created properties).
- For nicer UX add a slider or QDoubleSpinBox widget in the properties panel if NodeGraphQt supports custom widgets for node props.

9) Serialization & security
- Do not store API keys into exported flow files (use serializer redaction). your serializer already redacts api_key keys in _redact_in_place — good.
- Prefer users set API keys in config (api-keys.toml) and allow per-node override only for temporary testing.

10) Register nodes & load templates
- Register new nodes in FlowStudioDock._register_nodes.
- Provide some built-in templates (e.g., Context -> Anthropic -> Fallback to OpenAI) and add menu options like your existing load_template_best_of_5_openrouter.

11) Tests and backwards compatibility
- Maintain small unit tests for:
  - provider adapters
  - LLM nodes with dummy LLMClient (mock litellm)
  - engine timeout and fallback behavior
- Keep node property names stable across versions; if you change schema add node.version property (BaseExecNode already has version) and migration code in serializer.

12) Example properties summary (what to expose)
- temperature (float)
- top_p (float)
- max_tokens (int)
- n (int)
- stop (string)
- timeout_seconds (int)
- retry_attempts, retry_delay
- fallback_providers (text list)
- priority (int)
- provider (combo)
- api_key (line)
- base_url (line)
- model (text)
- model_mode (combo)

Implementation steps checklist
1. Add adapter interface + provider adapters (OpenAI, Anthropic, Gemini, OpenRouter, Generic).
2. Expand LLMClient to call adapters or create a thin wrapper over adapters.
3. Add new LLM node classes (AnthropicNode, OpenAINode already present — ensure it implements temperature/top_p) and add new GeminiNode/AnthropicNode if missing.
4. Add properties to LLMBaseNode (temperature/top_p/timeout/etc).
5. Update FlowStudioDock._register_nodes to include new nodes.
6. Add logic nodes (IfThen, RegexMatch, Switch).
7. Implement per-node timeout/fallback either in engine.execute_graph or in a Supervisor node.
8. Add UI inputs for the new properties (PropertiesBinWidget picks up node props). Add LLMModelConfigDialog improvements.
9. Update serializer to redact api_key (already handled).
10. Add built-in templates that demonstrate primary + fallback + conditional routing.

If you want, I can:
- produce a ready-to-drop-in AnthropicNode + ProviderAdapter example using your existing LLMClient style (small code),
- or produce a patch for engine.execute_graph to use per-node timeout + fallback attempts.

Which would you prefer next: a) code example for an Anthropic provider + node, or b) engine changes to enforce per-node timeout + fallback?