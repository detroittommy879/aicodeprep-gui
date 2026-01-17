# Internationalization & Accessibility Implementation Plan

## Agent Mission Statement

Implement comprehensive internationalization (i18n) and accessibility (a11y) features for aicodeprep-gui, working iteratively with self-verification through UI screenshots until the application is fully accessible and multilingual.

## Important Setup Instructions

**ALWAYS use `uv` for Python package management:**

- Run commands with: `uv run <command>`
- Install packages with: `uv pip install <package>`
- Run tests with: `uv run pytest`
- Run app with: `uv run aicodeprep-gui`

**Work on the feature branch:**

- Branch name: `feature/i18n-accessibility`
- All work should be committed to this branch
- Do NOT commit directly to `main`

---

## Phase 0: Setup Screenshot Capability for AI Feedback

### Goal

Enable the AI agent to capture and analyze screenshots of the running application to verify UI changes.

### Implementation Steps

1. **Create Screenshot Utility Module**

   - File: `aicodeprep_gui/utils/screenshot_helper.py`
   - Implement function to capture main window screenshot
   - Save to temporary directory with timestamp
   - Return path for AI to read/analyze

   ```python
   # Key functionality needed:
   - capture_window_screenshot(window) -> str (file path)
   - capture_widget_screenshot(widget) -> str (file path)
   - compare_screenshots(path1, path2) -> dict (difference metrics)
   ```

2. **Add Screenshot Test Helper**

   - File: `tests/test_helpers/screenshot_tester.py`
   - Create helper class for screenshot-based testing
   - Include methods to:
     - Launch app in test mode
     - Capture specific UI states
     - Verify text rendering (for i18n testing)
     - Check contrast ratios (for a11y testing)

3. **Create Debug Menu for Manual Verification**

   - Add "Debug" menu to main window (dev mode only)
   - Add "Take Screenshot" action
   - Add "Current Language: XX" display
   - Add "Accessibility Check" action

4. **Write Initial Screenshot Tests**

   ```python
   # tests/test_screenshot_baseline.py
   def test_capture_main_window():
       """Verify screenshot system works"""

   def test_ui_renders_without_errors():
       """Baseline test - current UI"""
   ```

### Verification

- Run app, take screenshot manually via debug menu
- Verify screenshot saved correctly
- Tests pass showing screenshot system functional

---

## Phase 1: Internationalization Infrastructure

### Goal

Set up the framework for translating all UI text into multiple languages.

### Technical Approach: Qt Linguist System

1. **Install Required Tools**

   - Add to dependencies: No extra packages needed (Qt includes linguist tools)
   - Tools available: `pylupdate6`, `lrelease`

2. **Create Translation Module**

   - File: `aicodeprep_gui/i18n/__init__.py`
   - File: `aicodeprep_gui/i18n/translator.py`

   Key functions:

   ```python
   class TranslationManager:
       def __init__(self, app: QApplication)
       def detect_system_language() -> str  # Auto-detect from OS
       def get_available_languages() -> List[tuple[str, str]]  # code, name
       def is_language_available(lang_code: str) -> bool
       def download_language_if_needed(lang_code: str) -> bool  # On-demand loading
       def set_language(lang_code: str) -> bool
       def get_current_language() -> str
       def retranslate_ui()  # Signal to all windows to retranslate
   ```

3. **Mark All Translatable Strings**

   - Search entire codebase for user-facing strings
   - Replace hardcoded strings with `self.tr("English Text")`
   - For strings not in a QObject context, use `QCoreApplication.translate()`

   Priority areas:

   - Menu items (File, Edit, Flow, Help)
   - Button labels
   - Dialog titles and messages
   - Status messages
   - Tooltips
   - Preset button names
   - Error messages
   - Info labels

