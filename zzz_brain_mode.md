# 🧠 Brain Mode Development Plan

_A modular, plugin-style approach for premium AI orchestration_

---

## 📁 Project Structure

```
aicodeprep_gui/
├── pro/                          # Premium features (plugin-style)
│   ├── __init__.py              # Plugin loader & license check
│   ├── brain_mode/
│   │   ├── __init__.py          # Brain mode main controller
│   │   ├── dock_manager.py      # Right dockable window
│   │   ├── parts_panel.py       # Left vertical draggable parts
│   │   ├── flow_canvas.py       # Central flowchart area
│   │   └── nodes/
│   │       ├── __init__.py
│   │       ├── base_node.py     # Abstract node class
│   │       ├── model_nodes.py   # AI model blocks
│   │       └── context_node.py  # Context block node
│   └── license/
│       └── validator.py         # Simple --pro flag checker
├── gui.py                       # Main UI (modified for plugin hooks)
└── main.py                      # Command-line --pro flag
```

(can we modify or make sure the structure can accomodate having provider/model? so i can count the exact tokens used by certain providers.. like..
OpenAI/
-o3
-o4-mini
Openrouter/
-modelname1
-modelname2
Gemini/
2.5-Pro
2.5-Flash

I am not sure how it should be organized with the folders or files can you suggest something? I would keep track of things like Gemini tokens or time limits, and OpenAI, but also I want these model blocks/squares to be able to have 2nd, 3rd, 4th options for models if 1st (or other) fails. like fall back models.
Want to keep track of token use just because OpenAI and google gemini give away a certain amount per day or per time period. I am not sure how to organize this..any ideas?)

---

## 🎯 Command-Line Flag

- **Flag**: `--pro`
- **Effect**: Activates premium features without real license validation
- **Usage**: `aicp --pro` or `aicodeprep-gui --pro`

---

## 🖥️ UI Layout (when Brain Mode active)

```
┌─────────────────────────────────────────────────────────┐
│  Main UI (existing)  │  Parts Panel │  Brain Mode Dock │
│                      │  (left)      │  (right)         │
│                      │              │                  │
│  [Tree/File list]    │  [Parts]     │  [Flowchart]     │
│                      │  • Model A   │  • Drag nodes    │
│                      │  • Model B   │  • Connect       │
│                      │  • Context   │  • Execute       │
└─────────────────────────────────────────────────────────┘
(this could be modified a little bit so blocks can be edited to include fallback models from any provider) or like a generic 'model block'
I want the user to have control so they can choose any api provider/URL that is openai compatible (but also google gemini's apis) so they could use OpenAI
for one block to use o3 but in a different block they can choose o3 with openrouter - this lets people get the max free credits from various places)
```

---

## 🎨 Styling Integration

- **Inherits** all existing dark/light mode colors
- **Uses** `apptheme.py` utilities for consistency
- **Files**:
  - `pro/brain_mode/styles.py` → Theme-aware QSS generators
  - Reuses checkbox styles, icons, and color palettes

---

## 🔌 Plugin Loading Logic

### 1. **Entry Point** (`pro/__init__.py`)

```python
def is_pro_enabled():
    """Check --pro flag via QSettings or env var"""
    return "--pro" in sys.argv

def load_brain_mode():
    """Import only if pro enabled and folder exists"""
    if not is_pro_enabled():
        return None
    try:
        from .brain_mode import BrainModeController
        return BrainModeController()
    except ImportError:
        return None
```

### 2. **GUI Hooks** (`gui.py`)

```python
# After premium_group_box creation
if pro_loader.load_brain_mode():
    self.brain_mode = pro_loader.load_brain_mode()
    self.brain_mode.attach_to_gui(self)
else:
    # Grey out the checkbox
    brain_mode_checkbox.setEnabled(False)
```

---

## 🧩 Parts Panel (Left)

### 📋 Drag Sources

