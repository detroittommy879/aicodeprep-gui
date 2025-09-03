Excellent! This is a fantastic and ambitious feature that will significantly enhance the capabilities of `aicodeprep-gui`. Analyzing your application's structure and the `NodeGraphQt` documentation reveals a clear path forward.

Here is a comprehensive Feature Add-on Requirements Document that breaks down the entire process into manageable, testable phases. This plan is designed to be detailed enough for an AI assistant to help generate code for each sub-task.

---

## Feature Requirements Document: AI Workflow Editor

### 1. Feature Overview

**Title:** AI Workflow Editor (Node-Based Processing)

**Objective:** To integrate a visual, node-based workflow editor into `aicodeprep-gui`. This feature will allow users to construct and execute complex processing chains, routing the application's generated code context through various AI models, text processors, and output steps. This transforms the app from a single-purpose tool into a versatile multi-AI orchestration platform.

**Target Audience:**

- **All Users:** Will view a new "Workflow" panel that visualizes the app's default behavior in a read-only mode. This enhances transparency and introduces the feature.
- **Pro Users:** Will unlock the full editing capabilities, including creating, modifying, saving, and loading custom workflows with advanced nodes like API endpoints.

### 2. Core Requirements & User Stories

| ID      | Requirement                    | User Story                                                                                                                                                                 |
| :------ | :----------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **FR1** | Dockable Node Editor UI        | As a user, I want a new dockable window for the workflow editor so I can arrange my workspace and view the processing logic alongside the file tree.                       |
| **FR2** | Default Workflow Visualization | As a new user, I want to see a visual representation of the default "Generate Context" action so I can understand what the app does and discover the new workflow feature. |
| **FR3** | Pro: Workflow Editing          | As a Pro user, I want to add, remove, move, and connect nodes on the canvas so I can create custom processing logic tailored to my needs.                                  |
| **FR4** | Node Library                   | As a Pro user, I want a palette of available nodes (Inputs, AI Models, Outputs) that I can drag onto the canvas to build my workflow.                                      |
| **FR5** | Advanced Node Functionality    | As a Pro user, I want to configure AI model nodes with my own API keys, endpoints, and custom prompts to query different services.                                         |
| **FR6** | Pro: Workflow Persistence      | As a Pro user, I want to save my complex workflows to a file and load them later, so I don't have to rebuild them every time.                                              |
| **FR7** | Workflow Execution Engine      | As a user, when I click the "Generate Context" button, I want the currently configured workflow to execute, processing the data as I have visually defined.                |

---

### 3. Technical Implementation Plan

The project will be implemented in five distinct phases. Each phase concludes with a set of testable criteria to ensure stability and functionality before proceeding.

#### **Phase 0: Setup and Dependencies**

**Objective:** Prepare the project environment by adding the new library and creating the necessary module structure.

1.  **Add Dependency:**

    - **File:** `pyproject.toml`
    - **Action:** Add `"NodeGraphQt"` to the `[project.dependencies]` list.
    - **Command:** Run `pip install NodeGraphQt` in your development environment to add the dependency.

2.  **Create New Module for Workflow:**
    - **Action:** Create a new sub-package: `aicodeprep_gui/gui/workflow/`
    - **Files to Create:**
      - `aicodeprep_gui/gui/workflow/__init__.py`
      - `aicodeprep_gui/gui/workflow/workflow_editor.py` (For the main dock widget and `NodeGraph` setup).
      - `aicodeprep_gui/gui/workflow/nodes.py` (For defining all custom `BaseNode` subclasses).
      - `aicodeprep_gui/gui/workflow/workflow_manager.py` (For handling execution, saving, and loading logic).

---

#### **Phase 1: Basic Dockable Node Editor UI**

**Objective:** Integrate a blank, dockable `NodeGraphQt` widget into the main window. This will be the foundation for all subsequent features.

1.  **Create the Workflow Editor Widget:**

    - **File:** `aicodeprep_gui/gui/workflow/workflow_editor.py`
    - **Details:**
      - Import `QtWidgets`, `NodeGraph`, and `NodesPaletteWidget`.
      - Create a class `WorkflowEditorDock(QtWidgets.QDockWidget)`.
      - In its `__init__`, instantiate `self.graph = NodeGraph()`.
      - Create a `NodesPaletteWidget`, link it to the graph, and add it and `self.graph.widget` to a layout.
      - Set this layout as the dock widget's main widget.