4. **Create Translation Files Structure**

   **Bundled Languages (included in package):**

   ```
   aicodeprep_gui/i18n/translations/
   ├── aicodeprep_gui_en.ts    (English - source, always bundled)
   ├── aicodeprep_gui_es.ts    (Spanish - common)
   ├── aicodeprep_gui_zh_CN.ts (Chinese Simplified - common)
   └── aicodeprep_gui_fr.ts    (French - common)
   ```

   **On-Demand Languages (downloaded when selected):**

   - Store at: `~/.aicodeprep-gui/translations/` or `%APPDATA%/aicodeprep-gui/translations/`
   - Available: German, Japanese, Korean, Arabic, Hebrew, Russian, Portuguese, etc.
   - Downloaded from GitHub releases or CDN when user selects them

   **System Language Detection:**

   - Use `QLocale.system().name()` to detect OS language
   - Auto-load if bundled, offer to download if not
   - Fall back to English if detection fails

5. **Generate Initial Translation Files**

   ```bash
   # Use the provided script (already uses uv internally)
   uv run python scripts/generate_translations.py

   # This script handles:
   # - Extracting strings with lupdate
   # - Creating/updating .ts files for bundled languages (en, es, zh_CN, fr)
   # - Compiling .qm files with lrelease
   ```

6. **Implement System Language Detection**

   - On first launch, detect system language using `QLocale.system()`
   - If system language is bundled, use it automatically
   - If not bundled, offer to download or use English
   - Save language preference to QSettings

7. **Add Language Selection UI**

   - Add to Settings/Preferences menu: "Language..."
   - Create language selection dialog
   - Show bundled languages (instantly available)
   - Show downloadable languages (with download indicator)
   - If user selects non-bundled language, download it first
   - Progress indicator for download
   - Save preference to QSettings
   - Restart notification (or dynamic retranslation)

8. **Implement Dynamic Retranslation**
   - Add signal/slot mechanism for language changes
   - Each window/dialog implements `changeEvent(QEvent)` handler
   - Detect `QEvent.LanguageChange`
   - Call `retranslateUi()` method

### Testing Strategy

Write tests FIRST (TDD approach):

```python
# tests/test_i18n.py
# Run with: uv run pytest tests/test_i18n.py -v

def test_translation_manager_initializes():
    """Translation manager loads without errors"""
    assert False  # Write failing test first

def test_get_available_languages():
    """Should return list of supported languages"""
    assert False

def test_detect_system_language():
    """Should detect OS language correctly"""
    assert False

def test_fallback_to_english():
    """Falls back to English if system language unavailable"""
    assert False

def test_switch_to_spanish():
    """UI should display Spanish text (bundled language)"""
    assert False

def test_switch_to_chinese():
    """UI should display Chinese characters correctly (bundled language)"""
    assert False

def test_download_language_on_demand():
    """Should download language file when user selects non-bundled language"""
    assert False

def test_cached_language_loads():
    """Previously downloaded language loads from cache"""
    assert False

def test_font_supports_chinese():
    """Verify Chinese characters render correctly"""
    # Use screenshot comparison
    assert False

def test_all_strings_marked_translatable():
    """No hardcoded English strings in UI code"""
    # Grep for patterns like QLabel("English") not using tr()
    assert False
```

### Implementation Loop

For EACH language:

1. Write failing test for that language
2. Implement translation file with mock translations (or use AI translation)
3. Run test and capture screenshot
4. Verify text displays correctly
5. Fix layout issues (text overflow, RTL, etc.)
6. Test passes ✓
7. Commit changes
8. Move to next language

### Special Considerations

**Right-to-Left (RTL) Languages (Arabic, Hebrew):**

- Set `QApplication.setLayoutDirection(Qt.RightToLeft)`
- Test that:
  - Menus appear on correct side
  - Buttons are mirrored
  - Tree widgets display correctly
  - Text alignment is proper

**CJK Languages (Chinese, Japanese, Korean):**

- Verify font fallback works (Qt should handle automatically)
- Test font sizes are readable
- Verify no text truncation with wider characters
- Test that vertical spacing is adequate

**Font Configuration:**

- Add font detection/fallback system
- Bundle Noto Sans fonts for comprehensive Unicode coverage:
  - Noto Sans (Latin, Greek, Cyrillic)
  - Noto Sans CJK (Chinese, Japanese, Korean)
  - Noto Sans Arabic
  - Noto Sans Hebrew

