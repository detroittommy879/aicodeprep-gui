# Everyday Use

## Tabs

Tabs are the main way to keep separate shells organized.

You can:

- open new tabs from the top bar
- click any tab to focus it
- double-click a tab title to rename it
- use the tab action menu to show a hidden tab in the current split layout
- close and recover recently closed tabs inside the app's undo window

The point is to keep terminal sessions named and visible instead of losing track of them.

## Splits and grids

![Screenshot Placeholder: Tiled terminal windows in grid layout](../img/tiled-windows-placeholder.png)

w111erd is built to show more than one terminal at a time.

From the top controls you can:

- arrange existing tabs left and right
- arrange existing tabs top and bottom
- show all tabs in a grid
- collapse the layout back down to one active tab

This is useful if you want one pane for a running command, another for logs, and another for navigation.

The split buttons do not create terminals anymore. Use the New Tab button when you want another shell, then use the layout controls to decide which tabs are visible at the same time.

When a split layout is active, tabs that are currently shown are marked in the tab strip. Open the tab action menu to bring a hidden tab into the current layout or to close a terminal explicitly.

## Copy and paste

Copy and paste behavior can vary a lot between terminal apps, shells, and operating systems. w111erd now handles those actions more directly so they are less dependent on whatever the shell happens to expect.

You can:

- use the app menu for Copy, Paste, and Select All
- use the configured keyboard shortcut preset from Settings
- switch paste mode between Auto, Direct, and Bracketed in Settings

Auto currently prefers direct paste on Windows and bracketed paste on macOS and Linux.

## Preset buttons

Preset buttons are one of the most approachable parts of the app.

Instead of remembering commands, you can click a button to send a prepared command into the active terminal.

The default top preset set includes examples like:

- Clear
- Dir
- Git Status
- Git Log
- PWD

You can add your own presets from the UI.

## Cool Stuff menu

The `Cool Stuff` menu is meant for the "I just want a machine ready quickly"
case.

Use `Cool Stuff` -> `Install AI Coding tools/apps` when you want w111erd to
help bootstrap a Windows, Ubuntu, or macOS AI-coding setup.

The dialog will:

- auto-detect the current operating system
- explain what the bundled script installs
- show the exact command it plans to type
- open a fresh terminal tab with that command prefilled instead of silently
  running it

That makes it easier to inspect what will happen first, especially on Windows
where the installer expects an elevated PowerShell session.

## SSH presets in the side dock

The left preset dock is separate from the top command bar.

It is intended for SSH or connection-oriented commands that you want to keep visible in their own place. That dock can be resized and collapsed.

## Search, links, and copied output

The terminal layer supports:

- search inside terminal content
- clickable web links when link detection is active
- serialized terminal text for saved session behavior behind the scenes

## AI Help button

The AI Help button in the status bar now opens a separate native window instead
of an in-app bottom panel.

That AI Help window can:

- live on another monitor or outside the main terminal window
- use normal OS maximize, restore, and snapping behavior
- use the current terminal tab as context
- stream the answer into the chat window as it arrives
- explain recent terminal output
- suggest up to three ordered terminal actions at a time
- send commands into the active terminal or trigger terminal controls like `Ctrl+C`
- run a short step sequence in order and wait for terminal output to settle between steps
- show an optional AI debug panel with the exact prompt, terminal context, and raw provider output
- zoom the AI panel text in or out directly from the overlay header

AI Help is configured inside the overlay itself. For now it supports:

- OpenRouter
- OpenAI
- generic OpenAI-compatible endpoints

The AI Help window now also links directly to a full `AI Help` tab in the
separate Settings window, which is the easiest place to fill in your endpoint,
model, API key, context defaults, and temperature.

Both the overlay and the Settings dialog expose a live connection test. That
test goes through the Rust/Tauri backend and sends a real OpenAI-compatible
request with your current provider settings.

Both surfaces now also try the provider's `v1/models` endpoint when possible.
If that succeeds, you get both a manual model field and a separate discovered-
model picker, so you do not need to clear the current model value just to pick
from the provider list.

Provider settings are stored in the active profile config, and the prompt files
live in `src/ai/prompts/` if you want to tweak the wording in the source tree.

## Settings window

Settings now opens in its own native window instead of staying trapped inside
the main terminal workspace.

That means you can:

- move Settings to another monitor while keeping terminals visible
- use normal OS snapping and maximize behavior
- leave Settings open while you continue working in the main window

The settings controls still apply live, and `Revert & Close` still discards the
changes from the current settings session.