2.  **Integrate Dock Widget into `main_window.py`:**
    - **File:** `aicodeprep_gui/gui/main_window.py`
    - **Details:**
      - Import `WorkflowEditorDock` from the new module.
      - In `FileSelectionGUI.__init__`, instantiate `self.workflow_dock = WorkflowEditorDock(...)` and add it using `self.addDockWidget()`.
      - Add a new `QCheckBox` "Show AI Workflow" to the "Options" group box (visible to everyone).
      - Connect its `toggled` signal to `self.workflow_dock.setVisible`. The dock should be hidden by default.

**▶️ Acceptance Criteria for Phase 1:**

- The application runs without errors for both free and Pro users.
- A "Show AI Workflow" checkbox is visible in the "Options" panel.
- Toggling the checkbox shows/hides a dockable window containing an empty node canvas and a node palette.

---

#### **Phase 2: Implementing the Default Workflow (Read-Only View)**

**Objective:** Create and display the default workflow that mimics the app's current functionality. This view will be read-only for non-Pro users.

1.  **Define Default Nodes:**

    - **File:** `aicodeprep_gui/gui/workflow/nodes.py`
    - **Details:**
      - Create `ContextNode(BaseNode)` with `__identifier__ = 'aicp.input.context'` and one output port named `"Context Text"`.
      - Create `WriteFileNode(BaseNode)` with `__identifier__ = 'aicp.output.file'` and one input port named `"Text"`. Set its `NODE_NAME` to `"Write to fullcode.txt"`.
      - Create `ClipboardNode(BaseNode)` with `__identifier__ = 'aicp.output.clipboard'` and one input port named `"Text"`. Set its `NODE_NAME` to `"Copy to Clipboard"`.

2.  **Display and Lock the Default Workflow:**

    - **File:** `aicodeprep_gui/gui/workflow/workflow_editor.py`
    - **Details:**
      - In `WorkflowEditorDock.__init__`, add an `is_pro` parameter.
      - Register the new node classes with `self.graph.register_nodes()`.
      - Create a method `_create_default_workflow()` that clears the graph, creates one instance of each default node, and connects them: `ContextNode`'s output should connect to both `WriteFileNode` and `ClipboardNode` inputs. Use `node.set_pos()` to arrange them neatly.
      - Call this method in `__init__`.
      - If `is_pro` is `False`, disable interaction with `self.graph.set_disabled(True)` and hide the node palette.

3.  **Modify Main Window Integration:**
    - **File:** `aicodeprep_gui/gui/main_window.py`
    - **Details:** When creating `WorkflowEditorDock`, pass the pro status: `self.workflow_dock = WorkflowEditorDock(is_pro=pro.enabled)`.

**▶️ Acceptance Criteria for Phase 2:**

- When a free user shows the workflow window, they see the three default nodes connected correctly.
- The graph is locked for free users (nodes cannot be moved, no new nodes can be added).
- When a Pro user shows the window, the graph is fully interactive.

---

#### **Phase 3: Defining Advanced Pro Nodes**

**Objective:** Create the classes for AI model nodes and other utility nodes, making them available in the palette for Pro users.

1.  **Define AI Model & Output Nodes:**

    - **File:** `aicodeprep_gui/gui/workflow/nodes.py`
    - **Details:**
      - **Base AI Node:** Create `AIModelNode(BaseNode)` to handle common logic. In its `__init__`, use `self.add_text_input()` for API Key/Endpoint fields and a custom widget for a multi-line prompt text area. It should have `"Input Text"` and `"Prompt"` inputs, and a `"Response Text"` output.
      - **Specific AI Nodes:** Create subclasses like `GPT5Node(AIModelNode)`, `Gemini25ProNode(AIModelNode)`, etc. They should inherit from `AIModelNode` and set their specific `NODE_NAME` and default endpoint URL.
      - **Custom API Node:** Create a generic `CustomOpenAPINode(AIModelNode)` for user-defined OpenAI-compatible endpoints.
      - **Output Nodes:** Create `DisplayTextNode(BaseNode)` with one input.

