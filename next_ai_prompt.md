# AI Agent Prompt: Wrap User-Facing Strings with Translation Markers

## Task Overview

You are an AI agent tasked with implementing internationalization in the AI Code Prep GUI application by wrapping all user-facing strings with appropriate translation markers.

## Your Mission

Wrap all user-facing strings in the application code with `self.tr()` method calls so they can be extracted for translation.

## Key Files to Modify

1. `aicodeprep_gui/gui/main_window.py` - Main application window
2. `aicodeprep_gui/gui/components/dialogs.py` - All dialog components
3. `aicodeprep_gui/gui/components/installer_dialogs.py` - Installation dialogs
4. `aicodeprep_gui/gui/components/preset_buttons.py` - Preset button components
5. `aicodeprep_gui/main.py` - Main application entry point

## Translation Guidelines

### Basic String Wrapping

- Wrap all literal strings that users will see with `self.tr()`
- Example: `self.setWindowTitle("aicodeprep-gui - File Selection")`
  becomes: `self.setWindowTitle(self.tr("aicodeprep-gui - File Selection"))`

### Menu Items and Actions

- All menu text, action labels, and tooltips need translation
- Example: `quit_act = QtGui.QAction("&Quit", self)`
  becomes: `quit_act = QtGui.QAction(self.tr("&Quit"), self)`

### Dynamic Strings

- For strings with variables, use `self.tr()` with `.arg()` method
- Example: `self.token_label.setText(f"Estimated tokens: {total_tokens:,}")`
  becomes: `self.token_label.setText(self.tr("Estimated tokens: %L1").arg(total_tokens))`

### String Formatting

- Use Qt's translation formatting: `%1`, `%2`, `%L1` (for localized numbers)
- Placeholders will be replaced in the translated strings

## What NOT to Translate

- Internal variable names
- File paths and technical identifiers
- Debug strings or developer comments
- String keys used for programmatic purposes

## Quality Requirements

1. **Completeness**: Every user-facing string must be wrapped
2. **Accuracy**: Preserve the exact meaning and punctuation of original strings
3. **Context**: Maintain proper context for translators (don't break sentences unnecessarily)
4. **Testing**: After wrapping, run `python extract_translations.py` to verify strings are extracted

## Verification Process

1. After making changes, run the extraction script: `python extract_translations.py`
2. Check that the `.ts` files now contain the wrapped strings
3. The script should report finding source texts (not 0 as before)

## Reference Files

- `TRANSL.md` - Contains a comprehensive list of all strings that need translation, organized by file and location
- `verify_translations.py` - Script that can help identify unwrapped strings

## Important Notes

- Work systematically through each file
- Pay special attention to HTML content and multi-line strings
- Maintain the existing code structure and formatting
- Test your changes don't break the application functionality
- Focus only on string wrapping - don't modify logic or structure

## Success Criteria

When complete, running `python extract_translations.py` should show a significant number of source texts found (not zero), indicating that user-facing strings are now properly marked for translation.

Start with `main_window.py` and work through the files systematically. The `TRANSL.md` file provides a detailed checklist of exactly which strings need to be wrapped in each file.