### Verification Checklist Per Language

- [ ] Translation file created and populated
- [ ] Screenshot captured showing UI in that language
- [ ] No text overflow or truncation
- [ ] No mojibake (corrupted characters)
- [ ] All UI elements translated (menus, buttons, dialogs)
- [ ] Keyboard shortcuts still work
- [ ] Tests pass for language switching

---

## Phase 2: Accessibility Implementation

### Goal

Make the application fully accessible to users with disabilities, following WCAG 2.1 Level AA standards.

### Accessibility Features to Implement

#### 1. Screen Reader Support (Critical for Blind Users)

**Implementation:**

a) **Set Accessible Names and Descriptions**

- Every interactive element needs accessible properties

```python
widget.setAccessibleName("File Browser Tree")
widget.setAccessibleDescription("Select files and folders to include in output")
button.setAccessibleName("Generate Content")
```

b) **Update `main_window.py` and All UI Files**

- File tree: Add accessible descriptions for each node type
- Buttons: Ensure accessible names match visible text
- Checkboxes: Clear accessible state reporting
- Menus: Verify keyboard navigation works
- Dialogs: Set accessible relationships

c) **Test with Screen Readers**

- Windows: NVDA (open source)
- macOS: VoiceOver (built-in)
- Linux: Orca (open source)

**Testing Strategy:**

```python
# tests/test_accessibility_screen_reader.py

def test_file_tree_has_accessible_name():
    """File tree must have accessible name for screen readers"""
    assert False

def test_all_buttons_have_accessible_names():
    """Every button must be identifiable by screen readers"""
    assert False

def test_generate_button_announces_action():
    """Generate button describes what it will do"""
    assert False

def test_keyboard_navigation_works():
    """All UI accessible via keyboard only"""
    assert False
```

#### 2. Keyboard Navigation (Critical for Motor Impairments)

**Implementation:**

a) **Tab Order**

- Set proper tab order for all widgets
- Test: Can user Tab through entire UI logically?

b) **Keyboard Shortcuts**

- Add shortcuts for all major actions
- Follow platform conventions (Ctrl vs Cmd)
- Document shortcuts in Help menu

c) **Focus Indicators**

- Ensure focus rectangle visible for all widgets
- Test with high contrast themes
- Custom focus style if needed:

```python
widget.setStyleSheet("QWidget:focus { border: 2px solid #0078d4; }")
```

**Testing Strategy:**

```python
# tests/test_accessibility_keyboard.py

def test_tab_order_logical():
    """Tab key moves through UI in logical order"""
    assert False

def test_all_actions_have_shortcuts():
    """Major actions accessible via keyboard"""
    assert False

def test_keyboard_only_workflow():
    """Complete workflow possible without mouse"""
    assert False

def test_escape_closes_dialogs():
    """ESC key closes all modal dialogs"""
    assert False

def test_focus_visible():
    """Focus indicator clearly visible on all widgets"""
    # Screenshot comparison
    assert False
```

#### 3. Color Contrast (Critical for Low Vision)

**Implementation:**

a) **Measure Current Contrast Ratios**

- Tool: Create function using PIL/Qt to measure contrast
- Requirement: 4.5:1 for normal text, 3:1 for large text (WCAG AA)

b) **Fix Dark Mode Contrast**

- Review all color combinations in `apptheme.py`
- Ensure sufficient contrast
- Test with color blindness simulators

c) **Fix Light Mode Contrast**

- Same as dark mode
- Common issues: gray text on white background

**Testing Strategy:**

```python
# tests/test_accessibility_contrast.py

def test_dark_mode_contrast_ratios():
    """All text in dark mode meets WCAG AA contrast"""
    assert False

def test_light_mode_contrast_ratios():
    """All text in light mode meets WCAG AA contrast"""
    assert False

def test_error_messages_visible():
    """Error colors have sufficient contrast"""
    assert False

def test_selected_items_visible():
    """Selection color has sufficient contrast"""
    assert False
```

