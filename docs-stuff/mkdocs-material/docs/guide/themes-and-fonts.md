# Themes and Fonts

![Screenshot Placeholder: Showcase of various themes](../img/themes-showcase-placeholder.png)

## Built-in themes

w111erd ships with a broad set of built-in themes instead of a single fixed look.

The catalog includes practical themes, stylized themes, novelty themes, and a few intentionally louder showcase themes.

The newer preset families are easy to spot because their names start with `v2-`, `v3-`, or `v4-`.

- `v2-` themes are bundled-font house presets.
- `v3-` themes push more distinct ANSI palettes.
- `v4-` themes are converted from the MIT-licensed Gogh terminal theme catalog.

Examples include:

- Pure Black
- Soft Black
- Pure White
- Soft White
- Midnight Console
- Amber Relay
- Neon Circuit
- Mallsoft Deck
- Bootleg Broadcast

## Apply sections matter

Themes are not all-or-nothing.

Instead of a single apply target, you can now decide whether a preset should change:

- app chrome
- terminal colors
- fonts
- gradients
- special effects

That makes it possible to keep your current typography, borrow only a gradient, or take colors from one preset and effects from another.

The Themes page also includes a `Randomize Bundled Fonts` button. It only picks from bundled fonts, and it keeps the terminal on bundled monospaced faces.

The Themes page is also more compact now: presets are grouped by family, the large Gogh import set stays collapsed by default, and you can filter by name, id, mood, or author.

## Saving and exporting custom themes

The Themes tab also has a custom theme library for your own looks.

Use it to:

- save the current app chrome, terminal colors, gradients, typography, and effects into the active profile
- reopen the profile theme folder directly from the UI
- export a saved theme as a JSON file for backup or sharing

Saved themes live beside the rest of the active profile data, so different
profiles can keep different theme libraries.

## Terminal colors

The terminal settings include the full 16-color ANSI palette, plus:

- background
- foreground
- cursor color
- selection color
- cursor blink

This lets the terminal itself feel distinct from the surrounding app shell.

The terminal settings page also includes a live ANSI preview so you can see the
16-color ramp update immediately even if the current shell output is not using
ANSI escapes.

Built-in themes can now define their own ANSI palettes too, so applying a theme
can change both the terminal chrome and the actual color ramp used by colored
terminal output.

The `v4-` Gogh imports carry their ANSI ramps directly from the source themes, with a mild background-adjacent gradient added to some of them so they still feel native inside w111erd.

## Gradients

The terminal can use a gradient background instead of a flat color.

You can control:

- whether gradients are enabled
- whether the gradient animates
- start and end colors
- extra blend colors
- gradient angle

If you want a plain terminal, you can turn the effect off.

## Fonts for different parts of the app

Typography is split into zones rather than one global font switch.

You can style fonts for:

- the shell UI
- tabs
- preset dock
- settings panel
- assistant panel
- status bar
- terminal text

That means the terminal can stay monospaced while the rest of the interface uses a more readable UI font.

The detached AI Help window now uses its own assistant typography zone correctly, so changing the assistant font settings actually changes that separate window instead of only the in-app styling hooks.

If you want one cleaner visual pass across the non-terminal UI, the Fonts tab now includes a `V5 Whole-App Fonts` section that copies one font treatment across the shell, tabs, dock, settings, AI Help, and status bar while keeping each area's own size.

## Terminal font controls

For the terminal itself, the important controls are:

- font family
- font size
- font weight

For the rest of the app UI, the main controls are font family, size, weight, and spacing.

## AI Help colors

The `AI Help` settings tab now includes its own window appearance controls for:

- background
- header
- button fill
- button hover
- accent color

Those controls are meant for the detached AI Help window, so you can make it feel complementary to the terminal without making it look identical.

Google Fonts are now disabled by default. You can enable them explicitly from the Fonts tab.

When Google Fonts stay disabled:

- the pickers only show bundled fonts
- existing saved Google-font selections are sanitized back to bundled stacks
- built-in `v2-` presets stay fully local because they only use bundled fonts

For bundled fonts, the app also tracks the real file names and known available weights more directly than before.

## Why fonts matter here

This app puts unusual weight on font quality because terminals live or die on readability.

If a font feels too heavy, too cramped, or too decorative, the interface becomes tiring fast. The goal of the font controls is to let you tune the terminal until it feels comfortable instead of forcing one generic monospaced stack on every user.
