"""API Key Management Dialog for Flow Studio.

Provides a user-friendly interface to manage API keys for various AI providers.
"""

import logging
from PySide6 import QtWidgets, QtCore, QtGui
from aicodeprep_gui.config import load_api_config, save_api_config, get_api_keys_file


class APIKeyDialog(QtWidgets.QDialog):
    """Dialog for managing API keys for AI providers."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔑 Manage API Keys")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        # Load current config
        self.config = load_api_config()

        self._setup_ui()
        self._load_values()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QtWidgets.QVBoxLayout(self)

        # Info label
        info_label = QtWidgets.QLabel(
            "Configure your API keys for AI providers. Keys are securely stored locally."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; margin-bottom: 10px;")
        layout.addWidget(info_label)

        # Scroll area for providers
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)

        # Store line edits for later access
        self.api_key_fields = {}
        self.base_url_fields = {}

        # OpenRouter
        openrouter_group = self._create_provider_group(
            "OpenRouter",
            "Access to 100+ models from various providers",
            "openrouter",
            "https://openrouter.ai/keys",
            default_base_url="https://openrouter.ai/api/v1"
        )
        scroll_layout.addWidget(openrouter_group)

        # OpenAI
        openai_group = self._create_provider_group(
            "OpenAI",
            "GPT-4, GPT-3.5, and other OpenAI models",
            "openai",
            "https://platform.openai.com/api-keys",
            default_base_url="https://api.openai.com/v1"
        )
        scroll_layout.addWidget(openai_group)

        # Gemini
        gemini_group = self._create_provider_group(
            "Google Gemini",
            "Google's Gemini models",
            "gemini",
            "https://makersuite.google.com/app/apikey",
            default_base_url="https://generativelanguage.googleapis.com/v1beta"
        )
        scroll_layout.addWidget(gemini_group)

        # Custom
        custom_group = self._create_provider_group(
            "Custom / OpenAI-Compatible",
            "Any OpenAI-compatible API endpoint",
            "custom",
            None,
            default_base_url=""
        )
        scroll_layout.addWidget(custom_group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Config file location
        config_path_label = QtWidgets.QLabel(
            f"📁 Config file: <a href='file:///{get_api_keys_file()}'>{get_api_keys_file()}</a>"
        )
        config_path_label.setOpenExternalLinks(True)
        config_path_label.setStyleSheet(
            "color: #64b5f6; font-size: 11px; margin-top: 10px;")
        config_path_label.setTextInteractionFlags(
            QtCore.Qt.TextBrowserInteraction)
        layout.addWidget(config_path_label)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()

        clear_btn = QtWidgets.QPushButton("Clear All")
        clear_btn.setToolTip("Clear all API keys")
        clear_btn.clicked.connect(self._clear_all)
        button_layout.addWidget(clear_btn)

        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QtWidgets.QPushButton("💾 Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save_and_close)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def _create_provider_group(self, title, description, provider_key, get_key_url, default_base_url):
        """Create a group box for a provider."""
        group = QtWidgets.QGroupBox(f"🤖 {title}")
        layout = QtWidgets.QVBoxLayout(group)

        # Description
        desc_label = QtWidgets.QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(desc_label)

        # API Key
        api_key_layout = QtWidgets.QHBoxLayout()
        api_key_label = QtWidgets.QLabel("API Key:")
        api_key_label.setMinimumWidth(80)
        api_key_layout.addWidget(api_key_label)

        api_key_edit = QtWidgets.QLineEdit()
        api_key_edit.setPlaceholderText(f"Enter your {title} API key...")
        api_key_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.api_key_fields[provider_key] = api_key_edit
        api_key_layout.addWidget(api_key_edit)

        # Show/Hide button
        show_btn = QtWidgets.QPushButton("👁")
        show_btn.setFixedWidth(40)
        show_btn.setCheckable(True)
        show_btn.setToolTip("Show/Hide API key")
        show_btn.toggled.connect(
            lambda checked, edit=api_key_edit: edit.setEchoMode(
                QtWidgets.QLineEdit.Normal if checked else QtWidgets.QLineEdit.Password
            )
        )
        api_key_layout.addWidget(show_btn)

        layout.addLayout(api_key_layout)

        # Base URL
        base_url_layout = QtWidgets.QHBoxLayout()
        base_url_label = QtWidgets.QLabel("Base URL:")
        base_url_label.setMinimumWidth(80)
        base_url_layout.addWidget(base_url_label)

        base_url_edit = QtWidgets.QLineEdit()
        base_url_edit.setPlaceholderText(default_base_url or "https://...")
        self.base_url_fields[provider_key] = base_url_edit
        base_url_layout.addWidget(base_url_edit)

        layout.addLayout(base_url_layout)

        # Get API Key link
        if get_key_url:
            link_label = QtWidgets.QLabel(
                f'<a href="{get_key_url}">🔗 Get {title} API Key</a>'
            )
            link_label.setOpenExternalLinks(True)
            link_label.setStyleSheet("font-size: 11px; margin-top: 5px;")
            layout.addWidget(link_label)

        return group

    def _load_values(self):
        """Load current values from config."""
        for provider_key, api_key_field in self.api_key_fields.items():
            provider_config = self.config.get(provider_key, {})
            api_key = provider_config.get("api_key", "")
            base_url = provider_config.get("base_url", "")

            api_key_field.setText(api_key)
            if provider_key in self.base_url_fields:
                self.base_url_fields[provider_key].setText(base_url)

    def _save_and_close(self):
        """Save the configuration and close dialog."""
        try:
            # Update config with new values
            for provider_key, api_key_field in self.api_key_fields.items():
                if provider_key not in self.config:
                    self.config[provider_key] = {}

                self.config[provider_key]["api_key"] = api_key_field.text().strip()

                if provider_key in self.base_url_fields:
                    base_url = self.base_url_fields[provider_key].text(
                    ).strip()
                    if base_url:
                        self.config[provider_key]["base_url"] = base_url

            # Add OpenRouter specific fields if not present
            if "openrouter" in self.config:
                if "site_url" not in self.config["openrouter"]:
                    self.config["openrouter"]["site_url"] = "https://github.com/detroittommy879/aicodeprep-gui"
                if "app_name" not in self.config["openrouter"]:
                    self.config["openrouter"]["app_name"] = "aicodeprep-gui"

            # Save to file
            save_api_config(self.config)

            QtWidgets.QMessageBox.information(
                self,
                "API Keys Saved",
                f"API keys have been saved successfully to:\n\n{get_api_keys_file()}\n\n"
                "You can now use AI nodes in Flow Studio!"
            )

            self.accept()

        except Exception as e:
            logging.error(f"Failed to save API keys: {e}")
            QtWidgets.QMessageBox.critical(
                self,
                "Save Failed",
                f"Failed to save API keys:\n\n{e}"
            )

    def _clear_all(self):
        """Clear all API key fields."""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Clear All Keys",
            "Are you sure you want to clear all API keys?\n\nThis will not save until you click Save.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            for api_key_field in self.api_key_fields.values():
                api_key_field.clear()
