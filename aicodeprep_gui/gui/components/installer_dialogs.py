"""OS-specific installer dialogs for right-click context menu integration."""

import platform
import logging
from PySide6 import QtWidgets, QtCore


class RegistryManagerDialog(QtWidgets.QDialog):
    """Windows context menu registry management dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Windows Context Menu Manager")
        self.setMinimumWidth(450)

        self.layout = QtWidgets.QVBoxLayout(self)

        info_text = (
            "This tool can add or remove a right-click context menu item in "
            "Windows Explorer to open `aicodeprep-gui` in any folder.<br><br>"
            "<b>Note:</b> This operation requires administrator privileges. "
            "A UAC prompt will appear."
        )
        self.info_label = QtWidgets.QLabel(info_text)
        self.info_label.setWordWrap(True)
        self.layout.addWidget(self.info_label)

        # Add custom menu text input
        menu_text_label = QtWidgets.QLabel("Custom menu text:")
        self.layout.addWidget(menu_text_label)

        self.menu_text_input = QtWidgets.QLineEdit()
        self.menu_text_input.setPlaceholderText("Open with aicodeprep-gui")
        self.menu_text_input.setText("Open with aicodeprep-gui")
        self.menu_text_input.setToolTip(
            "Enter the text that will appear in the right-click context menu")
        self.layout.addWidget(self.menu_text_input)

        # Add some spacing
        self.layout.addSpacing(10)

        # Classic menu checkbox and help icon
        self.classic_menu_checkbox = QtWidgets.QCheckBox(
            "Enable Classic Right-Click Menu (for Windows 11)")
        self.classic_menu_checkbox.setChecked(True)
        classic_help = QtWidgets.QLabel(
            f"<b style='color:#0078D4; font-size:{14 + (getattr(self.parent(), 'font_size_multiplier', 0))}px; cursor:help;'>?</b>")
        classic_help.setToolTip(
            "Restores the full right-click menu in Windows 11, so you don't have to click 'Show more options' to see this app's menu item.")
        classic_help.setAlignment(QtCore.Qt.AlignVCenter)
        classic_layout = QtWidgets.QHBoxLayout()
        classic_layout.setContentsMargins(0, 0, 0, 0)
        classic_layout.addWidget(self.classic_menu_checkbox)
        classic_layout.addWidget(classic_help)
        classic_layout.addStretch()
        self.layout.addLayout(classic_layout)

        self.status_label = QtWidgets.QLabel("Ready.")
        self.status_label.setStyleSheet("font-style: italic;")

        self.install_button = QtWidgets.QPushButton("Install Right-Click Menu")
        self.install_button.clicked.connect(self.run_install)

        self.uninstall_button = QtWidgets.QPushButton(
            "Uninstall Right-Click Menu")
        self.uninstall_button.clicked.connect(self.run_uninstall)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.install_button)
        button_layout.addWidget(self.uninstall_button)

        self.layout.addLayout(button_layout)
        self.layout.addWidget(self.status_label)

    def _run_action(self, action_name):
        """Run registry action with proper privilege handling."""
        try:
            from aicodeprep_gui import windows_registry

            enable_classic = self.classic_menu_checkbox.isChecked()
            if windows_registry.is_admin():
                # Already running as admin, just do the action
                if action_name == 'install':
                    custom_text = self.menu_text_input.text().strip()
                    success, message = windows_registry.install_context_menu(
                        custom_text if custom_text else None,
                        enable_classic_menu=enable_classic
                    )
                else:
                    success, message = windows_registry.remove_context_menu()

                self.status_label.setText(message)
                if success:
                    QtWidgets.QMessageBox.information(self, "Success", message)
                else:
                    QtWidgets.QMessageBox.warning(self, "Error", message)
            else:
                # Not admin, need to elevate
                if action_name == 'install':
                    custom_text = self.menu_text_input.text().strip()
                    success, message = windows_registry.run_as_admin(
                        action_name,
                        custom_text if custom_text else None,
                        enable_classic_menu=enable_classic
                    )
                else:
                    success, message = windows_registry.run_as_admin(
                        action_name)
                self.status_label.setText(message)
                if success:
                    # Close the main app window as a new elevated process will take over
                    if self.parent():
                        self.parent().close()
        except ImportError:
            QtWidgets.QMessageBox.critical(
                self, "Error", "Windows registry module not available.")
            logging.error("windows_registry module not found")
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"An error occurred: {e}")
            logging.error(f"Registry operation failed: {e}")

    def run_install(self):
        """Install the context menu."""
        self._run_action('install')

    def run_uninstall(self):
        """Remove the context menu."""
        self._run_action('remove')


class MacInstallerDialog(QtWidgets.QDialog):
    """macOS Quick Action installer dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("macOS Quick Action Manager")
        self.setMinimumWidth(450)
        self.layout = QtWidgets.QVBoxLayout(self)

        info_text = (
            "This tool installs or removes a <b>Quick Action</b> to open `aicodeprep-gui` "
            "from the right-click menu in Finder (under Quick Actions or Services).<br><br>"
            "The action is installed in your user's Library folder, so no administrator "
            "privileges are required."
        )
        self.info_label = QtWidgets.QLabel(info_text)
        self.info_label.setWordWrap(True)
        self.layout.addWidget(self.info_label)
        self.layout.addSpacing(10)

        self.install_button = QtWidgets.QPushButton("Install Quick Action")
        self.install_button.clicked.connect(self.run_install)

        self.uninstall_button = QtWidgets.QPushButton("Uninstall Quick Action")
        self.uninstall_button.clicked.connect(self.run_uninstall)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.install_button)
        button_layout.addWidget(self.uninstall_button)
        self.layout.addLayout(button_layout)

    def run_install(self):
        """Install the Quick Action."""
        try:
            from aicodeprep_gui import macos_installer
            success, message = macos_installer.install_quick_action()
            if success:
                QtWidgets.QMessageBox.information(self, "Success", message)
            else:
                QtWidgets.QMessageBox.warning(self, "Error", message)
        except ImportError:
            QtWidgets.QMessageBox.critical(
                self, "Error", "macOS installer module not available.")
            logging.error("macos_installer module not found")
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"An error occurred: {e}")
            logging.error(f"macOS installer operation failed: {e}")

    def run_uninstall(self):
        """Remove the Quick Action."""
        try:
            from aicodeprep_gui import macos_installer
            success, message = macos_installer.uninstall_quick_action()
            if success:
                QtWidgets.QMessageBox.information(self, "Success", message)
            else:
                QtWidgets.QMessageBox.warning(self, "Error", message)
        except ImportError:
            QtWidgets.QMessageBox.critical(
                self, "Error", "macOS installer module not available.")
            logging.error("macos_installer module not found")
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"An error occurred: {e}")
            logging.error(f"macOS installer operation failed: {e}")


