Feature Add-on PRD: “Flow Studio” (Node-Graph, dockable, pro-editable)

Overview

- Goal: Add a dockable “Flow Studio” that lets users compose node-based flows to route prompt/context and model outputs (similar to n8n). Include model nodes (GPT-5, GLM-4.5, Gemini 2.5 Pro), multiple API providers (OpenAI-compatible and native), and output nodes (clipboard, file, display).
- Default: Ship a read-only default flow that exactly mirrors current behavior: Generate Context! → write fullcode.txt → copy to clipboard. Non-Pro users can see the flow but cannot edit; Pro users can edit and create/import/export flows.
- Persistence: Store flows as JSON (using NodeGraphQt’s session save/load). Allow import/export from disk. Project-level default flow stored alongside `.aicodeprep-gui` preferences, with API keys stored in QSettings (not in flow JSON).

Rationale

- Minimally invasive to existing UX: “Generate Context!” continues to work the same. The Flow Studio adds orchestration on top, initially invoked after context generation, then expanded to multi-model pipelines.
- NodeGraphQt (ng.md): Provides the node graph widget, palettes, properties bin, context menus, serialization, and docking examples. It’s a good fit for a dock or separate panel.

Architecture at a glance

- UI: A new dock widget `FlowStudioDock` housing NodeGraphQt’s graph widget (`NodeGraph.widget`), and optional `NodesPaletteWidget` and `PropertiesBinWidget`.
- Nodes (initial set):
  - `ContextOutputNode` (source): outputs the text from `fullcode.txt`.
  - `ClipboardNode`: copies inbound text to OS clipboard.
  - `FileWriteNode`: writes inbound text to a file (default: `fullcode.txt`).
  - `OutputDisplayNode`: shows inbound text (for debugging/results).
- Model nodes:
  - `ModelNode` (generic OpenAI-compatible): endpoint, API key reference, model name, params.
  - `GeminiNode` (native Google API), `GLMNode` (native), and optional `OpenRouterNode` for convenience. All wrap to a consistent “text in → text out” interface.
- Engine: A small executor that topologically orders nodes and runs them (sync first; later async). Inputs are strings; outputs are strings (Phase 3 adds JSON option).
- Providers and secrets: QSettings-backed registry to hold API keys and provider endpoints. Flows store a provider “ref” not the secret.

Gating/Mode

- Free mode:
  - Flow Studio visible but read-only (can’t add/delete/connect nodes).
  - Default built-in flow matches current behavior.
- Pro mode:
  - Full editing: add nodes, drag, connect, run, import/export.

Dependencies

- Add to pyproject (see Phase 0):
  - NodeGraphQt
  - Note: NodeGraphQt uses the “Qt” shim (Qt.py). Recent versions work with PySide6 via shim; if needed, add dependency “Qt.py”.
- Continue using PySide6 (already in your project).

Phases and Testable Deliverables

Phase 0 — Prep and Packaging (low risk)

- Changes:
  - pyproject.toml:
    - Add `NodeGraphQt` to dependencies (or to an optional extra `[project.optional-dependencies.flow]` if you want to lazy install).
    - If needed add `Qt.py >= 1.3`.
- Tests:
  - pip install on all 3 OSes succeeds.
  - App launches normally. - DID THIS PART ---

Phase 1 — Basic Flow Studio Dock, Read-Only Default (no execution changes)

- New files:
  - `aicodeprep_gui/pro/flow/flow_dock.py`
  - `aicodeprep_gui/pro/flow/nodes/base.py`
  - `aicodeprep_gui/pro/flow/nodes/io_nodes.py` (ContextOutputNode, ClipboardNode, FileWriteNode, OutputDisplayNode)
  - `aicodeprep_gui/pro/flow/serializer.py` (wrappers for load/save sessions, redacting sensitive data)
- Imports to use:
  - `from NodeGraphQt import NodeGraph, BaseNode, NodesPaletteWidget, PropertiesBinWidget`
  - `from PySide6 import QtWidgets, QtCore, QtGui`
