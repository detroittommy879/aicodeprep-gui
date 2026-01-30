# AGENTS_intl.md

## Internationalization & Accessibility Reference

This file contains detailed guidance for working with translations, language support, and accessibility features. Consult this when:

- Adding or updating UI elements that need translation
- Completing translations for a language
- Testing language switching or visual appearance across locales
- Debugging translation compilation issues
- Working on accessibility features

---

## i18n translations (.ts -> .qm)

- Translation sources and binaries:
  - `.ts` and `.qm` live in `aicodeprep_gui/i18n/translations/`
  - 20 bundled languages, all have .ts/.qm files
  - **COMPLETE translations:** Japanese (ja), Hindi (hi) - use these as templates
  - **PARTIAL translations:** es, fr, de, zh_CN, pt, it, ru, ko, ar, tr, pl, nl, sv, da, fi, no, zh_TW --i think we finished these

- When you edit `.ts` files manually, you must recompile `.qm`:
  - Compile all: `uv run python scripts/compile_translations.py`
  - Compile subset: `uv run python scripts/compile_translations.py es fr zh_CN`
  - Alternative: `uv run python scripts/generate_translations.py --compile-only`

- `scripts/generate_translations.py` modes:
  - default: update `.ts` via lupdate and compile `.qm`
  - `--compile-only`: compile existing `.ts` into `.qm` (does not modify `.ts`)
  - `--update-ts-only`: regenerate `.ts` from source (does not compile)

- Runtime loading:
  - `aicodeprep_gui/i18n/translator.py` loads `aicodeprep_gui_<lang>.qm`.
  - CLI helpers:
    - `uv run aicodeprep-gui --list-languages`
    - `uv run aicodeprep-gui --language es`

---

## i18n: Adding translations for a new language

To complete translations for a language (e.g., Spanish):

1. **Use ja or hi as template** - these have complete translations:
   - `aicodeprep_gui/i18n/translations/aicodeprep_gui_ja.ts` (Japanese)
   - `aicodeprep_gui/i18n/translations/aicodeprep_gui_hi.ts` (Hindi)

2. **Edit the target .ts file** - Copy structure from ja/hi, translate the `<translation>` values:
   - Remove `type="unfinished"` attribute when translation is complete
   - Keep the `<source>` text exactly as-is (must match Python code)

3. **Compile after editing**: `uv run python scripts/compile_translations.py es`

4. **Test the language**: `uv run aicodeprep-gui --language es`

5. **Visual audit** (optional): `uv run python scripts/gui_language_screenshot_loop.py --language es`

---

## i18n: Key files for translation work

- `aicodeprep_gui/gui/main_window.py` - Main UI, most translatable strings here
  - All UI strings wrapped in `self.tr("...")`
  - `_retranslate_ui()` method handles live language switching
- `aicodeprep_gui/i18n/translator.py` - TranslationManager class
- `aicodeprep_gui/i18n/translations/` - All .ts and .qm files
- `INTL_A11Y_PROGRESS.md` - Progress tracking for i18n/a11y work

---

## i18n: Adding new UI elements (required workflow for devs/agents)

When you add new UI elements (buttons, labels, tooltips, dialogs, etc.), you **MUST** follow this workflow to ensure translations work:

### 1. Wrap ALL user-visible strings in `self.tr()`

In your Python code (typically `aicodeprep_gui/gui/main_window.py` or other GUI files):

```python
# CORRECT - wrapped in self.tr():
button.setText(self.tr("Click Me"))
button.setToolTip(self.tr("This button does something"))
label.setText(self.tr("File Name:"))

# WRONG - hardcoded English strings:
button.setText("Click Me")  # ❌ Won't be translated
button.setToolTip("This button does something")  # ❌ Won't be translated
```

**Critical locations to wrap:**

- Button text: `button.setText(self.tr("..."))`
- Labels: `label.setText(self.tr("..."))`
- Tooltips: `widget.setToolTip(self.tr("..."))`
- Checkbox text: `checkbox.setText(self.tr("..."))`
- Dialog titles and messages: `QMessageBox.information(self, self.tr("Title"), self.tr("Message"))`
- Group box titles: `groupbox.setTitle(self.tr("..."))`

**Exception:** HTML/styling markup in labels with "?" icons can stay outside, e.g.:

```python
help_icon.setText("<b style='color:#0098e4;'>?</b>")  # OK, not user text
help_icon.setToolTip(self.tr("This explains the feature"))  # Must wrap tooltip!
```

### 2. Regenerate translation files to pick up new strings

