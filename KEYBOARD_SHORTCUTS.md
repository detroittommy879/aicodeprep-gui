# Keyboard Shortcuts Reference

This document provides a comprehensive guide to all keyboard shortcuts and navigation features available in aicodeprep-gui.

## Global Shortcuts

These shortcuts work throughout the application, regardless of which element has focus:

| Action | Windows/Linux | macOS | Description |
|--------|---------------|-------|-------------|
| **Generate Context** | `Ctrl+G` | `Cmd+G` | Generate context from selected files and copy to clipboard |
| **Select All** | `Ctrl+A` | `Cmd+A` | Select all non-excluded files in the tree |
| **Deselect All** | `Ctrl+Shift+A` | `Cmd+Shift+A` | Deselect all files in the tree |
| **Quit** | `Ctrl+Q` | `Cmd+Q` | Quit the application |

## File Tree Navigation

Navigate and interact with the file/folder tree using these keys:

| Key | Action |
|-----|--------|
| **↑ Up Arrow** | Move selection to previous item |
| **↓ Down Arrow** | Move selection to next item |
| **→ Right Arrow** | Expand selected folder (if collapsed) |
| **← Left Arrow** | Collapse selected folder (if expanded) |
| **Space** | Toggle checkbox for selected item(s) |
| **Tab** | Move focus to next UI section (tree → prompt → buttons) |

### Multi-Selection

The tree widget supports selecting multiple items:

- Hold **Ctrl** (or **Cmd** on macOS) and click to select multiple items
- Press **Space** to toggle checkboxes for all selected items simultaneously

## Menu Navigation

Access menus using keyboard accelerators with **Alt** (or equivalent on your platform):

| Menu | Shortcut | Common Items |
|------|----------|--------------|
| **File** | `Alt+F` | Quit (`Q`) |
| **Edit** | `Alt+E` | New Preset (`N`), Open Settings Folder (`O`), Language (`L`) |
| **Flow** | `Alt+F` | Import (`I`), Export (`E`), Reset (`R`) |
| **Help** | `Alt+H` | Help/Links (`H`), About (`A`), Send Ideas (`S`) |

### Menu Item Accelerators

Once a menu is open, press the underlined letter to activate that item. For example:

1. Press `Alt+F` to open File menu
2. Press `Q` to quit

## Tab Order

The application follows a logical tab order for keyboard navigation:

1. **File Tree** - Navigate and select files
2. **Prompt Text Box** - Enter optional prompt
3. **Generate Context Button** - Primary action
4. **Select All Button** - Quick selection
5. **Deselect All Button** - Clear selection

Press **Tab** to move forward through this order, or **Shift+Tab** to move backward.

## Typical Keyboard-Only Workflow

Here's a complete workflow using only the keyboard:

1. **Launch application** - File tree has initial focus
2. **Navigate tree** - Use arrow keys (↑/↓) to browse files
3. **Expand folders** - Press → on folders to see contents
4. **Select files** - Press Space to toggle checkboxes
5. **Move to prompt** - Press Tab to focus prompt text box
6. **Enter prompt** (optional) - Type your question
7. **Generate** - Press Tab to reach Generate button, then Enter (or use `Ctrl+G` from anywhere)
8. **Context copied** - Application copies context to clipboard automatically

## Cross-Platform Notes

### Windows/Linux

- Primary modifier: **Ctrl**
- Menu access: **Alt**
- Standard keyboard navigation

### macOS

- Primary modifier: **Cmd** (⌘)
- Menu access: Platform-standard menu shortcuts
- All shortcuts automatically adapt to use Cmd instead of Ctrl

The application automatically detects your platform and uses the appropriate modifier keys.

## Accessibility Features

### Screen Reader Support

All major UI elements have accessible names and descriptions:

- **File Browser** - File tree with navigation instructions
- **Prompt Input** - Text box for entering prompts
- **Generate Context Button** - Primary action button
- **Prompt Presets** - Saved prompt template area

### Keyboard Navigation Best Practices

1. **Use Tab** to navigate between major sections
2. **Use Arrow Keys** within the file tree
3. **Use Space** to toggle selections
4. **Use Global Shortcuts** (`Ctrl+G`, etc.) for quick actions
5. **Use Alt+Letter** to access menus

## Tips and Tricks

- **Quick Generate**: Press `Ctrl+G` (or `Cmd+G`) from anywhere to generate context immediately
- **Fast Selection**: Use `Ctrl+A` to select all files at once
- **Keyboard-Only Operation**: The entire application can be operated without a mouse
- **Focus Indicator**: The currently focused element is highlighted for easy navigation

## Troubleshooting

### Shortcuts Not Working?

- Ensure the application window has focus
- Check if another application is capturing the same shortcut
- On macOS, verify System Preferences don't override the shortcut

### Can't Navigate Tree?

- Click the tree widget or press Tab until it has focus
- Check that keyboard focus indicator is visible on tree

### Menu Accelerators Not Responding?

- Press Alt (or platform equivalent) to activate menu bar
- Ensure you're pressing the underlined letter, not Ctrl+Letter

## Future Enhancements

Additional keyboard shortcuts and navigation features may be added in future versions. Check the changelog for updates.

---

**Need Help?** Visit [aicodeprep-gui documentation](https://wuu73.org/aicp) or contact tom@wuu73.org