- Implement:
  - Class `FlowStudioDock(QtWidgets.QDockWidget)`:
    - Creates `NodeGraph()`, sets up `graph.widget` as central content of the dock.
    - Optional tabs: `NodesPaletteWidget`, `PropertiesBinWidget`.
    - Adds lightweight toolbar: “Run Flow” (disabled this phase), “Import”, “Export”.
    - Respect dark mode changes (you can let default styling stand initially).
  - Nodes:
    - `ContextOutputNode(BaseNode)`: one output `text`.
      - Properties: path (default “fullcode.txt”), “use_latest_generated” (bool).
      - For this phase it’s just a placeholder UI (no actual run).
    - `ClipboardNode(BaseNode)`: one input `text`.
    - `FileWriteNode(BaseNode)`: one input `text`, property `path` (“fullcode.txt”).
    - `OutputDisplayNode(BaseNode)`: one input `text`, display preview area (property bin can read value).
  - Register nodes (NodeGraphQt API): `graph.register_node(...)` with unique identifiers.
  - Default flow creation:
    - Programmatically create a graph with:
      - `ContextOutputNode` → `ClipboardNode`
      - `ContextOutputNode` → `FileWriteNode(path: fullcode.txt)`
    - Save this as app bundled JSON (or programmatically generate at first run).
  - Pro gating:
    - In `aicodeprep_gui/pro/__init__.py`, add `get_flow_dock()` (like `get_preview_window`).
    - In `aicodeprep_gui/gui/main_window.py`, in Pro section, add toggle “Enable Flow Studio”:
      - On: create `FlowStudioDock` via `pro.get_flow_dock()` and add to `RightDockWidgetArea`.
      - Off: hide/unparent dock.
    - If not pro: still show the dock but set graph read-only:
      - Disable context menu to add nodes, hide `NodesPaletteWidget`, intercept keyboard shortcuts that add/delete.
- File changes:
  - `aicodeprep_gui/pro/__init__.py`: add `get_flow_dock()` and hold a singleton like preview.
  - `aicodeprep_gui/gui/main_window.py`: add UI toggle, add dock.
- Tests:
  - App opens; Flow Studio dock can be toggled.
  - Default flow visible/read-only in Free mode; editable in Pro mode, no execution yet.
  - No regression in “Generate Context!” flow.

STOP HERE AND ASK ME TO OPEN APP FOR A QUICK TEST-- I tested and worked out some minor bugs, now it works and the default nodes do display, but they are not connected. I can manually connect some of them though and it looks great!

Phase 2 — Flow persistence and default session handling; Import/Export UI

- New/updated:
  - `serializer.py`:
    - `save_flow_to_file(path)` and `load_flow_from_file(path)` wrapping `node_graph.save_session(file_path)` / `load_session(file_path)` or using in-memory dict if preferred.
    - Redact secrets: when exporting, strip API keys (Phase 3 will add provider refs).
  - Flow store:
    - Project-level default path: `.aicodeprep-flow.json` in project root (alongside `.aicodeprep-gui`), if present load it; otherwise load the built-in default.
    - Add global QSettings keys for “FlowStudio.last_import_dir”, etc.
  - Menu:
    - In main “File” or a new “Flow” menu:
      - “Import Flow JSON…”, “Export Flow JSON…”, “Reset to Default Flow”.
  - Read-only enforcement for Free:
    - Graph context menu removed via `node_graph.set_context_menu(...)` or not created.
    - Disable selection deletion/copy/paste; palette hidden.
- Tests:
  - Export/import roundtrip with basic nodes.
  - Free mode cannot modify; Pro mode can.

Phase 3 — Execution engine (sync), and hook it to “Generate Context!”

