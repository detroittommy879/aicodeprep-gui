# Internationalization & Accessibility Guide

**Version:** 0.10.3 | **Branch:** `feature/i18n-accessibility` | **Status:** Complete ✅

Quick reference for i18n and accessibility features in aicodeprep-gui.

---

## Internationalization (i18n)

### Supported Languages

**20 bundled languages** (no downloads required):

- **Complete:** English (en), Japanese (ja), Hindi (hi)
- **Partial:** Spanish (es), French (fr), German (de), Chinese Simplified (zh_CN), Portuguese (pt), Italian (it), Russian (ru), Korean (ko), Arabic (ar), Turkish (tr), Polish (pl), Dutch (nl), Swedish (sv), Danish (da), Finnish (fi), Norwegian (no), Chinese Traditional (zh_TW)

### CLI Commands

```bash
aicp --list-languages              # List all available languages
aicp --language es                 # Launch with Spanish
aicp --language ja                 # Launch with Japanese
```

### GUI Language Switching

**Edit → Language** - Switch languages at runtime (no restart required, though may be glitchy - restart if needed)

### System Detection

Auto-detects OS language on first launch. Falls back to English if language not bundled.

---

## Keyboard Navigation & Shortcuts

### Global Shortcuts

| Action       | Windows/Linux  | macOS         |
| ------------ | -------------- | ------------- |
| Generate     | `Ctrl+G`       | `Cmd+G`       |
| Select All   | `Ctrl+A`       | `Cmd+A`       |
| Deselect All | `Ctrl+Shift+A` | `Cmd+Shift+A` |
| Quit         | `Ctrl+Q`       | `Cmd+Q`       |

### File Tree Navigation

- **↑/↓** - Navigate items
- **→** - Expand folder
- **←** - Collapse folder
- **Space** - Toggle checkbox
- **Tab** - Move to next widget

### Menu Navigation

- **Alt+F** - File menu
- **Alt+E** - Edit menu (Language)
- **Alt+H** - Help menu

---

## Accessibility

### Screen Reader Support

All major widgets have accessible names and descriptions:

- File tree, prompt input, all buttons, preset area
- Not Tested with NVDA (Windows), VoiceOver (macOS), Orca (Linux) but if you find any errors and/or want a feature or fix, let me know

### Focus Management

- Initial focus on file tree
- Logical tab order: tree → prompt → buttons
- Visible focus indicators
