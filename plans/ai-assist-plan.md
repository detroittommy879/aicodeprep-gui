## Plan: AI Assist — Pro Prompt Rewriter & Smart File Selector

Add two Pro-gated AI features inside a new `pro/ai_assist/` package: (1) **AI Rewrite Prompt** rewrites the user's prompt for better AI responses, (2) **AI Smart Select** uses the prompt + directory listing (paths, sizes, dates) to auto-check relevant files. Both use OpenAI-compatible endpoints (default `http://localhost:59999/v1`). A "Waiting for AI..." busy dialog shows during requests. Endpoints/models stored in `~/.aicodeprep-gui/ai-endpoints.toml`. Smart Select and Rewrite are greyed out when Pro is not enabled.

**Phases (6 phases)**

1. **Phase 1: AI Client — `pro/ai_assist/ai_client.py`**
   - **Objective:** Create a standalone OpenAI-compatible HTTP client with automatic retries (3 attempts, exponential backoff), model listing, and basic chat completion. Uses `requests`. Lives in `pro/ai_assist/`.
   - **Files/Functions to Create:**
     - `aicodeprep_gui/pro/ai_assist/__init__.py`
     - `aicodeprep_gui/pro/ai_assist/ai_client.py` — `AIClient` class with `chat()`, `list_models()`, `_request_with_retry()`
   - **Tests to Write:**
     - `test_ai_client_chat_success`, `test_ai_client_chat_retry_on_failure`, `test_ai_client_list_models`, `test_ai_client_timeout_handling`

2. **Phase 2: Endpoint Config — `pro/ai_assist/endpoint_config.py`**
   - **Objective:** TOML-based config at `~/.aicodeprep-gui/ai-endpoints.toml` storing endpoints and selected model. Default: `http://localhost:59999/v1`.
   - **Files/Functions to Create:**
     - `aicodeprep_gui/pro/ai_assist/endpoint_config.py` — `load_endpoints()`, `save_endpoints()`, `get_active_endpoint()`, `set_active_model()`, `add_endpoint()`, `remove_endpoint()`
   - **Tests to Write:**
     - `test_endpoint_default_creation`, `test_endpoint_load_save_roundtrip`, `test_endpoint_add_remove`

3. **Phase 3: QThread Workers — `gui/handlers/ai_workers.py`**
   - **Objective:** Qt worker objects for non-blocking AI operations: `PromptRewriteWorker` and `SmartSelectWorker`. SmartSelectWorker builds XML-tagged prompt with directory listing and parses file paths from LLM response.
   - **Files/Functions to Create:**
     - `aicodeprep_gui/gui/handlers/ai_workers.py` — `PromptRewriteWorker`, `SmartSelectWorker`
   - **Tests to Write:**
     - `test_rewrite_worker_emits_finished`, `test_smart_select_worker_parse_xml_response`, `test_smart_select_worker_parse_markdown_response`, `test_smart_select_build_prompt`

4. **Phase 4: Tree Widget — `check_files_by_paths()` method**
   - **Objective:** Add method to `FileTreeManager` that deselects all files then checks only specified file paths.
   - **Files/Functions to Modify:**
     - `aicodeprep_gui/gui/components/tree_widget.py` — Add `check_files_by_paths()`
   - **Tests to Write:**
     - `test_check_files_by_paths_selects_correct`, `test_check_files_by_paths_deselects_others`

5. **Phase 5: UI — Buttons, Model Dropdown, Busy Dialog**
   - **Objective:** Add AI Assist UI to prompt area: buttons, model dropdown, gear button, busy dialog. Grey out when not Pro. Wire to workers.
   - **Files/Functions to Modify:**
     - `aicodeprep_gui/gui/main_window.py` — Add `_setup_ai_assist_ui()`, `_on_ai_rewrite_clicked()`, `_on_ai_smart_select_clicked()`, etc.
   - **Tests to Write:**
     - `test_ai_buttons_exist_and_greyed_without_pro`, `test_ai_model_combo_exists`

6. **Phase 6: Endpoint Settings Dialog**
   - **Objective:** QDialog for managing AI endpoints. Opened via gear button.
   - **Files/Functions to Create:**
     - `aicodeprep_gui/gui/components/ai_settings_dialog.py` — `AIEndpointSettingsDialog`
   - **Tests to Write:**
     - `test_ai_settings_dialog_opens`, `test_ai_settings_add_endpoint`, `test_ai_settings_remove_endpoint`

**Resolved Decisions**

1. Smart Select replaces current selection (deselect all, then check suggested)
2. Directory listing includes paths + file sizes + dates
3. Show "Waiting for AI..." QProgressDialog (no streaming)
4. Rewrite replaces prompt directly, Ctrl+Z to undo
5. Both features are Pro-only, greyed out for free users
6. All new code lives in `pro/ai_assist/` package