#### 4. Text Scaling (Critical for Low Vision)

**Implementation:**

a) **Respect System Font Size**

- Use system default font size as base
- Scale UI proportionally

b) **Add Font Size Controls**

- Settings menu: Text Size option
- Options: Small, Normal, Large, Extra Large
- Save preference

c) **Test UI at Different Sizes**

- Ensure no text truncation
- Ensure buttons remain accessible
- Test at 200% zoom

**Testing Strategy:**

```python
# tests/test_accessibility_text_scaling.py

def test_font_size_increases():
    """Font size settings work"""
    assert False

def test_ui_scales_at_200_percent():
    """UI remains usable at 200% text size"""
    assert False

def test_no_text_truncation_large_font():
    """All text visible at largest font size"""
    # Screenshot comparison
    assert False
```

#### 5. High Contrast Mode Support

**Implementation:**

a) **Detect System High Contrast Mode**

- Windows: Check system settings
- Adjust colors accordingly

b) **Provide High Contrast Theme Option**

- Add to theme selection
- Black/white with minimal colors
- Maximum contrast

**Testing Strategy:**

```python
# tests/test_accessibility_high_contrast.py

def test_high_contrast_mode_detected():
    """App detects system high contrast setting"""
    assert False

def test_high_contrast_theme_works():
    """High contrast theme provides maximum visibility"""
    assert False
```

#### 6. Motion Reduction (For Vestibular Disorders)

**Implementation:**

a) **Detect Prefers Reduced Motion**

- Check system setting
- Disable animations if set

b) **Add Option to Disable Animations**

- Settings: "Reduce animations"
- Disable/simplify any UI animations

**Testing Strategy:**

```python
# tests/test_accessibility_motion.py

def test_reduced_motion_respected():
    """Animations disabled when system preference set"""
    assert False
```

---

## Phase 3: Integration & Comprehensive Testing

### Test Matrix

Create comprehensive test suite covering all combinations:

| Language | Screen Reader | Keyboard Only | High Contrast | Large Font |
| -------- | ------------- | ------------- | ------------- | ---------- |
| English  | ✓             | ✓             | ✓             | ✓          |
| Spanish  | ✓             | ✓             | ✓             | ✓          |
| Arabic   | ✓             | ✓             | ✓             | ✓          |
| Chinese  | ✓             | ✓             | ✓             | ✓          |
| ...      | ...           | ...           | ...           | ...        |

### Automated Test Suite

```python
# tests/test_comprehensive_accessibility.py

@pytest.mark.parametrize("language", ["en", "es", "fr", "de", "zh_CN", "ar", "he"])
def test_language_accessibility_complete(language):
    """Each language works with all accessibility features"""
    # Set language
    # Enable high contrast
    # Set large font
    # Test keyboard navigation
    # Capture screenshot
    # Verify all elements accessible
    assert False

def test_wcag_aa_compliance():
    """Application meets WCAG 2.1 Level AA"""
    assert False
```

---

## Phase 4: Documentation & Finalization

### Documentation to Create

1. **User Guide: Accessibility Features**

   - File: `docs/ACCESSIBILITY.md`
   - Document all accessibility features
   - How to use with screen readers
   - Keyboard shortcuts reference
   - How to adjust text size

2. **User Guide: Language Selection**

   - File: `docs/INTERNATIONALIZATION.md`
   - How to change language
   - List of supported languages
   - How to contribute translations

3. **Developer Guide: Adding Translations**

   - File: `docs/TRANSLATION_GUIDE.md`
   - How to mark strings as translatable
   - How to generate/update .ts files
   - Translation workflow

4. **Update README.md**
   - Add section on accessibility
   - Add section on internationalization
   - List supported languages with flags/icons

---

## Implementation Workflow (Agent Instructions)

### Iterative Development Process

**For EACH feature or language:**

1. **Write Failing Test First**

   ```bash
   # Example for Spanish support
   uv run pytest tests/test_i18n.py::test_switch_to_spanish -v
   # Should FAIL
   ```