2.  **Register New Nodes for Pro Users:**
    - **File:** `aicodeprep_gui/gui/workflow/workflow_editor.py`
    - **Details:** In `WorkflowEditorDock.__init__`, if `is_pro` is true, register all the new AI and output node classes. Use the `nodes_palette.set_category_label()` method to organize them cleanly in the UI.

**▶️ Acceptance Criteria for Phase 3:**

- As a Pro user, the Node Palette shows new categories for "AI Models" and "Outputs".
- All new nodes can be dragged onto the canvas.
- AI Model nodes contain configurable properties for API credentials and prompts.

---

#### **Phase 4: Implementing the Workflow Execution Engine**

**Objective:** Wire up the "GENERATE CONTEXT!" button to trigger the execution of the visual workflow.

1.  **Create the Workflow Manager:**

    - **File:** `aicodeprep_gui/gui/workflow/workflow_manager.py`
    - **Details:**
      - Create a `WorkflowManager` class that takes the `NodeGraph` instance.
      - Create an `execute_workflow(context_text: str)` method. This method will:
        1.  Find the `ContextNode` in the graph.
        2.  Create a dictionary or custom object to hold its output value (`{'Context Text': context_text}`).
        3.  Begin a topological traversal of the graph, executing each node as its inputs become available.
        4.  Execution should handle async operations for API calls using `QNetworkAccessManager` to prevent UI freezes.

2.  **Implement Node Execution Logic:**

    - **File:** `aicodeprep_gui/gui/workflow/nodes.py`
    - **Details:**
      - Add a custom `execute(self, input_data: dict)` method to each node class.
      - **`ContextNode`**: Its logic is handled by the manager, it's the entry point.
      - **`WriteFileNode.execute()`**: Takes `input_data['Text']` and writes it to `fullcode.txt`.
      - **`ClipboardNode.execute()`**: Takes `input_data['Text']` and copies it to the system clipboard.
      - **`AIModelNode.execute()`**: This will be the most complex. It will:
        a. Read API key, endpoint, and prompt from its widgets.
        b. Construct the API request payload using the input data and prompt.
        c. Make an asynchronous network request.
        d. When the response is received, emit a custom signal with the result to be picked up by the `WorkflowManager` to continue the graph traversal.

3.  **Trigger Execution from Main Window:**
    - **File:** `aicodeprep_gui/gui/main_window.py`
    - **Action:** In `FileSelectionGUI.process_selected()`, replace the direct call to `process_files()` with a call to your new `workflow_manager.execute_workflow()`, passing in the generated context string.

**▶️ Acceptance Criteria for Phase 4:**

- Pressing "GENERATE CONTEXT!" executes the default workflow correctly (writes file, copies to clipboard).
- A Pro user can build a custom workflow (e.g., `Context -> AI Model -> Display Text`) and it executes successfully, showing the AI response.
- The UI remains responsive during network requests to AI models.

---

#### **Phase 5: Workflow Persistence (Pro-only)**

**Objective:** Allow Pro users to save and load their custom workflows as JSON files.

1.  **Implement Save/Load in Manager:**

    - **File:** `aicodeprep_gui/gui/workflow/workflow_manager.py`
    - **Details:**
      - Create a `save_workflow()` method that opens a `QFileDialog` and then calls `self.graph.save_session(filepath)`.
      - Create a `load_workflow()` method that opens a `QFileDialog` and then calls `self.graph.load_session(filepath)`.
      - Create `reset_workflow()` that calls the `_create_default_workflow` method on the editor dock.
      - Create `new_workflow()` that calls `self.graph.clear_session()`.

2.  **Add Menu Items for Workflow Management:**
    - **File:** `aicodeprep_gui/gui/main_window.py`
    - **Details:**
      - In the `File` menu, add a separator and a new submenu called "AI Workflow".
      - If `pro.enabled`, populate this submenu with actions: "New Workflow", "Import Workflow...", "Export Workflow...", and "Reset to Default".
      - Connect these actions to the corresponding methods in the `WorkflowManager`.

**▶️ Acceptance Criteria for Phase 5:**

- As a Pro user, I can create a custom workflow and save it to a JSON file.
- I can clear the canvas with "New Workflow".
- I can load a saved workflow from a JSON file, and it is restored perfectly.
- I can always return to the default setup using "Reset to Default".
