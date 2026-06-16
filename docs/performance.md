# Performance

AICodePrep is meant to feel fast even on large repositories.

The current version uses a Rust worker for the slowest parts of the workflow when the worker is available for your platform.

## What Rust Speeds Up

The Rust worker can handle:

- folder scanning
- ignore/exclude filtering
- context block generation

These are the operations that tend to get slow in large repos with many files.

## Fallback Behavior

Rust acceleration is not required for the app to work.

If the Rust worker is missing, cannot run, or returns an error, AICodePrep falls back to the Python implementation. The goal is that users get the speed improvement when possible, but still get a working app if something goes wrong.

## How To Tell Which Backend Ran

When launched from a terminal, the app logs which backend it used.

For Rust scanning or generation, you should see messages like:

```text
Using Rust worker for directory scan
Using Rust worker for context generation
```

If Rust is unavailable, you should see a fallback message instead:

```text
Rust file scan unavailable, falling back to Python
Rust backend failed, falling back to Python processing
```

The settings window also shows whether the worker is installed and available.

## Platform Packaging

Release builds can bundle worker binaries for common platforms:

- Windows x64
- Linux x64
- Linux ARM64
- macOS Intel
- macOS Apple Silicon

The Python package chooses the matching bundled worker at runtime. If no matching worker exists, the Python path is used.

## What This Is Not

This is not a rewrite of the whole app.

The desktop app is still the same Python/PySide app. Rust is currently used where it helps most: scanning folders and generating the context block quickly.