2. **Implement Minimum Code to Pass Test**

   - Add translation file
   - Mark strings as translatable
   - Implement language switching

3. **Capture Screenshot for Verification**

   ```python
   # In test or manually
   screenshot_path = capture_window_screenshot(main_window)
   print(f"Screenshot saved: {screenshot_path}")
   ```

4. **Visual Inspection**

   - Agent: Analyze screenshot for:
     - Text displays correctly
     - No truncation
     - No overlapping elements
     - RTL layout correct (for Arabic/Hebrew)
     - Font rendering good

5. **Fix Issues Found**

   - Adjust layouts
   - Fix fonts
   - Fix text lengths
   - Fix alignment

6. **Verify Test Passes**

   ```bash
   uv run pytest tests/test_i18n.py::test_switch_to_spanish -v
   # Should PASS
   ```

7. **Commit Changes**

   ```bash
   git add .
   git commit -m "Add Spanish language support

   - Created es.ts translation file
   - Marked strings as translatable in main_window.py
   - Verified UI renders correctly
   - All tests pass"
   # Remember: commit to feature/i18n-accessibility branch
   ```

8. **Move to Next Feature/Language**
   - Repeat steps 1-7

### Progress Tracking

Create a checklist file: `INTL_A11Y_PROGRESS.md`

```markdown
# Implementation Progress

## Internationalization

### Infrastructure

- [x] Screenshot system working
- [ ] Translation manager implemented
- [ ] System language detection working
- [ ] Language selection UI added
- [ ] Dynamic retranslation working
- [ ] On-demand download system working

### Bundled Languages (High Priority)

- [ ] English (en) - source, always bundled
- [ ] Spanish (es) - bundled
- [ ] Chinese Simplified (zh_CN) - bundled
- [ ] French (fr) - bundled

### On-Demand Languages (Download When Selected)

- [ ] German (de)
- [ ] Japanese (ja)
- [ ] Korean (ko)
- [ ] Arabic (ar) - RTL
- [ ] Hebrew (he) - RTL
- [ ] Russian (ru)
- [ ] Portuguese (pt)
- [ ] Chinese Traditional (zh_TW)
- [ ] Italian (it)
- [ ] Add more as requested by users

## Accessibility

### Screen Reader Support

- [ ] All widgets have accessible names
- [ ] All buttons have accessible descriptions
- [ ] File tree navigation accessible
- [ ] Tested with NVDA/VoiceOver

### Keyboard Navigation

- [ ] Tab order logical
- [ ] All actions have shortcuts
- [ ] Keyboard-only workflow tested
- [ ] Focus indicators visible

### Visual Accessibility

- [ ] Dark mode contrast WCAG AA
- [ ] Light mode contrast WCAG AA
- [ ] Font scaling implemented
- [ ] High contrast mode supported
- [ ] Motion reduction respected

## Testing

- [ ] All i18n tests passing
- [ ] All a11y tests passing
- [ ] Screenshot baseline captured
- [ ] Manual testing completed

## Documentation

- [ ] ACCESSIBILITY.md created
- [ ] INTERNATIONALIZATION.md created
- [ ] TRANSLATION_GUIDE.md created
- [ ] README.md updated
```

Update this file after each feature completion.

---

## Success Criteria

### Before Requesting Human Review

All of the following must be TRUE:

1. **All Tests Pass**

   ```bash
   uv run pytest tests/test_i18n.py -v
   uv run pytest tests/test_accessibility*.py -v
   # 100% pass rate
   ```

2. **All Languages Tested**

   - Screenshot captured for each language
   - No visual issues observed
   - RTL languages display correctly

3. **Accessibility Verified**

   - All widgets have accessible properties
   - Keyboard navigation works completely
   - Contrast ratios meet WCAG AA
   - Text scaling works without breaking UI

4. **Documentation Complete**

   - All required docs created
   - README updated
   - Translation guide available

5. **No Regressions**

   - Existing functionality still works
   - All previous tests still pass
   - No performance degradation

