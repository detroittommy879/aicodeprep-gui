# Status Bar and Limits

## What the status bar tells you

The bottom status bar is a quick health readout for the current terminal state.

It can show:

- the active renderer
- whether GPU-backed WebGL is active or the app has fallen back
- whether link detection is on
- whether gradient rendering is enabled
- the configured terminal size in columns and rows
- which tab is active and how many tabs exist
- how many panes are visible in the current layout
- whether debug logging is enabled
- the current terminal font zoom readout

## Zoom controls

On the right side of the status bar there is now a small zoom control block.

Use:

- `-` to zoom terminal text out
- the middle size button to reset back to the default terminal font size
- `+` to zoom terminal text in

These controls use the same zoom behavior as the `View` menu, so whichever
surface you use, the terminal font size changes the same way.

## Renderer and GPU labels

In plain language:

- `Renderer: webgl` means the terminal is using the GPU-backed WebGL path
- `GPU fallback` means GPU use was requested but the app had to fall back to a safer renderer
- `GPU off` means GPU acceleration is disabled for the current terminal runtime

## Links and gradients

If links are active, the status bar reflects that. The same is true for gradient usage, so you can tell at a glance whether a more decorative terminal presentation is currently in effect.

## Current limitations

This is the honest short list of things that are not yet the finished version of themselves:

- AI Help now works as an overlay, but it still depends on whatever OpenAI-compatible provider and model you configure
- the internal effect plugin structure is real, but it is not yet a user-managed plugin system
- planned ideas like remote control and mobile sync are not current app features
- some font-weight reporting still relies on browser-side behavior rather than a full operating-system font inventory

The docs in this site describe the current app, not the roadmap.
