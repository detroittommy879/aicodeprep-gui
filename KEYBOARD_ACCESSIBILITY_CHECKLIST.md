# Keyboard Navigation & Accessibility Implementation Checklist

## Phase 1: Core Keyboard Navigation

### Keyboard Handler Module

- [x] Create `aicodeprep_gui/gui/handlers/keyboard_handler.py` module
- [x] Implement `KeyboardShortcutManager` class with hardcoded default shortcuts (Ctrl+G → generate, Ctrl+A → select all, Ctrl+Shift+A → deselect all)
- [x] Add platform detection utility (`is_macos()`) to handle Ctrl/Cmd key differences
- [x] Verify module imports correctly

### Tree Widget Keyboard Navigation

- [x] Override `keyPressEvent()` in FileTreeManager (or LogoTreeWidget) to handle arrow key events
- [x] Implement Up/Down arrow navigation between tree items
- [x] Implement Right arrow to expand collapsed folders, Left arrow to collapse expanded folders
- [x] Test with large directory trees to ensure no performance issues with lazy-loading

### Focus Management & Tab Order

- [x] Set initial focus to file tree widget on app launch
- [x] Configure tab order: tree → prompt → buttons
- [x] Test tab key navigation flows logically through UI

### Space Key Checkbox Toggle

- [x] Extend keyPressEvent in tree widget to detect space key press
- [x] Toggle checkbox state of currently selected item(s)
- [x] Handle multi-selection scenario (toggle all simultaneously)

### Test & Verify Keyboard Navigation

- [x] Agent: Run app with `uv run aicodeprep-gui`, simulate key events, verify handlers work
- [ ] User: Perform complete keyboard-only workflow testing (launch → navigate tree → toggle files → tab to prompt → generate)
- [ ] Fix any issues identified during testing

## Phase 2: Global Shortcuts & Menu Integration

### Global Application Shortcuts

- [x] Create QAction or QShortcut objects in main_window for each global shortcut
- [x] Use KeyboardShortcutManager for platform-appropriate key combinations (Ctrl vs Cmd)
- [x] Connect shortcuts to existing methods (generate button, select all, deselect all)
- [x] Verify shortcuts work regardless of focus location in UI

### Menu Keyboard Accelerators

- [x] Add ampersand notation to menu titles and items (&File, &Edit, Open &Folder, &Generate Context, etc.)
- [x] Ensure no accelerator key conflicts within same menu
- [ ] Test Alt+Letter navigation opens menus and activates items

### Integrate Shortcuts with Main Window

- [x] Initialize KeyboardShortcutManager in main window startup
- [x] Update button tooltips to show keyboard shortcuts using `self.tr()` (e.g., `self.tr("Generate Context (Ctrl+G)")`)
- [x] Add shortcut hints to relevant UI elements (status bar, help menu)
- [x] Verify all shortcuts display correctly and work after integration

### Test Cross-Platform Shortcut Behavior

- [x] Agent: Verify KeyboardShortcutManager correctly detects platform and returns appropriate key combinations
- [ ] User: Test all shortcuts on Windows (Ctrl+G, Ctrl+A, Ctrl+Shift+A, Alt+Letter menus)
- [ ] User: Test all shortcuts on macOS (Cmd+G, Cmd+A, Cmd+Shift+A)
- [ ] User: Test on Linux if available (or document assumption that Ctrl behaves like Windows)

### Git Commit Phase 1 & 2

- [x] Stage all modified files from Phase 1 & 2
- [x] Write descriptive commit message for keyboard navigation and global shortcuts
- [x] Commit locally on feature/i18n-accessibility branch (DO NOT push to remote)

## Phase 3: Accessibility Labels & Documentation

### Accessible Properties

- [x] Add `setAccessibleName()` to major widgets: file tree, generate button, prompt text box, preset buttons area
- [x] Add `setAccessibleDescription()` to buttons and interactive elements
- [x] Ensure all accessible text uses `self.tr()` for i18n compatibility
- [x] Document which widgets received accessible properties in code comments

### Keyboard Shortcuts Documentation

- [x] Create `KEYBOARD_SHORTCUTS.md` file in repository root
- [x] Document all keyboard shortcuts organized by category (Navigation, Actions, Menus)
- [x] Include cross-platform notes explaining Ctrl/Cmd differences
- [x] Add usage examples showing typical keyboard-only workflow

### Update Progress Tracking

- [x] Update INTL_A11Y_PROGRESS.md checkboxes for completed items
- [x] Add implementation notes documenting delivered features
- [x] Add completion date

### Final Testing & Validation

- [x] Agent: Run complete test suite (all shortcuts, tree navigation, focus management, cross-platform handling)
- [x] Agent: Verify all major widgets have accessible properties set
- [ ] User: Perform real-world keyboard-only workflow testing across multiple scenarios
- [ ] User: Final approval or identify issues to address

### Git Commit Phase 3

- [ ] Stage all Phase 3 files (accessible properties, KEYBOARD_SHORTCUTS.md, INTL_A11Y_PROGRESS.md)
- [ ] Write descriptive commit message for accessibility labels and documentation
- [ ] Commit locally on feature/i18n-accessibility branch (DO NOT push to remote)

---

## Key Features Being Implemented

**Keyboard Navigation:**

- Arrow key navigation in file tree (Up/Down/Left/Right)
- Space key to toggle checkboxes
- Tab key navigation between major UI sections

**Global Shortcuts:**

- Ctrl+G (Cmd+G on macOS) - Generate context
- Ctrl+A (Cmd+A on macOS) - Select all
- Ctrl+Shift+A (Cmd+Shift+A on macOS) - Deselect all
- Alt+Letter menu navigation

**Accessibility:**

- Accessible names and descriptions on major widgets
- i18n-compatible accessible text using `self.tr()`
- Documentation for keyboard shortcuts