class LinuxInstallerDialog(QtWidgets.QDialog):
    """Linux file manager integration dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Linux File Manager Integration")
        self.setMinimumWidth(500)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.tabs = QtWidgets.QTabWidget()

        # Automated Installer Tab
        automated_tab = QtWidgets.QWidget()
        automated_layout = QtWidgets.QVBoxLayout(automated_tab)
        self.tabs.addTab(automated_tab, "Automated Setup")

        info_text = QtWidgets.QLabel(
            "This tool can attempt to install a context menu script for your file manager."
        )
        info_text.setWordWrap(True)
        automated_layout.addWidget(info_text)
        automated_layout.addSpacing(10)

        self.nautilus_group = QtWidgets.QGroupBox(
            "Nautilus (GNOME, Cinnamon, etc.)")
        nautilus_layout = QtWidgets.QVBoxLayout(self.nautilus_group)

        self.install_nautilus_btn = QtWidgets.QPushButton(
            "Install Nautilus Script")
        self.install_nautilus_btn.clicked.connect(self.run_install_nautilus)
        self.uninstall_nautilus_btn = QtWidgets.QPushButton(
            "Uninstall Nautilus Script")
        self.uninstall_nautilus_btn.clicked.connect(
            self.run_uninstall_nautilus)

        nautilus_layout.addWidget(self.install_nautilus_btn)
        nautilus_layout.addWidget(self.uninstall_nautilus_btn)

        automated_layout.addWidget(self.nautilus_group)
        automated_layout.addStretch()

        # Check if Nautilus is available
        try:
            from aicodeprep_gui import linux_installer
            if not linux_installer.is_nautilus_installed():
                self.nautilus_group.setDisabled(True)
                self.nautilus_group.setToolTip(
                    "Nautilus file manager not detected in your system's PATH.")
        except ImportError:
            self.nautilus_group.setDisabled(True)
            self.nautilus_group.setToolTip(
                "Linux installer module not available.")

        # Manual Instructions Tab
        manual_tab = QtWidgets.QWidget()
        manual_layout = QtWidgets.QVBoxLayout(manual_tab)
        self.tabs.addTab(manual_tab, "Manual Instructions")

        manual_text = QtWidgets.QLabel(
            "If your file manager is not listed above, you can likely add a custom action manually. "
            "Create a new executable script with the content below and add it to your file manager's "
            "scripting or custom actions feature. The selected folder path will be passed as the first argument ($1)."
        )
        manual_text.setWordWrap(True)
        manual_layout.addWidget(manual_text)

        script_box = QtWidgets.QPlainTextEdit()
        try:
            from aicodeprep_gui import linux_installer
            script_box.setPlainText(linux_installer.NAUTILUS_SCRIPT_CONTENT)
        except ImportError:
            script_box.setPlainText("# Linux installer module not available")
        script_box.setReadOnly(True)
        # Use monospace if available
        script_box.setFont(QtWidgets.QApplication.instance().font())
        manual_layout.addWidget(script_box)

        self.layout.addWidget(self.tabs)

    def run_install_nautilus(self):
        """Install Nautilus script."""
        try:
            from aicodeprep_gui import linux_installer
            success, message = linux_installer.install_nautilus_script()
            if success:
                QtWidgets.QMessageBox.information(self, "Success", message)
            else:
                QtWidgets.QMessageBox.warning(self, "Error", message)
        except ImportError:
            QtWidgets.QMessageBox.critical(
                self, "Error", "Linux installer module not available.")
            logging.error("linux_installer module not found")
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"An error occurred: {e}")
            logging.error(f"Linux installer operation failed: {e}")

    def run_uninstall_nautilus(self):
        """Remove Nautilus script."""
        try:
            from aicodeprep_gui import linux_installer
            success, message = linux_installer.uninstall_nautilus_script()
            if success:
                QtWidgets.QMessageBox.information(self, "Success", message)
            else:
                QtWidgets.QMessageBox.warning(self, "Error", message)
        except ImportError:
            QtWidgets.QMessageBox.critical(
                self, "Error", "Linux installer module not available.")
            logging.error("linux_installer module not found")
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"An error occurred: {e}")
            logging.error(f"Linux installer operation failed: {e}")


def get_installer_dialog_for_platform(parent=None):
    """Factory function to get the appropriate installer dialog for the current platform."""
    system = platform.system()

    if system == "Windows":
        return RegistryManagerDialog(parent)
    elif system == "Darwin":
        return MacInstallerDialog(parent)
    elif system == "Linux":
        return LinuxInstallerDialog(parent)
    else:
        return None
