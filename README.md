<p align="center">
  <img src="https://raw.githubusercontent.com/detroittommy879/aicodeprep-gui/main/aicodeprep_gui/images/aicp-transparent-min.png" alt="AICodePrep GUI" width="520">
</p>

<p align="center">
  <b>Pick your files. Generate one clean context block. Paste it into any AI chat.</b>
</p>

<p align="center">
  <a href="https://pypi.org/project/aicodeprep-gui/"><img src="https://img.shields.io/pypi/v/aicodeprep-gui?color=7c3aed&label=PyPI" alt="PyPI version"></a>
  <a href="https://pypi.org/project/aicodeprep-gui/"><img src="https://img.shields.io/pypi/pyversions/aicodeprep-gui?color=3b82f6" alt="Python versions"></a>
  <a href="https://github.com/detroittommy879/aicodeprep-gui/stargazers"><img src="https://img.shields.io/github/stars/detroittommy879/aicodeprep-gui?style=flat&color=eab308" alt="GitHub stars"></a>
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-22c55e" alt="Platforms">
  <a href="https://aicp.wuu73.org"><img src="https://img.shields.io/badge/docs-aicp.wuu73.org-db2777" alt="Docs"></a>
</p>

<p align="center">
  <a href="https://aicp.wuu73.org">Documentation</a> ·
  <a href="#install">Install</a> ·
  <a href="CHANGELOG.md">Changelog</a> ·
  <a href="https://wuu73.org/hello.html">Website</a>
</p>

---

AICodePrep is a small desktop app for anyone who codes with AI chat. When a bug or design question spans many files, you open the folder, check the files you want, and click **Generate Context**. You get one organized block (files separated by XML tags) on your clipboard, ready to paste into ChatGPT, Claude, Gemini, AI Studio, OpenRouter or anything else.

<!-- TODO(Tom): add the Hacker News link, e.g. "Featured on Hacker News: <link>" -->
Used daily by its author and a growing community of developers.

![AICodePrep main window](https://raw.githubusercontent.com/detroittommy879/aicodeprep-gui/main/scrs/n1.png)

## Why use it

- **You control the context.** Smart defaults skip `node_modules`, build output and other noise. You decide the rest.
- **Smarter answers.** Models often reason better without tools and agent scaffolding. Give them clean context and let them think.
- **Save money.** Use frontier models in their free or flat-rate web chats instead of paying per token.
- **Compare models.** Paste the same context into several chats and pick the best answer.
- **Works beside any editor.** VS Code, Cursor, Windsurf, PyCharm, Zed, a terminal. It is a standalone app, not a plugin.
- **Fast.** A bundled Rust worker handles scanning and context generation, with an automatic Python fallback.

## Install

```bash
uv tool install aicodeprep-gui
```

or

```bash
pipx install aicodeprep-gui
```

Pick one method and stick with it. Python 3.9 to 3.13 is supported.

Don't want to deal with Python? [This setup script](https://wuu73.org/vibe) gets a computer ready for AI coding and can install AICodePrep for you.

## Use it

```bash
aicp                    # open the current folder
aicp path/to/project    # open another folder
aicp --skipui           # generate context without the GUI
aicp --help             # all options
```

1. Open a project with `aicp`, or right-click a folder (the app can add this to Explorer, Finder or your Linux file manager).
2. Review the pre-checked files and adjust.
3. Add a prompt or pick a saved preset.
4. Click **Generate Context** and paste into your AI chat.

The output is also saved to `.aicp/context_block.md`.

## Configuration

Drop an `aicodeprep-gui.toml` in your project root to tune scanning:

```toml
max_file_size = 2000000
code_extensions = [".py", ".js", ".ts", ".html", ".css", ".rs"]
exclude_patterns = ["build/", "dist/", "*.log", "node_modules/", ".venv/"]
default_include_patterns = ["README.md", "main.py", "src/**/*.py"]
```

## Free and Pro

The free app covers the whole core workflow. Optional Pro features add extras for heavy use, such as prompts above and below the context, syntax highlighting in the preview, Flow Studio and built-in AI chat. See [Pro Features](https://aicp.wuu73.org/pro-features/).

## Development

```bash
git clone https://github.com/detroittommy879/aicodeprep-gui
cd aicodeprep-gui
uv run aicodeprep-gui   # run from source
uv run pytest           # run the tests
```

| Path | What's there |
| --- | --- |
| `aicodeprep_gui/` | The app (PySide6) |
| `rust_worker/` | Rust worker for fast scanning and context building |
| `tests/` | Pytest suite, including GUI screenshot tests |
| `docs/` | Documentation site source ([MkDocs Material](https://squidfunk.github.io/mkdocs-material/)) |
| `dev-docs/` | Maintainer notes: releases, Rust builds, metrics, docs deployment |

Preview the docs locally:

```bash
uv run --with-requirements requirements-docs.txt mkdocs serve
```

Bug reports, feature ideas and pull requests are welcome.

## Support

If AICodePrep saves you time, a Pro license or a [sponsorship](https://wuu73.org/hello.html) helps keep it going.

## License

[Sustainable License](SUSTAINABLE-LICENSE): free for personal and commercial use, you may use the output commercially, and you may keep and modify the source. You may not sell, redistribute or host the software as a service.