6. **Code Quality**
   - No linting errors
   - Type hints added where appropriate
   - Code follows project conventions

### Agent Self-Checklist Before Completion

Go through this list and verify each item:

```markdown
## Pre-Completion Verification

- [ ] System language detection works automatically
- [ ] I can run the app and switch between all 4 bundled languages
- [ ] Each bundled language displays without errors
- [ ] On-demand download system works (tested with at least 1 language)
- [ ] Previously downloaded languages load from cache
- [ ] RTL support implemented (tested with at least 1 RTL language)
- [ ] I can navigate the entire app using only keyboard
- [ ] All buttons have tooltips and accessible names
- [ ] Color contrast meets WCAG AA in both themes
- [ ] Text can be scaled to 200% without breaking UI
- [ ] All tests pass (run full test suite)
- [ ] Screenshots captured for each bundled language
- [ ] Documentation is complete and accurate
- [ ] No console errors when running the app
- [ ] Translation files are properly formatted
- [ ] Package size increased by less than 2MB (bundled translations)
- [ ] Git history is clean with descriptive commits
```

Only when ALL items are checked, notify human that feature is ready for review.

---

## Example Implementation Snippet

### For Reference: How to Mark Strings Translatable

**BEFORE (Hardcoded):**

```python
button = QtWidgets.QPushButton("Generate Content!")
label = QtWidgets.QLabel("The selected files will be added...")
menu = mb.addMenu("&File")
```

**AFTER (Translatable):**

```python
button = QtWidgets.QPushButton(self.tr("Generate Content!"))
label = QtWidgets.QLabel(self.tr("The selected files will be added..."))
menu = mb.addMenu(self.tr("&File"))
```

### For Reference: Implementing retranslateUi

```python
class FileSelectionGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        # Create widgets (WITHOUT text initially)
        self.generate_button = QtWidgets.QPushButton()
        self.file_menu = self.menuBar().addMenu("")
        # etc...

        # Set text via retranslateUi
        self.retranslateUi()

    def retranslateUi(self):
        """Set all translatable text - called on init and language change"""
        self.setWindowTitle(self.tr("AICodePrep - File Selection"))
        self.generate_button.setText(self.tr("Generate Content!"))
        self.file_menu.setTitle(self.tr("&File"))
        # ... all other text

    def changeEvent(self, event):
        """Handle language change events"""
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)
```

---

## Timeline Estimate

**Optimistic (Agent working continuously):**

- Phase 0 (Screenshot): 2-3 hours
- Phase 1 (i18n): 8-12 hours
- Phase 2 (a11y): 6-10 hours
- Phase 3 (Testing): 4-6 hours
- Phase 4 (Docs): 2-3 hours
- **Total: 22-34 hours**

**Realistic (With iterations and fixes):**

- Account for screenshot analysis time
- Multiple iterations per feature
- Testing and debugging time
- **Total: 40-50 hours**

---

## Agent Starting Instructions

**To begin implementation:**

1. Read this entire document carefully
2. Create the progress tracking file: `INTL_A11Y_PROGRESS.md`
3. Start with Phase 0: Screenshot system
4. Write the first failing test
5. Implement feature to pass test
6. Capture screenshot and verify
7. Commit and move to next test
8. Work through phases in order
9. Update progress file after each completion
10. Only request human review when ALL success criteria met

**Remember:**

- Write tests FIRST (TDD)
- Capture screenshots for verification
- Commit frequently with clear messages
- Update progress tracking
- Don't skip phases
- Self-verify before declaring complete

---

## Questions for Agent to Ask Human (If Needed)

- Which languages are highest priority? (Focus on those first)
- Are there any specific accessibility requirements beyond WCAG AA?
- Should translation files use AI translation or leave blank for human translators?
- What is the preferred testing approach for screen readers? (automated vs manual)
- Are there any existing translation resources or glossaries to use?

---

## END OF IMPLEMENTATION PLAN

**Agent**: When you are assigned this task, follow this plan meticulously. Work iteratively, test continuously, and only declare completion when all success criteria are verified. Good luck!
