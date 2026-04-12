# Profiles and Settings

## Settings is a live control panel

Settings now opens in its own native window. It is still a live control panel,
but it is no longer confined to the main terminal window.

The settings window is divided into several tabs, each covering a different part of the app:

- Themes
- App Look
- Terminal
- Fonts
- Layout
- Effects
- Advanced

Changes usually apply while the window is still open, which makes experimentation easier.

## The major settings areas

### Themes

Browse built-in looks, choose where each one applies, and save or export your
own custom theme files per profile.

### App Look

Tune shell surfaces, tabs, preset dock styling, status bar colors, and general control appearance.

### Terminal

Adjust terminal colors, cursor behavior, gradients, and related visual options.

### Fonts

Set typography per zone and adjust terminal font weight and size separately from the rest of the app. The Fonts tab also now has a `V5 Whole-App Fonts` section that can copy one UI font treatment across the shell, tabs, dock, settings, AI Help, and status bar without forcing them all to share one size.

### Layout

Control density and spacing so the interface feels compact or more relaxed.

### Effects

Turn static and noise overlays on or off and tune their intensity.

### Advanced

Toggle features such as:

- color test on startup
- autocomplete suggestions
- GPU acceleration
- debug logging
- keyboard shortcut preset
- paste mode
- terminal close affordance style for non-split views

The keyboard and clipboard section is where you choose whether the app uses platform-style shortcuts or a more terminal-friendly preset on Windows and Linux.

Paste mode controls how clipboard text is sent into the active shell:

- Auto: direct paste on Windows, bracketed paste on macOS and Linux
- Direct: write the text straight to the terminal process
- Bracketed: wrap pasted text so shells that support bracketed paste can treat it differently

## Profiles

Profiles let you keep separate app setups for different uses.

That can be useful if you want one profile for everyday work, one for experiments, and one for a very different visual style.

Each profile keeps its own configuration and session-related state.

That profile storage also now includes its own custom theme folder, so a work
profile and an experiment profile can keep separate saved looks.

## Where config lives

The app uses profile-aware config storage rather than one giant shared file.

The active profile is tracked separately, and each profile gets its own config location under the app's storage area.

The status bar and settings UI can surface the current config path so you can find the active file more easily.

## A note on closing and reverting

Because the settings window applies changes live, closing it is not the same thing as canceling an old-style form. In the detached native Settings window, the inner modal close button is gone so the window behaves more like a normal standalone tool window. If you are experimenting and want to discard the live changes from the current session, use the explicit revert action in the window.
