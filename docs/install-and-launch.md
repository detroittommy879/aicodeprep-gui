# Install And Launch

The usual install command is:

```text
uv tool install aicodeprep-gui
```

Then open a project with:

```text
aicp
```

## Install With uv

If you already use `uv`, install AICodePrep as a tool:

```text
uv tool install aicodeprep-gui
```

Upgrade later with:

```text
uv tool upgrade aicodeprep-gui
```

## Install With pipx

`pipx` also works:

```text
pipx install aicodeprep-gui
```

Upgrade later with:

```text
pipx upgrade aicodeprep-gui
```

## Launch

Run it in the current folder:

```text
aicp
```

Run it for another folder:

```text
aicp path/to/project
```

The longer command also works:

```text
aicodeprep-gui
```

## File Explorer Launch

After installing the right-click integration from inside the app, you can open AICodePrep from a folder in your file manager.

- Windows: File Explorer
- macOS: Finder action
- Linux: supported file manager integration

See [Right-Click Integration](right-click-integration.md).

## Python Requirement

AICodePrep is a Python desktop app. Install a supported Python version first if your system does not already have one.

The PyPI package currently supports Python 3.9 through 3.13.
