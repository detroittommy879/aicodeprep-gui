# Data and Privacy Information for aicodeprep-gui

We believe in transparency and respecting your privacy. This document explains what data `aicodeprep-gui` collects and what it does with it.

## Summary (TL;DR)

- We collect **minimal, anonymous data** to count how many people use the app.
- We **DO NOT** collect your code, file contents, file names, project info, or any other personal information.
- The app checks for updates by contacting the official and safe Python package server (pypi.org).
- All your settings, presets, and code selections are stored **locally on your computer only**.

---

## Detailed Breakdown

### What Data is Sent Over the Network?

The application makes two types of network requests:

#### 1. Anonymous Usage Ping

- **What is sent:** On startup, the app sends a single, one-way "ping" to `https://wuu73.org/`. This request contains two pieces of anonymous information:
  1.  A randomly generated anonymous ID (e.g., `a1b2c3d4-...`). This ID is created on the first launch and stored locally on your machine. It has no connection to you or your system.
  2.  A simple timestamp (e.g., `0430pm`).
- **Why:** This helps the developer get a rough, anonymous count of unique application launches. It's a simple way to know if people are finding the tool useful, which helps motivate future development.
- **Privacy:** This request is designed to be completely anonymous and does **not** include your IP address (beyond standard HTTP headers handled by the server), code, file names, or any other sensitive data.

#### 2. Application Update Check

- **What is sent:** The app contacts `https://pypi.org/`, the official Python Package Index, to ask for the latest version number of `aicodeprep-gui`.
- **Why:** To let you know if a new version with bug fixes or new features is available.
- **Privacy:** This is a standard, secure, and common practice for software. It is the same mechanism `pip` uses to find packages.

### What Data is Stored Locally (On Your Computer)?

All data created by the app is stored on your local machine. We never see it.

- **Project-Specific Settings (`.aicodeprep-gui` file):** When you save preferences for a folder, the app creates a `.aicodeprep-gui` file inside that folder. It contains:
  - A list of the relative paths of files you checked.
  - Your last-used window size and layout for that project.
- **Global Application Settings:** Your global preferences are stored in the standard location for application settings on your OS (e.g., Windows Registry, macOS `~/Library/Preferences`, Linux `~/.config`). This includes:
  - Your saved prompt presets.
  - Your dark/light mode preference.
  - The anonymous ID used for the usage ping.
  - The timestamp of the last update check.

### What We Proactively AVOID Collecting

This application is built with privacy in mind. The default configuration is specifically designed to **ignore and exclude** common files and folders that contain secrets and sensitive data, such as:

- `.git/` (your entire git history)
- `node_modules/`, `venv/` (dependencies)
- `.env`, `.npmrc`, `credentials.yaml` (environment variables and credentials)
- `*.key`, `*.pem`, `id_rsa` (private keys)

### Your Control

You are in full control.

- You can inspect the contents of the `.aicodeprep-gui` file and your global settings at any time.
- If you are uncomfortable with the anonymous usage ping, you can block the `wuu73.org` domain in your firewall or hosts file. This will not affect the application's core functionality.

## Questions?

If you have any questions about privacy or data handling, please feel free to [open an issue on GitHub](https://github.com/detroittommy879/aicodeprep-gui/issues).