- **Model Blocks**
  - "OpenAI o3"
  - "OpenAI o4-mini"
  - "Kimi AI K2"
  - "Gemini 2.5 Pro"
  - "GPT-4.1-mini"
- **Utility Blocks**
  - "Context Block" (pre-filled)
  - "Router" (future)
  - "Aggregator" (future)

(I think, there should be a expand/collapsable menu or options panel to type in api endpoints and api keys, and it could fetch the model list from those and make
them available. So each endpoint could have a provider name, and a list of models to choose from which it would get live. Also each api provider, maybe we
can start with openai compatible and gemini, but allow custom code for the future ones that might have slightly different api rules/ways to use them? keep in mind future add ons of newer non-openai compatible api endpoints - how can this be organized with files/folders?)

### 🖱️ Interaction

- **Drag**: `QDrag` with `application/x-brain-node` mime type
- **Visual**: Color-coded by type (models = blue, context = green)
- **Styling**: Uses same font/size as main UI

---

## 🧠 Flow Canvas (Right Dock)

### 🎨 Visual Design

- **Background**: Theme-aware (dark `#2b2b2b`, light `#ffffff`)
- **Grid**: Subtle dot grid for alignment
- **Nodes**: Rounded rectangles with consistent padding

### 🔗 Node System

```python
class BaseNode(QGraphicsItem):
    """All draggable nodes inherit from this"""
    - Unique ID
    - Input/output ports
    - Serialize/deserialize for save/load
    - Theme-aware paint()
```

### ⚙️ Execution Engine (MVP)

- **Synchronous** for now
  (but maybe we should have it async/parallel when the models are processing? with visual indicators of activity or waiting)

- **Context**: Takes the existing "GENERATE CONTEXT!" output
- **Output**: Concatenated responses (no smart aggregation yet but this could be a block, that is labeled "Combined" and there could be a block called PrintToWindow just a window that shows the text)

---

## 🛠️ Development Phases

### **Phase 0: Foundation** _(Week 1)_

- [ ] Create `pro/` directory with plugin loader
- [ ] Add `--pro` flag parsing in `main.py`
- [ ] Stub greyed-out checkbox in premium panel

### **Phase 1: UI Shell** _(Week 1-2)_

- [ ] `dock_manager.py`: Right dockable window
- [ ] `parts_panel.py`: Left vertical draggable list
- [ ] Theme integration with existing styles

### **Phase 2: Interactivity** _(Week 2-3)_

- [ ] Drag-and-drop from parts to canvas
- [ ] Basic node rendering on canvas
- [ ] Save/restore flow state (JSON)

### **Phase 3: Execution** _(Week 3-4)_

- [ ] Connect nodes to generate context
- [ ] Parallel model calls stub
- [ ] Display results in canvas

---

## 📄 Configuration Files

### `pro/brain_mode/config.json`

```json
{
  "models": [
    { "name": "OpenAI o3", "color": "#10a37f" },
    { "name": "Kimi K2", "color": "#00a6fb" }
  ],
  "canvas": {
    "grid_size": 20,
    "snap_to_grid": true
  }
}
(i want to have different model providers so i can track tokens by provider so how can i better handle the models stuff?)
```

---

## 🔄 Future Extensibility

- **Node Marketplace**: Users can drop `.py` files into `pro/nodes/`
- **License Upgrade**: Replace `--pro` with real license server
- **Themes**: `pro/themes/` folder for custom node styles

---

## ✅ MVP Success Criteria

1. Launch with `aicp --pro` → Brain Mode checkbox becomes active
2. Toggle checkbox → Shows 3-panel layout
3. Drag "Context Block" + "Model A" → Canvas
4. Click "Execute" → Uses existing context generation
5. All styling matches dark/light mode

---

## 📝 Next Steps

1. Create `pro/` directory structure
2. Implement `--pro` flag in `main.py`
3. Add plugin loader hooks in `gui.py`
4. Build basic 3-panel layout
5. Test with existing theme switching

Ready to start Phase 0?
