# Keyboard Navigation & Accessibility Enhancement – APM Implementation Plan

**Memory Strategy:** Dynamic-MD
**Last Modification:** Plan creation by the Setup Agent.
**Project Overview:** Implement minimal, pragmatic keyboard navigation and accessibility features for aicodeprep-gui PySide6 desktop application. Focus on core keyboard navigation (arrow keys, space, tab), hardcoded global shortcuts (Ctrl+G for generate, Ctrl+A for select all), and basic accessible labels for future AT compatibility. Skip comprehensive WCAG testing, TOML configuration, and complex dialog/preset keyboard enhancements to accelerate delivery.

---

## Phase 1: Core Keyboard Navigation

### Task 1.1 – Create Keyboard Handler Module - Agent_KeyboardNavigation

**Objective:** Create foundational keyboard handling infrastructure module.
**Output:** `aicodeprep_gui/gui/handlers/keyboard_handler.py` with KeyboardShortcutManager class.
**Guidance:** Establish central shortcut manager with hardcoded defaults and cross-platform key handling utilities (Ctrl/Cmd detection).

- Create `aicodeprep_gui/gui/handlers/keyboard_handler.py` module
- Implement `KeyboardShortcutManager` class with hardcoded default shortcuts dictionary (Ctrl+G → generate, Ctrl+A → select all, Ctrl+Shift+A → deselect all, standard menu shortcuts)
- Add platform detection utility (`is_macos()`) to handle Ctrl/Cmd key differences cross-platform
- Verify module imports correctly and integrates with existing handler structure

### Task 1.2 – Implement Tree Widget Keyboard Navigation - Agent_KeyboardNavigation

**Objective:** Enable full keyboard navigation in file tree widget.
**Output:** Enhanced FileTreeManager with arrow key navigation and folder expand/collapse.
**Guidance:** Override keyPressEvent in custom tree widget. Consider lazy-loading performance when implementing keyboard-driven tree expansion. **Depends on: Task 1.1 Output**

