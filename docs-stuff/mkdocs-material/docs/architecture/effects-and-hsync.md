# Effects System and HSync Notes

This document explains how the visual effects pipeline currently works in
`w111erd`, what the hsync/sine-wave effect is actually doing, and what has been
tried so far to fix the remaining scroll-smear bug.

## Short answer first

Yes: the hsync effect is currently applied to a hidden bitmap-like copy of the
visible terminal output.

More specifically:

- `xterm.js` still renders the terminal normally into its own internal canvases
- the app gathers those live `xterm` canvases each animation frame
- those canvases are composited into an offscreen canvas
- the effect then redraws that composited image into a visible post-process
  canvas with a horizontal line shift
- while the post-process canvas is active, the underlying `.xterm-screen` is
  made invisible with `opacity: 0`

So the effect is not reading PTY text and repainting glyphs itself. It is
warping a canvas snapshot of what `xterm.js` already drew.

## Files involved

- `src/App.tsx`
- `src/components/TerminalPane.tsx`
- `src/plugins/effects/gradient.ts`
- `src/plugins/effects/simpleNoise.ts`
- `src/plugins/effects/terminalHsync.ts`
- `src/styles.css`

## Effects pipeline in general

There are three different kinds of visual effects in the app right now.

### 1. Background effect: terminal gradient

File: `src/plugins/effects/gradient.ts`

This is the simplest layer.

- it targets the `#terminal-workspace` element directly
- it changes that element's CSS background
- if gradient animation is enabled, it also changes CSS animation/background-size

This effect does not touch terminal glyph canvases at all. It only changes the
background behind them.

### 2. Workspace overlay effect: simple noise

Files:

- `src/plugins/effects/simpleNoise.ts`
- `src/styles.css` (`#simple-noise-canvas`)

This effect uses a dedicated canvas that sits over the terminal workspace.

Order:

1. find `#simple-noise-canvas`
2. size it to the terminal workspace bounds
3. generate a low-resolution noise frame
4. scale that low-resolution frame up into the visible overlay canvas
5. control opacity using the configured amount

This layer is global to the terminal workspace, not per-terminal-pane.

### 3. Per-terminal post-process effect: hsync/sine-wave

Files:

- `src/components/TerminalPane.tsx`
- `src/plugins/effects/terminalHsync.ts`

This one is the most complicated because it is attached to each terminal pane.

Order:

1. `TerminalPane` creates the normal `xterm.js` terminal
2. `xterm.js` renders into its own internal canvases inside `.xterm-screen`
3. `TerminalPane` also owns a separate `<canvas class="terminal-postprocess-canvas">`
4. when hsync is enabled for a visible pane, a render loop starts
5. each frame:
   - query `.xterm-screen canvas`
   - measure those canvases relative to their host
   - draw them into an offscreen composite canvas
   - redraw that composite one scanline at a time with a sine-based x-offset
   - show the post-process canvas
   - hide the real `.xterm-screen` by setting its opacity to `0`

That means the displayed terminal is the post-processed copy, not the original
`xterm` canvas, while hsync is active.

## Current hsync implementation

Current file: `src/plugins/effects/terminalHsync.ts`

The current implementation is intentionally simple:

- use an offscreen 2D composite canvas
- copy all live `xterm` canvases into that composite using their measured DOM
  offsets
- clear the visible post-process canvas
- draw the composite back out one horizontal line at a time
- each line is shifted left/right by a sine wave based on:
  - `shiftRange`
  - `wavePeriod`
  - `speed`

In other words, the current renderer is:

- canvas-to-canvas
- scanline-based
- not glyph-aware
- not PTY-aware
- not buffer-aware

## What has been tried so far

There have been three meaningful hsync attempts.

### Attempt 1: WebGL fullscreen shader over a composite texture

Original direction:

- composite `xterm` canvases into a temporary canvas
- upload that canvas as a WebGL texture
- run a fullscreen fragment shader that samples the texture with a shifted `x`
  coordinate per line

What went wrong:

- the effect looked like old text was being left behind after scrolling
- the bug strongly resembled stale alpha or stale frame contents

### Attempt 2: better layer measurement plus blending changes

The first fix pass tried to solve two likely causes:

1. the original compositor was drawing source canvases as if every layer started
   at `(0, 0)`
2. blending state could have been preserving semi-transparent edges from older
   frames

Changes made:

- added live DOM measurement of the `xterm` canvases
- drew each layer using measured offsets
- explicitly disabled WebGL blending for the fullscreen replacement pass

Why this still failed:

- the visual artifact the user reported still looked like scroll-time overdraw
- in practice the new composition rules were not enough

### Attempt 3: remove the shader and switch to a simpler 2D line renderer

The latest pass simplified the path on purpose:

- remove the WebGL shader from the hsync renderer
- keep an offscreen composite canvas
- redraw the final frame line-by-line with 2D canvas drawing
- clear the visible target canvas before every frame

Why this still appears unresolved:

- the user reports no visible improvement
- that suggests the stale-content problem may not be coming only from the final
  post-process canvas
- the stale content may already exist in the source `xterm` canvases at the
  moment they are sampled, or the sampling timing may be racing scroll updates

## What the remaining bug probably is

The symptom reported by the user is:

- once terminal output reaches the bottom and starts scrolling
- new text appears to draw on top of old text
- it looks as though no erase/scroll cleanup happened

The most likely remaining explanations are:

### A. We are sampling `xterm` in the middle of its own scroll/update cycle

If the hsync loop grabs the `xterm` canvases before `xterm` has completed the
visual scroll invalidation for that frame, the effect will faithfully copy a bad
intermediate frame.

### B. One of the source layers is itself preserving stale pixels

`xterm.js` uses multiple internal canvases/layers. If one of those layers is not
fully invalidated the way we assume during scroll, compositing them reproduces
the stale line data exactly.

### C. The "hide source / show post-process copy" swap is still too optimistic

The app currently does:

- source visible until processed frame succeeds
- then source opacity `0`
- post-process canvas visible

That is correct in principle, but it still assumes every processed frame is a
good snapshot.

## Debugging guidance for the next pass

Useful places to inspect:

- `TerminalPane` hsync enable/disable lifecycle
- timing around `refreshTerminal("hsync enabled")`
- timing around PTY output chunks and `scheduleHsyncRefresh(...)`
- whether `xterm` scroll output needs a delayed capture after paint

Good experiments for later:

1. force a one-frame or two-frame delayed capture after output/scroll
2. capture only the final `xterm` canvas layer if one layer is authoritative
3. add a "freeze source canvas snapshots to disk" debug path for affected panes
4. temporarily keep the source visible side-by-side with the processed output to
   prove whether the stale image is already present before post-processing
5. disable the effect during active scroll and re-enable after the frame settles

## What this document is claiming with confidence

- the effect is currently post-processing a canvas snapshot, not terminal text
- the visible hsync output is drawn into a dedicated post-process canvas
- the underlying `xterm` screen is hidden while that post-process canvas is in
  use
- multiple fix passes were attempted already
- the remaining failure almost certainly involves source-frame timing or source
  layer invalidation, not just "forgot to clear the final visible canvas"

## Related logging

The app now routes debug logging to a real backend log file when debug logging is
enabled in Settings.

That should make the next hsync pass easier to instrument without relying only on
the console.