- New:
  - `aicodeprep_gui/pro/flow/engine.py`:
    - `execute(graph, context={})`:
      - Build DAG: use NodeGraphQt node/port APIs:
        - For each node, gather input connections and create adjacency.
      - Topological sort nodes (raise error if cycle).
      - Each node class implements `run(inputs: dict[str, str], settings: dict) -> dict[str, str]`.
      - Pass along a dict of named outputs (e.g., `{"text": "...", "json": "..."}; start with `text` only).
      - Keep a map `node_id -> outputs`.
      - For I/O nodes:
        - `ContextOutputNode.run`: read file path (default “fullcode.txt”), return `text`.
        - `ClipboardNode.run`: copy inbound `text` to clipboard using Qt; return empty.
        - `FileWriteNode.run`: write inbound `text` to path; return empty.
        - `OutputDisplayNode.run`: emit a signal that the Flow dock can observe to show output (keep it simple: store last run output in node property and refresh UI).
  - Hook in main_window:
    - In `process_selected()`, after existing logic (writing fullcode.txt and clipboard copy), trigger flow execution IF a checkbox “Auto-run Flow after Generate Context!” is enabled (default Off for Free; Pro may enable). This preserves current default behavior even if flow fails.
- Tests:
  - Generate context runs as before.
  - If auto-run enabled, the flow runs and performs the same clipboard/file write via nodes (you’ll see duplicate clipboard writes; keep default flow’s Clipboard/File nodes disabled by default and only used when you enable auto-run).

Phase 4 — Provider manager and Model nodes (OpenAI-compatible generic)

- New:
  - `aicodeprep_gui/pro/flow/providers.py`:
    - `ProviderRegistry`: stores provider entries in `QSettings("aicodeprep-gui","AIProviders")` with:
      - `provider_id` (string key)
      - `display_name`
      - `base_url` (OpenAI-compatible; e.g., `https://api.openai.com/v1`, `https://openrouter.ai/api/v1`, etc.)
      - `api_key_ref` (a key alias stored in `QSettings("aicodeprep-gui","AISecrets")`, not in flow).
    - `SecretsStore`: QSettings for `AISecrets` that maps `alias -> encrypted value` (if you want to encrypt later; for now store plain with clear warning).
    - UI dialog: `ProviderManagerDialog` (basic CRUD). Place under Help or Edit → “Manage AI Providers…”.
  - Node: `ModelNode(BaseNode)`:
    - Inputs: `prompt` (text), optional `context` (text).
    - Outputs: `text` (string), maybe `raw_json`.
    - Properties: `provider_ref`, `model`, `temperature`, `max_tokens`, `headers` (optional), `mode` (chat or completion).
    - Execution:
      - Build OpenAI-compatible chat payload (messages: system(optional), user prompt + context concatenated).
      - POST to `{base_url}/chat/completions`, headers: `Authorization: Bearer <api_key>`, etc.
      - Parse `choices[0].message.content` to `text`.
  - Guardrails:
    - Connection constraints so only `text` ports connect to `prompt/context` ports (see ng docs: Port.add_accept_port_type).
- Tests:
  - Add an OpenRouter provider with a test key; create flow: `ContextOutputNode` -> `ModelNode(GPT-5 on OpenRouter)` -> `OutputDisplayNode`.
  - Run flow: content visible in OutputDisplayNode.

Phase 5 — Gemini 2.5 Pro and GLM-4.5 nodes

- Add adapters:
  - `GeminiNode(BaseNode)`: Inputs: `prompt`, `context`. Properties: API key ref, model (e.g., `gemini-2.0-pro-exp` or 2.5 as appropriate), safety settings; endpoint: `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`.
  - `GLMNode(BaseNode)`: If using native Zhipu API, implement according to GLM-4.5 docs; or simply use OpenRouter’s compat to simplify.
- Both should still output `text`. Warn users when not using OpenAI-compatible path that the provider must be native.
- Tests:
  - Create flows for each provider/model, run, show output.

Phase 6 — UX polish and Property Bin/editor

- Add `NodesPaletteWidget` and `PropertiesBinWidget` (ng.md): show palette to drag nodes and a property editor for selected node (Pro only).
- Context menu customization (docs examples/ex_menu.rst): add “Run from here”, “Disable node”, “Set pipe layout”.
- Pipe style/direction defaults (from docs ex_pipe): set ANGLE to reduce edge overlaps.

Phase 7 — Async, streaming, and retries (optional)

- Convert engine to run async via threads; allow cancel.
- Streaming outputs for OpenAI-compatible endpoints via SSE if provider supports it; update `OutputDisplayNode` live.
- Retry/backoff on HTTP errors.

Data model and JSON schema

- Use NodeGraphQt session save/load for layout and connections.
- Node custom properties:
  - Common: `node_type`, `version`
  - For `ModelNode`: `provider_ref`, `model`, `params` dict (temperature, max_tokens, extra_headers).
  - For `ContextOutputNode`, `path`, `use_latest_generated`.
  - For outputs: no secrets in saved JSON; only provider refs.
- File locations:
  - Project default flow: `.aicodeprep-flow.json` in project root.
  - Import/export: any path; on export redact sensitive fields.
  - Global path if none per project: keep an embedded default flow JSON (packaged as resource), or programmatically build on first open.

Security

- Never serialize API keys in `*.json` exports.
- Store API keys in `QSettings("aicodeprep-gui","AISecrets")`. For Pro later, consider OS keychain.

Detailed Change List

1. pyproject.toml

- Add dependency:
  - NodeGraphQt>=0.6.0 (or latest stable known to support PySide6 via Qt.py)
  - Optionally Qt.py>=1.3.0 if NodeGraphQt requires it.
- Optionally add an extra:
  [project.optional-dependencies]
  flow = ["NodeGraphQt", "Qt.py"]

2. aicodeprep_gui/pro/**init**.py

- Add:
  - `enabled` check already exists.
  - Global singleton: `_flow_dock = None`
  - `def get_flow_dock():` create and return `FlowStudioDock` if pro enabled; else return a read-only dock variant (or None).
- Export helper functions as needed for main window.

3. aicodeprep_gui/pro/flow/flow_dock.py

- Class `FlowStudioDock(QtWidgets.QDockWidget)`:
  - Create `self.graph = NodeGraph()`
  - Register nodes (Phase 1’s I/O nodes)
  - `self.setWidget(self.graph.widget)` (or wrap in a parent with palette/bin panels)
  - Methods: `load_default_flow()`, `import_flow(path)`, `export_flow(path)`
  - A `run()` method that calls `engine.execute(self.graph)`

4. aicodeprep_gui/pro/flow/nodes/base.py

- Define a `BaseExecNode(BaseNode)` with helpers:
  - `get_input_text(name='in')`, `set_output_text(text, name='out')`
  - `run(inputs, settings) -> dict`
- Subclasses implement `run`.

5. aicodeprep_gui/pro/flow/nodes/io_nodes.py

- `ContextOutputNode(BaseExecNode)`:
  - Outputs: `text`
  - Properties: `path` (default “fullcode.txt”), `use_latest_generated` (default True)
- `ClipboardNode(BaseExecNode)`:
  - Inputs: `text`
- `FileWriteNode(BaseExecNode)`:
  - Inputs: `text`
  - Property `path`
- `OutputDisplayNode(BaseExecNode)`:
  - Inputs: `text`
  - Store last result in a node property; Flow dock subscribes to a signal to refresh a side panel or uses PropertiesBin to show “last_result”

6. aicodeprep_gui/pro/flow/serializer.py

- `save_session(file_path)` and `load_session(file_path)` wrappers
- `export_to_json(file_path, redact=True)`: if `redact`, strip provider secrets
- `import_from_json(file_path)`

7. aicodeprep_gui/pro/flow/engine.py

- `execute(graph, run_from_selected=None)`
  - Build adjacency: for each node list outgoing edges to target nodes via their ports
  - Topo-sort
  - For each node call `node.run(inputs, settings)` where `inputs` are dict of input-port-name to value; store outputs
  - Return dict `node_id -> outputs`
- Consider minimal error handling and a small log area in the dock.

8. aicodeprep_gui/pro/flow/providers.py

- `ProviderRegistry` (QSettings-based): CRUD providers (`provider_ref -> data`)
- `SecretsStore` (QSettings-based): CRUD secret values (key alias -> api key)
- `ProviderManagerDialog` (QtWidgets.QDialog) to manage providers and secrets (Pro only).

9. aicodeprep_gui/pro/flow/nodes/model_nodes.py

- `ModelNode(BaseExecNode)`:
  - Ports: in: `prompt`, `context`; out: `text`
  - Properties: `provider_ref`, `model`, `temperature`, `max_tokens`, `headers_json`, `system_prompt`
  - `run`: Build request → POST → parse response
- `GeminiNode(BaseExecNode)`, `GLMNode(BaseExecNode)` (optional provider-specific)
- Connection constraints: `add_accept_port_type` per ng docs to only accept text inputs on the right ports.

10. aicodeprep_gui/gui/main_window.py

- Pro section:
  - Add checkbox “Enable Flow Studio” next to Preview toggles. On enable: create dock (`self.flow_dock = pro.get_flow_dock()`).
  - “Flow” menu: Import, Export, Reset default, Run Flow Now.
- On “Generate Context!”:
  - Keep existing behavior.
  - If a separate “Auto-run Flow after generate” is checked (store in QSettings), call `self.flow_dock.run()` inside a try/except.

11. aicodeprep_gui/gui/settings/preferences.py

- Optionally add `flow_auto_run_enabled` under `[pro]` in `.aicodeprep-gui` (or just QSettings global is fine).
- Store only booleans; do NOT store provider secrets here.

12. Metrics (optional)

- Emit simple events “flow_run_start/finish” count via existing metrics manager.

Default flow definition (programmatic)

- On first-time Flow Studio open:
  - Create nodes:
    - `ctx = ContextOutputNode(name='Context Output', path='fullcode.txt')`
    - `clip = ClipboardNode(name='Clipboard')`
    - `file = FileWriteNode(name='Write fullcode', path='fullcode.txt')`
  - Connect `ctx.text -> clip.text`, `ctx.text -> file.text`
  - Layout auto (`graph.auto_layout_nodes()`)
- Save as in-memory default in dock state; if `.aicodeprep-flow.json` exists, load that instead.
- Free mode: disable editing.

Execution details (Phase 3)

- Inputs/outputs as plain text initially.
- The engine should:
  - For each node, gather each input port’s upstream node’s output string.
  - If multiple inbound connections to the same input port: concatenate with delimiters (simple v1: join with two newlines; later add input aggregator node).
  - Pass a dict: `{'prompt': "…", 'context': "…", 'text': "…"}` depending on port names.
- NodeGraphQt access:
  - Get all nodes: `graph.all_nodes()`
  - Ports: node.inputs(), node.outputs(), and their connections (see docs ex_node.rst, ex_port.rst).
- Don’t block UI: For now run in the UI thread (small flows); add a worker QThread in Phase 7.

Importer/Exporter UX (Phase 2)

- Menu actions:
  - “Flow → Import…”: `QFileDialog.getOpenFileName` (JSON); `load_session(path)`.
  - “Flow → Export…”: `QFileDialog.getSaveFileName`; `save_session(path)`; also call `export_to_json()` to redact.
  - “Flow → Reset to Default”: reload programmed default; confirm dialog.

Provider UX (Phase 4)

- Menu “Edit → Manage AI Providers…”:
  - List providers with name, base URL, model preview, key alias status.
  - Buttons: Add, Edit, Delete.
  - On Add/Edit: let user set `display_name`, `base_url`, `api_key_alias`. Provide a second tab to “Manage Secrets…” to set `alias -> value`.
- In `ModelNode` property bin:
  - `provider_ref` is a drop-down populated from `ProviderRegistry`.
  - `model` is a text box (or drop-down populated from a provider preset list you maintain).
  - `system_prompt`, `temperature`, `max_tokens`, `headers_json` (with validation).

Pro/read-only enforcement

- Free mode limits:
  - Hide node palette and properties bin.
  - Disable `node_graph.context_menu` commands for add/delete.
  - Block drag-n-drop.
  - Intercept keyboard shortcuts for edit operations.

Minimal code scaffolds (snippets)

- Creating the dock and graph:

```python
# aicodeprep_gui/pro/flow/flow_dock.py
from PySide6 import QtWidgets, QtCore
from NodeGraphQt import NodeGraph, NodesPaletteWidget, PropertiesBinWidget

class FlowStudioDock(QtWidgets.QDockWidget):
    def __init__(self, parent=None, read_only=False):
        super().__init__("Flow Studio", parent)
        self.setObjectName("flow_studio_dock")
        self.graph = NodeGraph()
        self.graph_widget = self.graph.widget
        wrapper = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wrapper)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.graph_widget)
        # Optional: add palette/bin to the right
        self.setWidget(wrapper)

        # register nodes here
        # self.graph.register_node(ContextOutputNode)
        # self.graph.register_node(ClipboardNode)
        # self.graph.register_node(FileWriteNode)
        # self.graph.register_node(OutputDisplayNode)

        # load default or project flow
        self.load_default_flow()

        if read_only:
            self._apply_read_only()

    def load_default_flow(self):
        # try load .aicodeprep-flow.json; else build programmatically
        pass

    def run(self):
        # call engine.execute(self.graph)
        pass

    def _apply_read_only(self):
        # disable palette, context menus, editing shortcuts
        pass
```

- Model node execution (OpenAI-compatible):

```python
# aicodeprep_gui/pro/flow/nodes/model_nodes.py
import json
import requests
from NodeGraphQt import BaseNode

class ModelNode(BaseNode):
    __identifier__ = 'aicp.flow'
    NODE_NAME = 'Model (OpenAI-compatible)'

    def __init__(self):
        super().__init__()
        self.add_input('prompt')
        self.add_input('context', multi_input=True)
        self.add_output('text')
        # properties
        self.create_property('provider_ref', '')
        self.create_property('model', 'gpt-4o-mini')
        self.create_property('temperature', 0.2)
        self.create_property('max_tokens', 4096)
        self.create_property('headers_json', '')

    def run(self, inputs, settings):
        prompt = (inputs.get('prompt') or '') + "\n\n" + (inputs.get('context') or '')
        provider = settings['provider_registry'].get(self.get_property('provider_ref'))
        api_key = settings['secrets_store'].get(provider.api_key_alias)
        url = provider.base_url.rstrip('/') + '/chat/completions'
        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        extra = self.get_property('headers_json').strip()
        if extra:
            try: headers.update(json.loads(extra))
            except Exception: pass

        payload = {
            'model': self.get_property('model'),
            'temperature': float(self.get_property('temperature')),
            'max_tokens': int(self.get_property('max_tokens')),
            'messages': [{'role':'user', 'content': prompt}]
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        txt = data['choices'][0]['message']['content']
        return {'text': txt}
```

QA test matrix

- Phase 1:
  - Windows/macOS/Linux start app, toggle Flow Studio, default flow shows.
- Phase 2:
  - Import/export flow JSON. Free mode cannot change nodes; Pro can.
- Phase 3:
  - After Generate Context!, engine executes (when enabled), clipboard/file nodes behave correctly.
- Phase 4:
  - Create a provider (OpenRouter) and a Model node, run, see output in `OutputDisplayNode`.
- Phase 5:
  - Add Gemini/GLM nodes and test with real keys (or mock).
- Regression:
  - Tree selection, token counter, preview dock, Pro toggles unaffected.

Rollout plan

- Ship Phase 1–3 behind a Pro-feature toggle (editing requires Pro). Default behavior remains unchanged for all users.
- After stabilization, add Phase 4 providers and Phase 5 nodes.
- Document how to use Flow Studio in Help/Links.

File-by-file edits (summary)

- pyproject.toml: add dependencies (NodeGraphQt [+ Qt.py])
- aicodeprep_gui/pro/**init**.py: `get_flow_dock()`
- aicodeprep_gui/pro/flow/flow_dock.py: new dock implementation
- aicodeprep_gui/pro/flow/engine.py: flow executor
- aicodeprep_gui/pro/flow/nodes/base.py, io_nodes.py, model_nodes.py: node classes
- aicodeprep_gui/pro/flow/providers.py: provider registry + secrets
- aicodeprep_gui/pro/flow/serializer.py: load/save, redact
- aicodeprep_gui/gui/main_window.py:
  - Add Flow toggle in Pro features area
  - Flow menu: Import/Export/Reset/Run
  - Hook optional auto-run to `process_selected()`
- aicodeprep_gui/gui/settings/preferences.py or QSettings: store auto-run and panel visibility

Notes from ng.md to apply

- Use `NodeGraph.widget` for embedding in dock.
- Provide `NodesPaletteWidget` and `PropertiesBinWidget` (docs: builtin_widgets) for Pro.
- Use `BaseNode.add_input`, `add_output`, `set_property`, `add_custom_widget` for property UIs.
- Use `graph.register_node` to register custom node classes.
- Use `graph.save_session`, `graph.load_session` for JSON.
- Use connection constraints via `Port.add_accept_port_type`.

Open items to decide

- Whether to include palette and property bin in Phase 1 or wait for Phase 6 (recommended: delay to Phase 6).
- Whether to store `.aicodeprep-flow.json` per project or always use QSettings/global by default (recommended: per project if present, else global default).
- Whether to implement minimal encryption for API keys in QSettings (later).

With this plan, you can implement step-by-step and verify after each phase that the app still works as today, while gradually enabling the Flow Studio for Pro users.