- Override `keyPressEvent()` in FileTreeManager (or LogoTreeWidget if that's the target) to handle arrow key events
- Implement Up/Down arrow navigation between tree items using QTreeWidget navigation API
- Implement Right arrow to expand collapsed folders, Left arrow to collapse expanded folders (use `item.setExpanded()`)
- Ensure lazy-loading tree expansion doesn't cause performance issues when navigating with keyboard (test with large directory trees)

### Task 1.3 – Implement Focus Management & Tab Order - Agent_KeyboardNavigation

**Objective:** Configure logical tab navigation and initial focus on tree widget.
**Output:** Properly configured focus management in main_window.py.
**Guidance:** Set tree widget as initial focus point on app launch. Configure tab order: tree → prompt → buttons.

- Set initial focus to file tree widget in main window `__init__` or `showEvent()` using `self.tree_widget.setFocus()`
- Configure tab order between major UI sections using `setTabOrder(tree_widget, prompt_textbox)` and `setTabOrder(prompt_textbox, generate_button)`
- Test tab key navigation flows logically through UI (tree → prompt → buttons)

### Task 1.4 – Add Space Key Checkbox Toggle - Agent_KeyboardNavigation

**Objective:** Enable space key to toggle file/folder selection checkboxes.
**Output:** Space key checkbox toggle functionality in tree widget.
**Guidance:** Extend keyPressEvent from Task 1.2 to handle space key. Support multi-selection toggle. **Depends on: Task 1.2 Output**

- Extend keyPressEvent in tree widget to detect space key press
- Toggle checkbox state of currently selected item(s) using `item.setCheckState()` (cycle between Qt.Checked and Qt.Unchecked)
- Handle multi-selection scenario (if multiple items selected, toggle all simultaneously)

### Task 1.5 – Test & Verify Keyboard Navigation - Agent_KeyboardNavigation

**Objective:** Validate all Phase 1 keyboard navigation functionality.
**Output:** Verified keyboard navigation with documented test results.
**Guidance:** Agent performs initial automated verification, user performs final manual validation per retained requirement. **Depends on: Task 1.1 Output, Task 1.2 Output, Task 1.3 Output, Task 1.4 Output**

1. **Agent Verification:** Run app with `uv run aicodeprep-gui`, simulate key events (arrows, space, tab), verify keyboard handlers respond correctly, document initial findings
2. **User Manual Testing:** User performs complete keyboard-only workflow testing (launch → navigate tree → toggle files → tab to prompt → generate), validates UX feels natural and responsive
3. **Issue Resolution:** If user identifies problems, agent makes fixes and returns to step 1; if validation passes, proceed to Phase 2

---

## Phase 2: Global Shortcuts & Menu Integration

### Task 2.1 – Implement Global Application Shortcuts - Agent_GlobalShortcuts

**Objective:** Register application-wide keyboard shortcuts for major actions.
**Output:** Functional global shortcuts (Ctrl+G, Ctrl+A, Ctrl+Shift+A) in main_window.py.
**Guidance:** Use QAction/QShortcut with KeyboardShortcutManager for cross-platform key handling. Connect to existing action methods. **Depends on: Task 1.1 Output by Agent_KeyboardNavigation**

- Create QAction or QShortcut objects in main_window for each global shortcut (generate context, select all, deselect all)
- Use KeyboardShortcutManager to get platform-appropriate key combinations (Ctrl vs Cmd based on OS)
- Connect shortcuts to existing methods: generate button click handler, select all handler, deselect all handler
- Verify shortcuts trigger actions correctly regardless of focus location in UI

### Task 2.2 – Add Menu Keyboard Accelerators - Agent_GlobalShortcuts

**Objective:** Enable keyboard navigation for all menu items.
**Output:** Keyboard-accessible menus with ampersand notation in main_window.py.
**Guidance:** Add accelerator keys to menu titles and items following standard conventions (Alt+F for File, etc.). Avoid key conflicts within same menu.

- Add ampersand notation to menu titles and menu items (&File, &Edit, Open &Folder, &Generate Context, etc.)
- Ensure no accelerator key conflicts within same menu (use different letters if needed)
- Test Alt+Letter navigation opens menus and activates menu items as expected

### Task 2.3 – Integrate Shortcuts with Main Window - Agent_GlobalShortcuts

**Objective:** Complete shortcut system integration and add user-visible shortcut hints.
**Output:** Fully integrated keyboard shortcut system with tooltips and help text.
**Guidance:** Initialize shortcut manager at app startup. Add shortcut hints to tooltips using self.tr() for i18n compatibility. **Depends on: Task 2.1 Output, Task 2.2 Output**

- Initialize KeyboardShortcutManager in main window startup sequence
- Update button tooltips to show keyboard shortcuts using `self.tr()` for i18n compatibility (e.g., `self.tr("Generate Context (Ctrl+G)")`)
- Add shortcut hints to relevant UI elements (status bar, help menu items)
- Verify all shortcuts display correctly and work after integration

### Task 2.4 – Test Cross-Platform Shortcut Behavior - Agent_GlobalShortcuts

**Objective:** Validate keyboard shortcuts work correctly across platforms.
**Output:** Verified cross-platform shortcut compatibility with test report.
**Guidance:** Agent tests platform detection logic. User performs actual platform-specific testing (Windows/macOS/Linux). Document platform-specific behavior. **Depends on: Task 2.3 Output**

1. **Agent Platform Detection Test:** Verify KeyboardShortcutManager correctly detects platform and returns appropriate key combinations (test `is_macos()` utility, verify Ctrl vs Cmd translation)
2. **Windows Testing:** User tests all shortcuts on Windows (Ctrl+G, Ctrl+A, Ctrl+Shift+A, Alt+Letter menus), validates behavior matches expectations
3. **macOS Testing:** User tests all shortcuts on macOS (Cmd+G, Cmd+A, Cmd+Shift+A, platform-appropriate menu shortcuts), validates Mac-specific behavior
4. **Linux Testing (if available):** User tests shortcuts on Linux, documents any platform-specific issues; if user doesn't have Linux, document assumption that Ctrl behaves like Windows

### Task 2.5 – Git Commit Phase 1 & 2 - Agent_GlobalShortcuts

**Objective:** Create local git commit capturing Phase 1 and 2 implementation.
**Output:** Local git commit on feature/i18n-accessibility branch.
**Guidance:** Stage all modified files, write descriptive commit message, commit locally. DO NOT push to remote per user requirement. **Depends on: Task 2.4 Output**

- Stage all modified files from Phase 1 & 2 using `git add` (keyboard_handler.py, main_window.py, FileTreeManager modifications, etc.)
- Write descriptive commit message: "feat: Add keyboard navigation and global shortcuts\n\n- Implement tree widget keyboard navigation (arrows, space toggle)\n- Add focus management and tab order\n- Implement global shortcuts (Ctrl+G, Ctrl+A, Ctrl+Shift+A)\n- Add menu keyboard accelerators\n- Cross-platform key handling (Ctrl/Cmd)"
- Commit locally on feature/i18n-accessibility branch (DO NOT push to remote per user requirement)

---

## Phase 3: Accessibility Labels & Documentation

### Task 3.1 – Add Accessible Properties to Major Widgets - Agent_Accessibility

**Objective:** Annotate major UI widgets with accessible properties for future AT compatibility.
**Output:** Accessible names and descriptions set on all major interactive elements.
**Guidance:** Add setAccessibleName/Description to widgets using self.tr() for i18n compatibility. No AT testing required per user preference.

- Add `setAccessibleName()` to major widgets: file tree (`self.tr("File Browser")`), generate button (`self.tr("Generate Context Button")`), prompt text box (`self.tr("Prompt Input")`), preset buttons area (`self.tr("Prompt Presets")`)
- Add `setAccessibleDescription()` to buttons and interactive elements explaining their purpose (e.g., `self.tr("Generate context and copy to clipboard")`)
- Ensure all accessible text uses `self.tr()` for i18n compatibility across all 20 bundled languages
- Document which widgets received accessible properties in code comments for future reference

### Task 3.2 – Create Keyboard Shortcuts Documentation - Agent_Accessibility

**Objective:** Create comprehensive keyboard shortcuts reference documentation.
**Output:** KEYBOARD_SHORTCUTS.md file with complete shortcut documentation.
**Guidance:** Document all shortcuts organized by category. Include cross-platform notes (Ctrl/Cmd). User will integrate into main docs later. **Depends on: Task 2.5 Output by Agent_GlobalShortcuts**

- Create `KEYBOARD_SHORTCUTS.md` file in repository root with clear title and introduction
- Document all keyboard shortcuts organized by category: Navigation (arrows, space, tab), Actions (Ctrl+G, Ctrl+A, Ctrl+Shift+A), Menus (Alt+Letter shortcuts)
- Include cross-platform notes explaining Ctrl/Cmd differences between Windows/Linux and macOS
- Add usage examples showing typical keyboard-only workflow (launch → navigate → select → generate)

### Task 3.3 – Update INTL_A11Y_PROGRESS.md - Agent_Accessibility

**Objective:** Update progress tracking file to reflect completed work.
**Output:** Updated INTL_A11Y_PROGRESS.md with completed items checked off.
**Guidance:** Check off completed accessibility items (keyboard navigation, basic accessible labels). Add implementation notes.

- Update INTL_A11Y_PROGRESS.md checkboxes for completed items under "Accessibility" section (keyboard navigation, basic accessible labels)
- Add implementation notes documenting delivered features: arrow navigation, space toggle, tab order, global shortcuts, accessible properties
- Add completion date and note that feature is ready for user testing/integration

### Task 3.4 – Final Testing & Validation - Agent_Accessibility

**Objective:** Perform comprehensive end-to-end validation of all features.
**Output:** Validated complete feature implementation with test report.
**Guidance:** Agent performs comprehensive automated testing and property verification. User performs final manual validation and approval. **Depends on: Task 3.1 Output, Task 3.2 Output, Task 3.3 Output**

1. **Agent Comprehensive Testing:** Run complete test suite - all keyboard shortcuts (Ctrl+G, Ctrl+A, menus), tree navigation (arrows, space, tab), focus management, cross-platform key handling verification, document test results
2. **Accessible Property Verification:** Agent inspects code to verify all major widgets have accessible properties set, confirms self.tr() usage for i18n, documents which widgets are annotated
3. **User Manual Validation:** User performs real-world keyboard-only workflow testing across multiple scenarios, validates UX quality, identifies any usability issues or missing features
4. **Final Approval or Issue Resolution:** If user approves, proceed to Task 3.5 for final commit; if issues found, agent addresses them and returns to step 1

### Task 3.5 – Git Commit Phase 3 & Feature Complete - Agent_Accessibility

**Objective:** Create final git commit marking feature implementation complete.
**Output:** Final local git commit on feature/i18n-accessibility branch.
**Guidance:** Stage Phase 3 files, write commit message noting feature completion, commit locally. DO NOT push to remote. **Depends on: Task 3.4 Output**

- Stage all Phase 3 files using `git add` (accessible property additions, KEYBOARD_SHORTCUTS.md, INTL_A11Y_PROGRESS.md updates)
- Write descriptive commit message: "feat: Add accessibility labels and documentation\n\n- Add accessible properties to major widgets (tree, buttons, text boxes)\n- Create KEYBOARD_SHORTCUTS.md documentation\n- Update progress tracking\n- Feature complete: keyboard navigation + basic accessibility"
- Commit locally on feature/i18n-accessibility branch (DO NOT push to remote per user requirement)