After adding/modifying `self.tr()` strings, run:

```bash
uv run python scripts/generate_translations.py
```

This will:

- Update all 20 `.ts` files with new strings (marked `type="unfinished"`)
- Compile `.qm` binaries

New strings will appear in `.ts` files like:

```xml
<message>
    <source>Your new English string</source>
    <translation type="unfinished"></translation>
</message>
```

### 3. Add translations to .ts files

Edit each language's `.ts` file in `aicodeprep_gui/i18n/translations/`:

**Use ja (Japanese) or hi (Hindi) as reference** - they have complete translations.

Example for Spanish (`aicodeprep_gui_es.ts`):

```xml
<message>
    <source>Your new English string</source>
    <translation>Tu nueva cadena en español</translation>  <!-- Add translation here -->
</message>
```

**Remove `type="unfinished"` attribute** when translation is complete.

### 4. Recompile .qm files after editing translations

After manually editing `.ts` files, recompile:

```bash
# Compile all languages:
uv run python scripts/compile_translations.py

# Or compile specific languages:
uv run python scripts/compile_translations.py es fr de
```

This generates `.qm` files that Qt actually loads at runtime.

### 5. Test your translations

```bash
# Test specific language:
uv run aicodeprep-gui --language es

# Visual audit with screenshots:
uv run python scripts/gui_language_screenshot_loop.py --language es
```

### Common mistakes to avoid:

1. **Forgetting to wrap tooltips** - Tooltips are easy to miss but critical for UX
2. **Not recompiling after editing .ts** - Changes won't appear until `.qm` files are compiled
3. **Hardcoding strings outside self.tr()** - These will stay English in all languages
4. **Forgetting dynamic strings** - Strings set via `setText()` later must also use `self.tr()`
5. **Skipping the regenerate step** - New strings won't appear in `.ts` files for translation

### Quick checklist for new features:

- [ ] All button text wrapped in `self.tr()`
- [ ] All labels wrapped in `self.tr()`
- [ ] All tooltips wrapped in `self.tr()`
- [ ] All dialog messages wrapped in `self.tr()`
- [ ] Ran `uv run python scripts/generate_translations.py`
- [ ] Added translations to key languages (at minimum: ja, hi, es, fr, de, zh_CN)
- [ ] Ran `uv run python scripts/compile_translations.py`
- [ ] Tested with `uv run aicodeprep-gui --language <lang>`

---

## GUI Language Testing & Screenshot Loop

Use this when you want the _actual GUI_ to run, switch language, capture screenshots, and generate a quick report of strings that stayed identical to English.

- Run one language:
  - `uv run python scripts/gui_language_screenshot_loop.py --language es`
- Run multiple languages:
  - `uv run python scripts/gui_language_screenshot_loop.py --languages es fr zh_CN`
- **Set auto-close timeout** (default 2500ms):
  - `uv run python scripts/gui_language_screenshot_loop.py --language es --auto-close-ms 5000`
  - Use longer timeout (e.g. 10000) if you need more time to view the window
- Output:
  - Screenshots + report written to `screenshots/test_captures/`
  - Report file name: `ui_i18n_audit_<lang>_<timestamp>.txt`

---

## Accessibility (a11y) Work

- See `INTL_A11Y_PROGRESS.md` for current status
- See `KEYBOARD_ACCESSIBILITY_CHECKLIST.md` for keyboard navigation requirements
- See `KEYBOARD_SHORTCUTS.md` for documented shortcuts
- See `I18N_ACCESSIBILITY_GUIDE.md` for implementation guide

---

## Troubleshooting Translation Issues

### Translation doesn't appear in UI

1. Check if string is wrapped in `self.tr()` in Python code
2. Verify `.ts` file has the translation (no `type="unfinished"`)
3. Recompile: `uv run python scripts/compile_translations.py <lang>`
4. Restart app with language: `uv run aicodeprep-gui --language <lang>`

### New strings not showing up in .ts files

1. Make sure strings are wrapped in `self.tr()` in Python code
2. Run: `uv run python scripts/generate_translations.py`
3. Check `.ts` files for new `<message>` entries

### .qm file not loading

1. Verify `.qm` file exists in `aicodeprep_gui/i18n/translations/`
2. Check filename matches pattern: `aicodeprep_gui_<lang>.qm`
3. Verify TranslationManager is loading the correct path

### Process hangs during screenshot loop

- Use `AICODEPREP_AUTO_CLOSE=1` environment variable
- Or add `--auto-close-ms 5000` to command
- On Windows, kill stuck processes: `taskkill /IM python.exe /F`
