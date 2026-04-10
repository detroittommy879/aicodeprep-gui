# Terminal Control CLI Architecture

## Goal

`w111erdctl` gives scripts and AI agents a small local command surface for controlling an already running `w111erd` instance.

The design is intentionally CLI-first. MCP can be added later as a wrapper over the same backend API, but it is not the center of the implementation.

## Why this shape

- The app already owns the PTY lifecycle in Rust.
- The app already captures terminal output and can safely write to the PTY.
- A local CLI is easier for agents to use than repeatedly loading MCP schemas.
- The app should keep typed, app-owned control primitives instead of collapsing into a generic `run arbitrary shell` abstraction.

## Current architecture

The implementation has four layers for the shipped runtime, plus an optional Claude-side helper layer for agent ergonomics:

1. `TerminalPane` and the tab store continue to manage visible tabs in the React app.
2. The frontend now sends a lightweight tab snapshot into Tauri whenever the tab list or active tab changes.
3. The Rust backend keeps a control-state registry keyed by PTY id, captures recent PTY output, and exposes an authenticated loopback HTTP API.
4. `scripts/w111erdctl.mjs` reads the local connection file and turns CLI commands into HTTP requests.

For Claude-specific usage, `.claude/skills/w111erd-terminal-control/scripts/` can add higher-level workflow wrappers that compose the core CLI without changing the backend contract.

## Control model

The backend control registry stores:

- PTY id
- tab id
- tab title
- shell label
- active-tab flag
- recent input
- recent output tail
- truncation state for long output
- last update timestamp

This data is enough for a practical first control surface without depending on the React window at request time.

## Local transport

The control API binds to `127.0.0.1` on an ephemeral port.

On startup the app writes `~/.w111erd/control-api.json` with:

- `baseUrl`
- `authToken`
- `updatedAtMs`

The CLI reads that file and sends `Authorization: Bearer ...` with each request.

This is local-machine control only. It is not a remote API.

## Exposed commands

The first implementation focuses on the commands that are immediately useful for agents and automation:

- `status`
- `tabs`
- `read`
- `wait-for-text`
- `wait-for-quiet`
- `send`
- `key`
- `presets`
- `preset-run`

The two wait operations are implemented as CLI-side polling over the existing `read` endpoint. That keeps the backend API small while still giving agents a usable confirmation primitive.

Selectors resolve in this order:

- `active`
- numeric PTY id
- exact tab id
- exact tab title, case-insensitive

## Why presets are backend-loaded

The CLI needs to list and run presets even when no separate frontend bridge is available.

Instead of duplicating preset state in the control sync payload, the backend reads the active profile config directly from the existing profile storage layout and exposes a small preset view.

## Deliberate omissions in this phase

The first pass does not try to do everything from the brainstorming notes.

It intentionally leaves out:

- MCP wrapping
- secret injection
- full history paging by absolute line block
- remote networking
- UI for configuring control access

Those should be layered on the same control core instead of changing the CLI contract again.

## Next logical extensions

- `wait` operations like `wait-for-text` and `wait-for-quiet`
- better output slicing and chunked history reads
- secret slot listing and guarded secret injection
- explicit audit logging for control actions
- optional MCP wrapper that maps one-to-one onto the CLI/backend API
