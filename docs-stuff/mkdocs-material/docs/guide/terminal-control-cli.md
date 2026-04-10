# Terminal Control CLI

`w111erdctl` is a local command-line tool for controlling a running `w111erd` window.

It is meant for automation, quick scripting, and AI agents that need a small shell-friendly surface instead of a large tool schema.

## What it can do right now

- list known tabs
- read recent output from a tab
- wait for text to appear in recent output
- wait for a tab to go quiet after output settles
- send text to a tab with or without Enter
- send common control keys like `Ctrl+C`
- list saved presets from the active profile
- run a preset into a selected tab

## Important limits

- `w111erd` must already be running
- the control API is local-only on `127.0.0.1`
- output reads come from the stored recent-output tail, not infinite history
- secret injection and MCP wrappers are not part of this first version yet

## Basic usage

![Screenshot Placeholder: MCP/CLI AI agent connecting and controlling terminal windows](../img/ai-agent-control-placeholder.png)

Run the CLI from the repo with:

```bash
pnpm w111erdctl --help
```

On Windows PowerShell you can also run it directly without installing anything globally:

```powershell
pnpm w111erdctl --help
.\scripts\w111erdctl.ps1 tabs
```

Useful commands:

```bash
pnpm w111erdctl tabs
pnpm w111erdctl read --tab active --lines 120
pnpm w111erdctl wait-for-text --tab active --text "server ready"
pnpm w111erdctl wait-for-quiet --tab active --quiet-ms 1500
pnpm w111erdctl send --tab "Deploy" --text "docker ps" --enter
pnpm w111erdctl key ctrl+c
pnpm w111erdctl presets
pnpm w111erdctl preset-run --label "prod ssh"
```

## Wait commands

The wait commands are polling helpers built on top of `read`. They are useful when a script or agent needs confirmation instead of a fixed sleep.

Wait for output text:

```bash
pnpm w111erdctl wait-for-text --tab active --text "server ready"
pnpm w111erdctl wait-for-text --tab active --text "error" --ignore-case --timeout-ms 30000
```

Wait for output to stop changing:

```bash
pnpm w111erdctl wait-for-quiet --tab active --quiet-ms 1500
pnpm w111erdctl wait-for-quiet --tab Deploy --quiet-ms 2000 --timeout-ms 30000
```

These do not stream backend events. They poll the current stored output tail until the condition is met or the timeout expires.

## Tab selectors

Most commands accept `--tab`.

You can target a tab by:

- `active`
- PTY id like `12`
- tab id
- exact tab title like `Deploy`

If a selector is ambiguous or missing, use `pnpm w111erdctl tabs` first.

## JSON output

Add `--json` when a script or agent wants structured results instead of the default human-readable output.

Examples:

```bash
pnpm w111erdctl tabs --json
pnpm w111erdctl read --tab active --chars 4000 --json
```

## Connection file

When the app starts, it writes a local connection file to:

```text
~/.w111erd/control-api.json
```

The CLI reads the loopback URL and auth token from that file automatically.

## Making the command work in PowerShell

There are two normal ways to do this on Windows.

For repo-local use, stay in the repo and use either of these:

```powershell
pnpm w111erdctl -- tabs
.\scripts\w111erdctl.ps1 tabs
```

Use `pnpm w111erdctl`, not `pnpm exec w111erdctl`. In this workspace, `pnpm exec` does not expose the root package `bin`, while the package script and the PowerShell wrapper both work.

For a global command, link the package once from the repo root:

```powershell
Set-Location G:\ccc\z_terminals\w111erd
pnpm link --global
w111erdctl tabs
Get-Command w111erdctl
```

That is the usual pattern used by CLI-oriented repos. They do not usually add OS detection inside the command itself. Instead they expose a package `bin`, and the package manager creates the right Windows shim for PowerShell and `cmd.exe`.

## Testing from a separate local Claude Code

The repo now includes a Claude Code skill at `.claude/skills/w111erd-terminal-control/`.

Recommended setup:

1. Keep this repo checked out locally.
2. Start `w111erd` normally so it writes `%USERPROFILE%\.w111erd\control-api.json`.
3. In the separate Claude Code environment, either open this repo directly or set `W111ERD_REPO` to this checkout path.
4. Use the skill wrapper script to call the repo CLI.

Windows example:

```powershell
$env:W111ERD_REPO = 'G:\ccc\z_terminals\w111erd'
node .claude/skills/w111erd-terminal-control/scripts/w111erdctl.mjs tabs
node .claude/skills/w111erd-terminal-control/scripts/w111erdctl.mjs read --tab active --lines 80
node .claude/skills/w111erd-terminal-control/scripts/w111erdctl.mjs wait-for-quiet --tab active --quiet-ms 1500
```

If you already linked the package globally, Claude Code can also just call `w111erdctl` directly.

For common multi-step Claude flows, the skill also now includes a higher-level workflow helper:

```powershell
node .claude/skills/w111erd-terminal-control/scripts/workflows.mjs inspect-active-tab --lines 120
node .claude/skills/w111erd-terminal-control/scripts/workflows.mjs interrupt-active-tab --lines 80
node .claude/skills/w111erd-terminal-control/scripts/workflows.mjs run-preset-and-read --label "prod ssh" --tab active --lines 120
```

Those helpers are convenience wrappers around the main CLI. They are useful for agent prompts, but the lower-level `w111erdctl` commands remain the stable interface.
