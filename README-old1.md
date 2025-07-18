# aicodeprep-gui - AI Code Preparation GUI

_Streamline code sharing with AI chatbots (macOS & Windows & Linux)_

[![GitHub stars](https://img.shields.io/github/stars/detroittommy879/aicodeprep-gui.svg?style=social&label=Stars)](https://github.com/detroittommy879/aicodeprep-gui/stargazers)

**Latest Version: 1.0.0 (June 20, 2025)**

---

## What is aicodeprep-gui?

It is a Code Concatenator, Context Builder, Code Files + questions ---> pasteable prompt.
Its more than that, but that's the gist of it. Developers run into situations where they need to ask a question about some code or project, but they would have to copy and paste each file. If they let an AI coding agent do it, the AI gets so much unnecessary context about tool usage instructions that it dumbs it down too much.

This tool solves a lot of problems and is designed for speed, designed to remove friction. It automates a lot of annoying repetitive things.

Sure, you can just use a more expensive, super smart model, which sometimes will work, just have Claude 4 do everything... but it gets expensive. All of the AI models work better on their web chat interfaces, without tool use or agent abilities. I have theories about why that is but anyways...

aicodeprep-gui or aicp is a cross-platform desktop application that helps developers quickly gather and share their project code with AI chatbots. Instead of manually copying and pasting multiple files just to ask a question, this tool automatically collects relevant code files into a single 'block' + text file, copies it to your clipboard automatically (also writes it to fullcode.txt), and formats it with AI-friendly tags. READY... to paste right into an AI chat, or multiple ones (they are still usually free! you can paste it into 3 different AI chat's and compare the outputs).

You can set presets which quickly add on text to what you typed, so you can do things like click the Cline button to tell the AI you want it to reply with a nice prompt you can just paste right into Cline to make fast changes without all the manual copying, pasting, typing over and over..

Use the smart expensive AI models for the hard stuff, then let Cline, Cursor or whatever agentic system you use, implement the solution.

Basically what this does is get rid of all the little annoying frictions between me asking my question, and giving the AI the code i'm asking about. Without this tool I would have to open each code file, copy, paste it into AI Studio/Gemini/whatever, type the same questions I ask over and over.. I hate the tedious stuff, I want to spend my brain power on better things. That's what this does.

ChatGPT, Gemini 2.5 Pro, o3, Openrouter, I have like 15 tabs open of different web chat's like this and most are free.
(for more info about the workflow, staying free or cheap yet still good: wuu73.org/blog/guide.html)

This helps you "vibe code" faster. Only need to paste one time. It will automatically guess as to which code files you will want for context, but allow you to fine tune it. This might seem pointless ohhh but its not. All of the available agents in IDEs will make the AI dumber by giving it a bunch of information unrelated to your problem.

Or, it won't give it enough information or context from your project.

When you use web chat interfaces, you don't have the giant hidden prompts telling the AI all about how to be an agent, how to edit files, how to use 500 tools, etc. The more of this that is sent with your prompt, the dumber it will be. We can't afford to do that for difficult problems, hard to find bugs, complex tasks. If you ask a question or give it a task via the web chat interface its almost always going to be smarter. This app gets rid of most of the friction between you giving the AI your code files and questions/tasks.

There are many other similar tools that are command line only, and don't have smart file checking and prefs saving, saving which files you chose for next time (when you check more files or uncheck certain ones, it will remember, for next time - this is what the .aicodepre-gui file is for). It even saves the window size and where you dragged the bar in the UI, so you won't have to do that again. Saving time and being less annoying, makes me happy, and probably makes you happy too.

It supports **Windows**, **macOS (M1+)**, and **Linux** with context menu/right-click integration, terminal command 'aicp' and 'aicodeprep-gui'.

---

## ✨ New Features in v1.0.0

- **Modern TOML Configuration System:**

  - Industry-standard TOML configuration replacing custom formats
  - User-customizable settings via `aicodeprep-gui.toml` in project directories
  - Comprehensive default configuration with smart file filtering
  - `.gitignore`-style pattern matching for robust exclusion rules

- **Lazy Loading Performance:**

  - Lightning-fast startup by avoiding scanning of large excluded directories
  - On-demand expansion of folders like `node_modules`, `venv`, etc.
  - Dramatically improved performance for large codebases
  - Users can still manually expand any directory for fine-grained selection

- **Enhanced Global Preset System:**

  - Create and manage reusable prompt presets globally across projects
  - Presets are automatically saved and synced across all project folders
  - Quick preset buttons with ✚ and 🗑️ controls for easy management
  - Default presets include "Debug", "Security check", "Best Practices", etc.

- **Improved File Tree Experience:**

  - Smart auto-expansion of folders containing checked files
  - Better visual feedback with hover effects on checkboxes
  - Binary file detection and automatic exclusion
  - Cleaner, more intuitive folder navigation

- **Enhanced Output Options:**
  - Choose between XML `<code>` tags or Markdown `###` formatting
  - Optional prompt/question text appended to output
  - Intelligent file processing with better error handling

---

## Previous Features (v0.9.x)

- **Dark Mode Support:**

  - Automatic theme detection based on system preferences
  - Manual dark/light mode toggle in the top-right corner
  - Carefully designed dark theme palette for optimal readability

- **PySide6 Migration:**

  - Upgraded to Qt6 via PySide6 for improved performance
  - Modern Qt features and future-proofing
  - Better cross-platform compatibility

- **Persistent Preferences:**

  - Automatically saves window size and selected files in `.aicodeprep-gui` file per project
  - Remembers splitter position and window layout
  - Optional preference saving (can be disabled)

- **Token Counter:**
  - Real-time token estimation as you select/deselect files
  - Helps optimize context size for AI models

---

## Screenshots & Usage

Update coming soon - but you can look at the older version and get an idea for how it is used at these links:

[https://wuu73.org/aicp - the old homepage for the app with old screenshots](https://wuu73.org/aicp)

[Guide on how to code free/cheap, workflow info, etc](https://wuu73.org/blog/guide.html)

---

## Installation

Make sure python is installed on your system, then install pipx. Just google how to do that or ask AI etc. Then open a fresh terminal/cmd window and type:

pipx install aicodeprep-gui

## Mac

```sh
# Install pipx using Homebrew
brew install pipx

# Add pipx to your PATH
pipx ensurepath
```

#### (then close/open a fresh new terminal window)

```sh
pipx install aicodeprep-gui
```

## Windows

Download python from python.org - pick one of the stable versions, 3.11.x is good.

Then try:

```sh
py -m pip install --user pipx
py -m pipx ensurepath
```

(if py doesn't work, try 'python' or 'python3')

Close that terminal window, and open a fresh new one (very important after installing pipx

```sh
pipx install aicodeprep-gui
```

It should say success or something similar or done.

Now that it is installed, you can type 'aicp' + enter in a terminal to run it or aicp path/to/folder/
also aicodeprep-gui works instead of aicp. aicp is shorter, both do the same thing (open the app window in whichever folder you typed it)

A common thing would be when you are using VS Code or Cursor, and whichever agent / agentic coder is pissing you off or acting stupid, go to the VS Code terminal and type 'aicp' to open it for the project you are working on.

## Linux

#### Update package lists and upgrade existing packages

```sh
sudo apt update && sudo apt upgrade -y
```

#### Install pip for Python 3

```sh
sudo apt install python3-pip -y
```

#### Install and Configure pipx

Now, use pip to install pipx. It's best to install it in your user space to avoid needing sudo for Python packages.

```sh
pip3 install --user pipx
```

```sh
pipx ensurepath
```

#### IMPORTANT: After running pipx ensurepath, you must close and reopen your terminal for the PATH changes to take effect.

In a new terminal, type:

```sh
pipx install aicodeprep-gui
```

---

Old instructions for versions below 1.0.0:

1. Download the Linux package from the releases page.
2. Follow the installation instructions in the included README.
3. Use via command line: `aicodeprep-gui [directory]`
4. File manager context menu integration may be available depending on your desktop environment.

### Python Installation

```older version - sti
pip install aicodeprep-gui
aicodeprep-gui  # Run in current directory
aicodeprep-gui /path/to/project  # Run in specific directory

or:

aicp
aicp path/to/project/code/etc
```

---

## Features Summary

- **Cross-platform GUI** for easy visual file selection
- **Smart Preselection** of relevant code files based on configured extensions and exclusions
- **Dark/Light Theme Support** with system preference detection and manual toggle
- **Lazy Loading Tree View** with instant startup and on-demand directory expansion
- **Global Preset Management** for reusable prompt templates across projects
- **TOML Configuration** with `.gitignore`-style pattern matching
- **Preferences Saving** via `.aicodeprep-gui` per folder to remember selections and window layout
- **Token Counter** displays estimated token count in real-time
- **Context Menu Integration** for quick access from file managers
- **Clipboard & File Output** for seamless pasting into AI chatbots
- **Flexible Output Formats** (XML `<code>` tags or Markdown `###` sections)
- **High-DPI Support** with crisp UI scaling on all displays

---

## Usage

1. **Launch:** Open the tool from your project folder's context menu (right-click) or command line.
2. **Review Files:** The tool automatically pre-selects relevant code files and expands folders containing them.
3. **Customize Selection:**
   - Expand/collapse folders as needed
   - Check/uncheck files manually
   - Use **Select All** or **Deselect All** for bulk operations
4. **Choose Format:** Select XML `<code>` or Markdown `###` output format from the dropdown.
5. **Add Prompt (Optional):** Use preset buttons or type custom prompts in the text area.
6. **Process:** Click **Process Selected** to generate output and copy to clipboard.
7. **Preferences:** Toggle "Remember checked files..." to save your selection for next time.

---

## Configuration

You can customize file extensions, directories, and exclusion patterns via an `aicodeprep-gui.toml` file in your project folder. This will override the default configuration.

Example `aicodeprep-gui.toml`:

```toml
max_file_size = 2000000

code_extensions = [".py", ".js", ".ts", ".html", ".css"]

exclude_patterns = [
    "build/",
    "dist/",
    "*.log",
    "temp_*"
]

default_include_patterns = [
    "README.md",
    "main.py"
]
```

Refer to `aicodeprep-gui/data/default_config.toml` for all available configuration options.

---

## Command Line Options

```bash
aicodeprep-gui [directory] [options]

Options:
  -h, --help          Show help message
  -n, --no-copy       Don't copy output to clipboard
  -o, --output FILE   Output filename (default: fullcode.txt)
  -d, --debug         Enable debug logging
```

---

## Contributing

Contributions and pull requests are welcome! Please submit bug reports and feature requests via GitHub Issues.

---

## Support & Donations

If you find this tool useful, consider supporting future development:

| Method   | Address / Link                                                                                    |
| -------- | ------------------------------------------------------------------------------------------------- |
| Bitcoin  | `bc1qkuwhujaxhzk7e3g4f3vekpzjad2rwlh9usagy6`                                                      |
| Litecoin | `ltc1q3z327a3ea22mlhtawmdjxmwn69n65a32fek2s4`                                                     |
| Monero   | `46FzbFckBy9bbExzwAifMPBheYFb37k8ghGWSHqc6wE1BiEz6rQc2f665JmqUdtv1baRmuUEcDoJ2dpqY6Msa3uCKArszQZ` |
| CashApp  | `$lightweb73`                                                                                     |
| Website  | [https://wuu73.org/hello.html](https://wuu73.org/hello.html)                                      |

---
