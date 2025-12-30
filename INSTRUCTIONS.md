# AICodePrep-GUI Installation Instructions

Thank you for downloading AICodePrep-GUI! This guide will walk you through the installation process. Please choose the instructions for your operating system.

For the easiest installation, please use the included installer scripts. For advanced users, manual command-line instructions are also provided.

---

## ★ Windows Installation

### Easiest Method (Recommended)

1.  **Install Python:** Double-click the included Python installer file (e.g., `python-3.13.5-amd64.exe`).
    - **IMPORTANT:** In the first screen of the Python installer, make sure to check the box at the bottom that says **"Add python.exe to PATH"**.
    - Follow the on-screen instructions to complete the installation.
2.  **Install the App:** Once Python is installed, simply double-click the `INSTALLER_Windows.bat` script. A command window will open, show the installation progress, and close when finished.

### Manual Method (Advanced)

If you prefer to install using the command line:

1.  **Install Python:** Follow step 1 from the "Easiest Method" above, ensuring you add Python to your PATH.
2.  **Open a Fresh Terminal:** Open a new Command Prompt or PowerShell window. **Do not reuse an old one.**
3.  **Install `pipx`:** This tool installs Python applications in a clean, isolated environment.
    ```shell
    py -m pip install --user pipx
    ```
4.  **Add `pipx` to your PATH:** This makes sure you can run `pipx` commands from anywhere.
    ```shell
    py -m pipx ensurepath
    ```
5.  **Open another Fresh Terminal:** Close your current terminal and open a new one to ensure the PATH changes are loaded.
6.  **Install `aicodeprep-gui`:**
    ```shell
    pipx install aicodeprep-gui
    ```

---

## ★ macOS Installation

### Easiest Method (Recommended)

Simply double-click the `INSTALLER_MacOS.sh` script. Your Mac may ask for permission to run it. The script will handle installing dependencies (like Homebrew and `pipx`) and the application itself.

### Manual Method (Advanced)

1.  **Install Homebrew:** If you don't have it, open Terminal and run:
    ```shell
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```
2.  **Install `pipx`:**
    ```shell
    brew install pipx
    ```
3.  **Add `pipx` to your PATH:**
    ```shell
    pipx ensurepath
    ```
4.  **Open a Fresh Terminal:** Close the current Terminal window and open a new one.
5.  **Install `aicodeprep-gui`:**
    ```shell
    pipx install aicodeprep-gui
    ```

---

## ★ Linux Installation

### Easiest Method (Recommended)

1.  Open a terminal in the directory where you extracted these files.
2.  Make the installer script executable:
    ```shell
    chmod +x INSTALLER_Linux.sh
    ```
3.  Run the script:
    ```shell
    ./INSTALLER_Linux.sh
    ```
    The script will detect your distribution's package manager (e.g., `apt`, `dnf`, `pacman`) and ask for your password to install dependencies like `python3-pip` if they are missing.

### Manual Method (Advanced)

1.  **Install Python and Pip:** Use your distribution's package manager.
    - **Debian/Ubuntu:** `sudo apt update && sudo apt install python3 python3-pip -y`
    - **Fedora:** `sudo dnf install python3 python3-pip -y`
    - **Arch:** `sudo pacman -Syu python python-pip --noconfirm`
2.  **Install `pipx`:**
    ```shell
    python3 -m pip install --user pipx
    ```
3.  **Add `pipx` to your PATH:**
    ```shell
    python3 -m pipx ensurepath
    ```
4.  **Open a Fresh Terminal:** Close your current terminal and open a new one.
5.  **Install `aicodeprep-gui`:**
    ```shell
    pipx install aicodeprep-gui
    ```

---

## ✔ After Installation: Running the App

After a successful installation, you **must open a new terminal window**.

You can now run the app from any folder on your system by opening a terminal in that folder and typing:

```shell
aicp
```

...or the longer command `aicodeprep-gui`.

## ✔ Add Right-Click "Open With..." Functionality (Optional, but awesome!)

For the best experience, add the right-click context menu to your file manager.

- **Windows:**

  1.  Run the app (`aicp`).
  2.  In the application's menu bar, go to `File` -> `Install Right-Click Menu...`.
  3.  Follow the on-screen instructions. A UAC prompt will appear, as this requires administrator privileges to modify the registry.

- **macOS:**

  1.  After successfully installing the application, find the `AICodePrep.workflow` file that was included with your download.
  2.  **Double-click `AICodePrep.workflow`**.
  3.  A dialog will appear asking if you want to install the "AICodePrep" Quick Action. Click **Install**.
  4.  You can now right-click any folder in Finder and find the action under the **Quick Actions** menu.
      _(Note: The `File` menu option inside the app does not currently work for this on macOS, so you must double-click the `.workflow` file.)_

- **Linux (Nautilus File Manager):**

  1.  This feature is designed for the Nautilus file manager, which is default on GNOME, Ubuntu, and Cinnamon desktops.
  2.  Run the app (`aicp`).
  3.  In the application's menu bar, go to `File` -> `Install File Manager Action...`.
  4.  Use the "Install Nautilus Script" button.
  5.  You may need to restart Nautilus (`nautilus -q`) or log out and back in for the script to appear in your right-click menu.

- **Linux (Other File Managers):**
  If you use a different file manager (like Dolphin, Thunar, etc.), the automated installer might not work. However, you can likely add a custom action manually. Ask an AI assistant for help! For example, you could ask:
  > "How do I add a custom right-click action to the Thunar file manager on XFCE that runs the command `aicp %f` on a selected folder?"
