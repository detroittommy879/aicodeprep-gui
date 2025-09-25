Please come up with a task list I can give to a AI coding agent like Cline to make the changes to get this working (the flow graph visuals already work good, it just doesn't do much currently). Give enough details to get the subtasks done like "in file xyz.py, find the section that starts with blah blah and replace that entire function with abcblahblahblah" - it helps to give a little explanation as to why we are doing these edits / what our high level purpose is.

REQUIREMENTS doc for the new flow feature where people can send the context block to multiple api endpoints and draw a graph of it (or type what they want, with AI, and it tries to auto-generate it) and route the outputs of that into custom things like prompts and more api endpoints, instead of the default which is to copy it to clipboard and write it to fullcode.txt. For example, I want a built in graph option they can load, where it shows a graph of context output going to 5 different openrouter models. It sends the prompt/question just like normal but instead of to the clipboard/fullcode.txt, it sends using litellm to 5 openrouter models, then the outputs of each one goes to a node that combines it with text/prompt that asks "can you analyze all the different outputs, and also the original code, and come up with a "best of N" best version? try to think of the pros and cons of each, and come up with something better than all of them using all of them as help". There should be a way to set the nodes to "openrouter, but random free" where it will use openrouter api endpoint / auth info but just picks some random free models

use litellm library - with just the python part, not the proxy server. Just openai compatible api endpoints and gemini for now (want to allow people to use openrouter, chutes ai, openai official api, gemini api, add any other openai compatible endpoints etc - but maybe allow them to "lazy load" / add on extras if possible later (not worried for now)? so that every user doesn't have to be bloated from what a few users might want to add to litellm)

I want to also have the graph use a simple language, so that AI can easily generate it from plain language, or people can just type out what they want instead of having to draw the graph / visualization of it.

Can you come up with a task list to get a basic version up and running that has some built in providers like openrouter, gemini api, openai official api, openai compatible (where they can paste in any api endpoint and the app will automatically add on the /chat/completions or whatever is needed, and will be able to use /models and other standard endpoints to allow things like dropdown boxes/random/free since it can grab a list of available models) - it should let them paste in an api key and then it will automatically create a dropdown menu for them to choose a model IF they do add that to a graph. It should also have an option in the dropdown for 'random' and 'random free' (on openrouter it will just use any models that end in :free). For now just add random and free to the openrouter node.

Come up with a basic json file i can load which will have context output --> 5 different models from openrouter --> it will combine all 5 as they come in with a new prompt asking to analyze the original context, the potential solutions created by the 5 models, and a text prompt add on to the end that asks it to analyze all solutions and create a 'best of N or best of all" solution --> that will then go to the clipboard node which will copy to clipboard, and also write to a file best_of_n.txt. The user should be able to load this setup, maybe you can have it built into the app as one of the possible built in ones, If a user tries to run this without plugging in all necessary details like api keys etc it will just show them a popup saying please fill out details for openrouter (or whichever node is an issue). Make sure lots of error catching is built into this and try to think of all the places an error could occur.

Context / tokens - it should try to use the token counter as a guide and try to detect models that have too small of a context window and notify the user somehow (if the info is available) like red letters saying model might not support enough context, try a model with a larger context window) - we can worry about this later once we get some simple model routing working. Put this part in a later phase.

Try to split this main big task up into a few phases where I could test after each phase is added.

---

Please come up with a task list and enclose it in a single code tag so i can copy and paste it into Cline.

---

# Phase 1 – Core Flow Runtime & Data Model (backend-only)

1. **Add litellm dependency**

   - Open `pyproject.toml`; in the `[project] dependencies` list insert a new entry: `"litellm>=1.41.0"`.
   - Reason: we’ll use litellm’s Python API to hit OpenAI-compatible endpoints.

2. **Create flow runtime package**

   - Add a new package directory `aicodeprep_gui/flow_runtime/`.
   - Inside, create `__init__.py` exporting a `FlowRuntime` class and any helpers you need.
   - Create `aicodeprep_gui/flow_runtime/runtime.py` implementing:
     - `FlowRuntime.load_from_json(path_or_dict)` → builds an in-memory graph structure.
     - `FlowRuntime.run(context_text, extra_inputs)` → executes nodes topologically, catching/recording errors.
     - Execution context that stores node outputs keyed by node ID.
     - Shared dataclasses for `NodeSpec`, `ConnectionSpec`, etc.
   - Design it so UI can pass in provider credentials and runtime will handle errors gracefully (return structured error info, not exceptions).
   - Reason: Life-cycle of a run (load graph, execute nodes, gather outputs) must be well-defined before wiring the GUI.

3. **Define base node classes**

   - In `aicodeprep_gui/flow_runtime/nodes/base.py` create an abstract `RuntimeNode` class with:
     - `node_id`, `node_type`, `config` dict.
     - `async execute(context: FlowExecutionContext)` method returning output dict.
     - Synchronous wrapper for `FlowRuntime` to await nodes sequentially.
   - Provide helper to fetch upstream payloads.
   - Reason: NodeGraphQt UI nodes are purely visual; runtime nodes must be independent, testable, and decoupled from Qt.

4. **Implement initial runtime nodes**

   - Add a module `aicodeprep_gui/flow_runtime/nodes/io.py` with runtime counterparts to existing graph nodes:
     - `ContextSourceNode` (reads context text from runtime input rather than a file for now).
     - `ClipboardNode`, `FileWriterNode`.
     - Include defensive checks (e.g., clipboard node requires `QtWidgets.QApplication.clipboard()`; if unavailable, return error).
   - Reason: we’ll replace the current “copy to clipboard” logic with runtime-driven execution in Phase 4.

5. **Create provider runtime nodes**

   - Add `aicodeprep_gui/flow_runtime/nodes/model_nodes.py` with placeholder `MultiCompletionNode` class that:
     - Reads provider config from node `config`.
     - Has stub method `call_model` (to be implemented in Phase 3).
     - For now, return `{ "outputs": [], "metadata": {} }` and mark node as “not implemented”.
   - Reason: Wireframe so UI can already build graphs referencing provider nodes while backend is still stubbed.

6. **JSON schema & loader**
   - Create `aicodeprep_gui/flow_runtime/schema.py` describing the JSON structure (nodes array, edges array, version).
   - In `FlowRuntime.load_from_json`, validate against schema (use `jsonschema` if already installed; otherwise simple manual checks).
   - Reason: ensures flows authored by AI are validated before execution, avoiding random runtime crashes.

# Phase 2 – Flow Studio UI Integration & Settings

1. **Add “Flow Settings” dialog**

   - Create `aicodeprep_gui/gui/components/flow_settings_dialog.py` with a dialog that:
     - Lets user enter API keys per provider (OpenRouter, OpenAI, Gemini, “Custom OpenAI-compatible”).
     - Persists encrypted/obfuscated values via `QSettings` (similar to existing preferences).
   - Hook dialog under Flow menu (“Manage Provider Credentials…”).
   - Reason: runtime nodes need credentials; UI must store/retrieve them securely.

2. **Expose runtime in FlowStudioDock**

   - Edit `aicodeprep_gui/pro/flow/flow_dock.py`:
     - Import `FlowRuntime` at top (lazy import to avoid heavy load if NodeGraphQt absent).
     - Add instance attribute `self.runtime = None` and new method `_build_runtime_from_graph()` that exports graph JSON (reuse serializer) and feeds it to `FlowRuntime`.
     - Replace current `FlowStudioDock.run()` stub:
       - Validate runtime (call `_build_runtime_from_graph`).
       - Fetch current “context text” by calling an injected callback `self.parent().get_current_context_text()` (create fallback placeholder returning clipboard text or file content).
       - Await runtime `run` (use `asyncio.run` or start a worker thread if UI must stay responsive; for first version synchronous is acceptable).
       - Display results in a message box or update Output Display node’s property.
   - Reason: tying the runtime to existing Run Flow button enables end-to-end execution.

3. **Graph export enhancements**

   - Ensure serializer includes node `config` JSON and not just UI info. Look at `aicodeprep_gui/pro/flow/serializer.py`:
     - Confirm `save_session` / `load_session` round-trips node custom properties; adjust if needed.
     - When building runtime (step above), use `node.to_dict()` or equivalent to pull `custom_property_data`, `inputs`, `outputs`, `position`.
   - Reason: runtime needs provider configs stored in node properties.

4. **Flow error messaging**

   - Add centralized helper in `FlowStudioDock` to interpret runtime errors (missing API key, HTTP failure, etc.) and show `QMessageBox.warning` with actionable text.
   - Reason: empowers users to fix configuration issues quickly.

5. **Provider settings injection**
   - Create a helper `aicodeprep_gui/flow_runtime/settings.py` with `get_provider_settings()` reading `QSettings`.
   - In `FlowRuntime.run`, fetch provider credentials via this helper (pass a callback when constructing runtime if static import not desired).
   - Reason: runtime shouldn’t know about Qt; pass in provider info from GUI so backend remains testable.

# Phase 3 – Provider Implementations & Model UI

1. **Implement provider registry**

   - Create `aicodeprep_gui/flow_runtime/providers/__init__.py` exposing:
     - `ProviderRegistry` mapping provider type strings (`"openrouter"`, `"openai"`, `"gemini"`, `"custom_openai"`) to callables.
     - A base `ProviderConfig` dataclass (api_url, api_key, optional headers).
   - Add concrete provider modules (`openrouter.py`, `openai.py`, `gemini.py`, `custom_openai.py`) each with:
     - Function `list_models(config)` returning list of dicts with `id`, `display_name`, `context_window`.
     - Function `complete(config, model_id, prompt, **kwargs)` using litellm `completion`/`acompletion`.
   - Support `random` & `random_free` for OpenRouter by filtering model list before call.

2. **Wire provider nodes**

   - Update `aicodeprep_gui/flow_runtime/nodes/model_nodes.py`:
     - `MultiCompletionNode.execute` should build prompts for each target model in node config, call provider registry, and collect results.
     - Add strong error handling: missing API key → return `{"error": "Missing OpenRouter key"}`; HTTP/status errors include provider message.
     - Include concurrency support: run sequential first; leave TODO for async/gather in later phase.

3. **Model selector UI widget**

   - In Flow Studio, provider nodes should expose dropdowns for models.
   - Modify `aicodeprep_gui/pro/flow/nodes/io_nodes.py` (or create new node class file for provider nodes) so `NodeGraphQt` nodes:
     - Add inputs: (“prompt text”), (“context text”).
     - Add properties for provider type and selected model.
     - Add button property “Refresh Models” that calls provider registry (using credentials) and repopulates options.
   - Probably create new node class `MultiModelNode` (visual).
   - Reason: users need to choose models without editing raw JSON.

4. **Provider config validation**

   - Extend Flow Settings dialog to test credentials (call `list_models()` with `timeout=5`).
   - Save the resulting model list cache in QSettings to re-use (store timestamp to refresh as needed).
   - Reason: ensures runtime won’t hit endpoints with invalid keys.

5. **Token window metadata**
   - When listing models, capture their context window if provider exposes it.
   - Store in node property so runtime can warn later (Phase 5). For now simply store `model_info` mapping.

# Phase 4 – Built-in “Best of 5 OpenRouter” Flow & Execution Pipeline

1. **Add built-in flow JSON**

   - Create `aicodeprep_gui/flow_runtime/presets/best_of_five_openrouter.json` with structure:
     - Source node: `ContextOutput` (reads from GUI context text).
     - Five `OpenRouterCompletion` nodes each configured with different default models (or placeholder `random_free`).
     - Aggregation node that:
       - Accepts original context + all five responses.
       - Applies a fixed prompt asking: “Analyze all outputs and produce improved best-of version…”.
       - Calls OpenRouter again (maybe `random_free` or configurable).
     - Output nodes: `ClipboardNode` + `FileWriterNode` writing `best_of_n.txt`.
   - Document schema at top of JSON file for clarity.

2. **Preset loader UI**

   - In `FlowStudioDock`, add menu item under Flow → “Load Built-in Flow → Best of Five OpenRouter”.
   - Implement method `load_builtin_flow(name)` reading from `presets` dir and invoking serializer `load_session`.
   - After loading, mark graph as dirty (update title/status).

3. **Run pipeline integration**

   - Ensure `FlowRuntime.run` now:
     - Accepts `context_text` from GUI.
     - Passes it to source node.
     - After execution, returns dict with final outputs (e.g., `{"clipboard_text": "...", "file_outputs": {"best_of_n.txt": "..."} }`).
   - Modify `FlowStudioDock.run()` to:
     - If runtime returned clipboard text, copy to clipboard using same code as `process_selected` currently does.
     - For file outputs, write to designated path with error handling (create in cwd).
     - Update status label or show toast summarizing success (e.g., “Combined answer copied to clipboard & saved to best_of_n.txt”).

4. **Credential enforcement**

   - Before running, call helper `ensure_provider_credentials(node_list)`:
     - For each node needing provider, check `QSettings` for required key.
     - If missing, show popup specifying provider (e.g., “Flow requires OpenRouter API key. Please open Flow → Manage Provider Credentials.”).
     - Abort run gracefully.
   - Reason: prevents runtime from attempting failing requests.

5. **Runtime logging**
   - Add logging (using `logging` module) when each node starts and completes.
   - On exceptions, log stack trace, but only expose user-friendly message.
   - Reason: debug runs without disturbing UI.

# Phase 5 – Text & DSL Input (simple language for AI)

1. **Define DSL spec**

   - Create `docs/flow_dsl.md` describing a minimal declarative syntax, e.g.:
     ```
     flow "best_of_n":
       context -> openrouter(model=random_free) x5
       openrouter.results -> aggregator(prompt="Analyze all solutions ...")
       aggregator.output -> clipboard
       aggregator.output -> file("best_of_n.txt")
     ```
   - Reason: Provide guidance for conversion.

2. **Implement parser**

   - Add `aicodeprep_gui/flow_runtime/parser.py` with function `parse_flow_spec(text)` returning the JSON structure used by runtime.
   - Keep grammar simple (YAML-like, maybe use `pyparsing` or manual split lines).
   - Provide tests (Phase 6 optional) verifying DSL → JSON matches preset.

3. **Hook parser to UI**
   - In Flow menu, add “Import Flow from Text…”.
   - Show a dialog with text box; parse on submit; on success, load into Flow Studio graph (maybe by converting JSON to NodeGraph session).
   - Reason: enables AI suggestions and manual text entry.

# Phase 6 – Testing & Polish

1. **Unit tests for runtime**

   - Create `tests/test_flow_runtime.py` (if test suite exists; otherwise new). Cover:
     - Loading preset JSON.
     - Mock provider completions (patch litellm) returning known strings and verifying aggregator output is processed.
     - Missing API key handling.
   - Provide instructions to run `pytest` (if not currently used, add minimal harness).

2. **Manual QA checklist**

   - Document manual test steps in `docs/flow_testing.md`: run built-in flow with dummy context using actual OpenRouter key, verify results.

3. **Future TODO placeholders**
   - In runtime nodes, add `# TODO Phase7: parallel execution`, `# TODO Phase8: token window checks` etc. so future work is scaffolded (per requirement to note red text warnings later).

---

```
Phase 0 – Prep & Dependencies
  0.1 Update pyproject.toml:
      • Under [project] → dependencies, add "litellm>=1.40.0".
      • Run `pip install litellm` in dev environment after editing.
  0.2 Create new module file aicodeprep_gui/flow/__init__.py exporting shared helpers (will be filled next phases).

Phase 1 – Core Flow Runtime & Context Hand-off
  1.1 Store latest generated context in the GUI:
      • In aicodeprep_gui/gui/main_window.py locate FileSelectionGUI.process_selected().
      • After reading fullcode.txt into `content`, set `self.latest_context_text = content`.
      • Add `self.latest_context_text = ""` to __init__ initializer near other state variables.
  1.2 Flow runtime module:
      • Create new file aicodeprep_gui/flow/runtime.py.
      • Implement classes:
          - FlowExecutionError(Exception).
          - FlowContext dataclass with `graph`, `inputs`, `settings`, `logger`.
          - FlowRunner with methods:
              • `from_graph(graph_widget)` -> builds adjacency/topological order using NodeGraphQt API (raise FlowExecutionError on cycles).
              • `run(start_payload: dict)` -> iterates nodes, calling node.run(inputs, settings).
          - Utility to collect node inputs from connected ports, ensuring missing input raises descriptive error.
      • Keep runtime import-light (no Qt), but allow optional logger callable.
  1.3 Wire runtime into FlowStudioDock:
      • In aicodeprep_gui/pro/flow/flow_dock.py:
          - Add `self.runner = None`.
          - On successful `_ensure_flow_dock()` / graph load, instantiate FlowRunner storing NodeGraphQt graph (Graph widget accessible via self.graph).
          - Enable Run Flow toolbar button only when runner built and not read_only (`self._act_run.setEnabled(not self.read_only)`).
          - Connect `_act_run.triggered` to new method `_on_run_clicked`.
  1.4 Implement FlowStudioDock._on_run_clicked:
      • Fetch main window via `main_window = self.parent()`; guard if None.
      • Ensure main_window has `latest_context_text`; if empty, attempt to reopen fullcode.txt; if still empty show QMessageBox warning to generate context first.
      • Build payload dict `{"context": context_text, "prompt": main_window.prompt_textbox.toPlainText()}`.
      • Call `self.runner.run(payload)` inside try/except; on exceptions show critical dialog with traceback text (use logging).
      • Store last result on dock (e.g., `self.last_run_output = result` for debugging).

Phase 2 – Provider Configuration & litellm Nodes
  2.1 Provider settings utility:
      • Create file aicodeprep_gui/flow/providers.py with functions:
          - `get_provider_settings(provider_id: str) -> dict`.
          - `save_provider_settings(provider_id: str, **kwargs)`.
          - Use QtCore.QSettings("aicodeprep-gui", "FlowProviders").
          - Provide helper `require_api_key(provider_id, parent)` that prompts user via QInputDialog if key missing.
  2.2 Shared litellm helper:
      • In providers.py add `call_llm(provider_id, model, messages, extra_params)` that:
          - loads settings, merges base_url, api_key.
          - Handles `model == "random"` / `"random_free"` for openrouter:
                ▪ fetch models using requests (cache in settings for 5 minutes with timestamp).
                ▪ choose random free model (endswith ":free") or any random.
          - Wrap litellm.completion call, return string response. Catch litellm exceptions and rethrow FlowExecutionError with readable message.
  2.3 New node definitions:
      • Create aicodeprep_gui/pro/flow/nodes/provider_nodes.py.
      • Implement `LLMCallNode(BaseExecNode)`:
          - Properties: provider_id (enum), model (string), temperature(float default 0.2), extra_prompt(str optional).
          - add_input("text") for context; add_input("prompt") optional override; add_output("response").
          - run(): combine inputs: context_text, prompt_text, append `self.get_property("extra_prompt")`.
          - Build messages:
                [{"role": "system", "content": "You are an AI assistant analyzing provided context."},
                 {"role": "user", "content": combined_text}]
          - Use providers.call_llm.
          - Return {"response": text_result, "model": chosen_model}.
      • Implement `ModelListNode` later? (not required now).
  2.4 Register node:
      • In pro/flow/flow_dock.py `_register_nodes`, import and register LLMCallNode.
      • Update `__all__` if necessary.

Phase 3 – Aggregation & Output Nodes
  3.1 Combine node:
      • Add file aicodeprep_gui/pro/flow/nodes/aggregator_nodes.py with class `BestOfAggregatorNode(BaseExecNode)`:
          - Inputs: add_input("context"), add_input("prompt"), add_input("responses", multi_input=True).
          - Property: `analysis_prompt` default text (from requirements).
          - run():
                ▪ Gather responses as list of dicts (ensure order stable).
                ▪ Build summary text enumerating responses (include model id if provided).
                ▪ Compose final messages:
                    system prompt emphasising "synthesize best-of".
                    user content concatenating context, original prompt, aggregated outputs, analysis_prompt.
                ▪ Call providers.call_llm using provider for aggregator (allow separate provider_id property default openrouter).
                ▪ Return {"best_response": text, "debug_bundle": {...}}.
      • Register node in FlowStudioDock register method.
  3.2 Extend ClipboardNode:
      • In existing pro/flow/nodes/io_nodes.py update ClipboardNode to override run():
          - Accept `text` input; on run, copy to QApplication.clipboard(); return {"status": "copied"}.
          - Add try/except with FlowExecutionError on failure.
  3.3 Extend FileWriteNode.run():
      • In same file, add run() to write incoming text to configured path (default still fullcode.txt). Use os.path.join(os.getcwd(), property path). Return {"path": path}.
  3.4 Add optional `PassThroughNode`? Not needed.

Phase 4 – Execution Wiring & Built-In Flow Template
  4.1 FlowRunner node invocation contract:
      • Update runtime FlowRunner to expect each node to expose `run(inputs, settings)` (for IO nodes update accordingly). Provide default run in BaseExecNode fallback that uses `self.run(inputs, settings)` method (already defined but returning {}), ensure override uses `BaseExecNode.run`.
  4.2 Ensure NodeGraph connections produce dictionaries:
      • For nodes that output single field, return dict with keys matching port names.
      • FlowRunner should map port names to keys; when connecting multi-input aggregator ensure collects list.
  4.3 Built-in flow JSON:
      • Create directory aicodeprep_gui/data/flows/ if missing.
      • Add file best_of_five_openrouter.json with structure (document nodes, positions, properties) referencing new node types. Use 5 LLMCallNodes with models set to placeholder "random_free".
      • Ensure aggregator provider_id maybe "openrouter".
      • Connect aggregator output to ClipboardNode and FileWriteNode (path best_of_n.txt).
      • Provide metadata key `requires`: ["openrouter"] for UI hints.
  4.4 Loader helper:
      • In flow/runtime or new module aicodeprep_gui/flow/templates.py add function `load_builtin_flow(name)` returning parsed JSON.
      • Modify FlowStudioDock._flow_reset_action to detect template name (maybe new combo). For now, extend existing `_flow_reset_action` to ask user via QInputDialog to choose "Default context→clipboard" or "Best of 5 (OpenRouter)".
      • When user selects best-of template, clear graph then call new helper to import nodes via serializer.import_from_json.
  4.5 Simple language importer stub:
      • Add method FlowStudioDock._show_text_importer() (hook to Flow menu new action "Generate Flow from Text…").
      • Create new action in Flow menu (main_window __init__ Flow menu) hooking to new method.
      • Implementation: opens QDialog with QTextEdit where user can paste DSL (for now accept JSON). Parse using json.loads; on failure show tooltip. On success call serializer.import_from_json.
      • Document that natural language support TODO (leave comment). This satisfies "simple language" requirement as JSON spec accessible to AI.

Phase 5 – Provider UI, Validation & Error Handling
  5.1 Provider property editor:
      • In LLMCallNode.__init__, call `self.create_property("provider_id", "openrouter", items=["openrouter","openai","gemini","custom"])`.
      • For model property: `self.create_property("model_name", "random_free")`.
      • Use NodeGraphQt property UI so user can pick from dropdown (works through PropertiesBin).
  5.2 Missing API key guard:
      • In providers.call_llm, if api_key missing call require_api_key; if user cancels raise FlowExecutionError("API key missing for {provider}").
  5.3 Post-run feedback:
      • In FlowStudioDock._on_run_clicked after success show non-blocking QMessageBox.information summarizing outputs (path to best_of_n.txt). Optionally open aggregator debug.
  5.4 Token limit warning stub:
      • In runtime.run before executing nodes gather payload["context"] length in tokens (use len//4). Store in FlowRunner (self.token_estimate). After aggregator output, if provider metadata includes `max_context_tokens` property (optional), compare and warn (for now just TODO comment). Provide method FlowRunner.check_context_window() returning placeholder; call in _on_run_clicked to display yellow banner (QMessageBox) when stub triggered.
  5.5 Logging:
      • Add logging statements to runtime, providers, nodes using logging.getLogger("flow"). Log start/end of each node, provider responses truncated to 200 chars.

Phase 6 – Tests & Docs
  6.1 Manual test harness:
      • Add script tests/manual_flow_test.py that loads best_of_five template with mocked providers (optional). If time short, create README instructions.
  6.2 README update:
      • Append section "Flow Studio Best-of-5" describing new capability and API key requirements.
      • Mention the JSON template path.
  6.3 Ensure __all__ exports:
      • Update aicodeprep_gui/pro/flow/__init__.py to expose new nodes/modules.
      • If needed adjust aicodeprep_gui/flow/__init__.py to import runtime, providers.

After all phases, run lint/tests:
  • `python -m pip install litellm` (already).
  • `python -m pytest` (if suite).
  • Manual run: start app, generate context, open Flow Studio, reset to template, fill API key, run flow, verify clipboard + best_of_n.txt.

```
