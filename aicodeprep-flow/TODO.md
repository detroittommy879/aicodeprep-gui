# aicodeprep-flow Project TODO List

- [ ] Analyze requirements and confirm extraction scope
- [ ] Scaffold new project directory structure (`src/`, `data/`, etc.)
- [ ] Create `pyproject.toml` with combined dependencies
- [ ] Create initial `README.md` and `mcp_config.json`
- [ ] Copy `aicodeprep_gui/pro/flow/` → `src/aicodeprep_flow/flow/`
- [ ] Copy `aicodeprep_gui/pro/llm/` → `src/aicodeprep_flow/llm/`
- [ ] Copy `aicodeprep_gui/config.py` → `src/aicodeprep_flow/config.py`
- [ ] Copy `aicodeprep_gui/apptheme.py` → `src/aicodeprep_flow/apptheme.py`
- [ ] Copy `aicodeprep_gui/data/flow.json` → `src/aicodeprep_flow/data/flow.json`
- [ ] Copy `aicodeprep_gui/data/flow_studio_help.html` → `src/aicodeprep_flow/data/flow_studio_help.html`
- [ ] Adapt all imports in copied files to new package structure
- [ ] Update `config.py` for `.aicodeprep-flow` config directory and user messages
- [ ] Remove "Pro" mode and licensing logic from `flow/flow_dock.py`
- [ ] Create `src/aicodeprep_flow/main_window.py` for the new GUI
- [ ] Create `src/aicodeprep_flow/main.py` as the CLI entry point
- [ ] Create `src/aicodeprep_flow/mcp/server.py` for MCP server logic
- [ ] Test GUI: create, edit, save, load, and run flows
- [ ] Test MCP server: run headless, verify `execute_flow` tool
- [ ] Finalize documentation and polish for release

......

Task Completed

All code migration, adaptation, and new file implementations for the standalone `aicodeprep-flow` application are complete. The project is ready for testing:

- To launch the GUI editor:

  ```javascript
  python -m aicodeprep_flow.main
  ```

- To run the MCP server (headless):

  ```javascript
  python -m aicodeprep_flow.main --mcp
  ```

Verify that the GUI launches and flows can be created/edited, and that the MCP server responds to `execute_flow` requests as expected.
