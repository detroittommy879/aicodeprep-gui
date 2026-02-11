"""
Individual chat tab widget for AI Chat Dock.
Uses AIClient for OpenAI-compatible API calls.
"""
from PySide6 import QtWidgets, QtGui, QtCore
from ..ai_assist.endpoint_config import get_active_endpoint, set_active_model, load_endpoints
from ..ai_assist.ai_client import AIClient, AIClientError
from .markdown_renderer import ChatMessageDisplay
import logging
import threading


class ChatTabWidget(QtWidgets.QWidget):
    """
    Individual chat tab with model selection, message input, and chat history.
    Uses the same AIClient as the AI rewrite feature.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._endpoint_id = None
        self._selected_model = None
        self._endpoint_config = {}
        self._chat_history = []  # List of {"role": "user" | "assistant", "content": str}
        self._is_streaming = False

        self._setup_ui()
        self.load_endpoint_config()

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Top bar: Model selector and include context checkbox
        top_bar = QtWidgets.QHBoxLayout()

        # Model selector label
        model_label = QtWidgets.QLabel("Model:")
        model_label.setFixedWidth(50)
        top_bar.addWidget(model_label)

        # Model dropdown
        self.model_combo = QtWidgets.QComboBox()
        self.model_combo.setMinimumWidth(150)
        self.model_combo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        top_bar.addWidget(self.model_combo)

        # Include context checkbox
        self.include_context_checkbox = QtWidgets.QCheckBox("Include context")
        self.include_context_checkbox.setChecked(True)
        self.include_context_checkbox.setToolTip("Include the current context block in messages to AI")
        top_bar.addWidget(self.include_context_checkbox)

        # Tab checkbox (for multi-select when sending context to AI)
        self.tab_checkbox = QtWidgets.QCheckBox()
        self.tab_checkbox.setChecked(True)
        self.tab_checkbox.setToolTip("Select this tab when sending context to multiple tabs")
        top_bar.addWidget(self.tab_checkbox)

        # Refresh models button
        self._refresh_button = QtWidgets.QPushButton("↻")
        self._refresh_button.setFixedWidth(25)
        self._refresh_button.setToolTip("Refresh model list")
        self._refresh_button.clicked.connect(self.load_endpoint_config)
        top_bar.addWidget(self._refresh_button)

        layout.addLayout(top_bar)

        # Chat history display
        self.chat_display = ChatMessageDisplay()
        layout.addWidget(self.chat_display, stretch=1)

        # Input area
        input_layout = QtWidgets.QHBoxLayout()

        self.input_text = QtWidgets.QTextEdit()
        self.input_text.setMaximumHeight(100)
        self.input_text.setPlaceholderText("Type your message here...")
        self.input_text.setTabChangesFocus(True)
        input_layout.addWidget(self.input_text, stretch=1)

        # Send button
        self.send_button = QtWidgets.QPushButton("Send")
        self.send_button.setFixedWidth(80)
        self.send_button.clicked.connect(self._send_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        # Status label
        self.status_label = QtWidgets.QLabel()
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666;")
        layout.addWidget(self.status_label)

    def load_endpoint_config(self):
        """Load endpoint configuration and populate model dropdown."""
        self._endpoint_config = get_active_endpoint()
        self._endpoint_id = self._endpoint_config.get("id", "local")

        # Update model dropdown with available models
        self.model_combo.clear()

        # Add a placeholder
        self.model_combo.addItem("-- Loading models --", "")

        # Load models from endpoint
        self._load_models_from_endpoint()

        # Restore previously selected model if any
        saved_model = self._endpoint_config.get("selected_model", "")
        if saved_model:
            idx = self.model_combo.findData(saved_model)
            if idx >= 0:
                self.model_combo.setCurrentIndex(idx)
                self._selected_model = saved_model
            else:
                # Model not in list, add it
                self.model_combo.addItem(saved_model, saved_model)
                self.model_combo.setCurrentIndex(self.model_combo.count() - 1)
                self._selected_model = saved_model

        # If no models loaded and no saved model, set a default
        if not self._selected_model and self.model_combo.count() == 1:
            # Common model names to try
            common_models = ["gpt-3.5-turbo", "gpt-4", "claude-3-haiku", "claude-3-sonnet"]
            for model in common_models:
                self.model_combo.addItem(model, model)
            self.model_combo.setCurrentIndex(0)

    def _load_models_from_endpoint(self):
        """Load models from the endpoint URL using AIClient."""
        url = self._endpoint_config.get("url", "")
        api_key = self._endpoint_config.get("api_key", "")

        if not url:
            logging.warning("No endpoint URL configured")
            return

        def fetch_models():
            try:
                client = AIClient()
                models = client.list_models(url, api_key=api_key, timeout=5, retries=1)

                # Store model IDs as comma-separated string to avoid Qt type marshaling issues
                model_ids = [m.get("id", "") for m in models if m.get("id")]
                model_str = ",".join(model_ids)

                # Update UI on main thread using string
                QtCore.QMetaObject.invokeMethod(self, "_update_models_list",
                    QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, model_str))
            except Exception as e:
                logging.warning(f"Could not load models from endpoint: {e}")
                # Signal failure with special marker
                QtCore.QMetaObject.invokeMethod(self, "_update_models_list",
                    QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, "ERROR"))

        # Fetch models in background
        thread = threading.Thread(target=fetch_models, daemon=True)
        thread.start()

    @QtCore.Slot(str)
    def _update_models_list(self, model_str: str):
        """Update the model dropdown with fetched models (called on main thread)."""
        # Remove placeholder
        if self.model_combo.count() == 1 and self.model_combo.itemData(0) == "":
            self.model_combo.clear()

        if model_str == "ERROR":
            logging.error("Failed to load models from endpoint")
            return

        if model_str:
            model_ids = model_str.split(",")
            for model_id in model_ids:
                if model_id:
                    self.model_combo.addItem(model_id, model_id)
            logging.info(f"Loaded {len(model_ids)} models from endpoint")
        else:
            logging.warning("No models returned from endpoint")

    def _on_model_changed(self, index: int):
        """Handle model selection change."""
        self._selected_model = self.model_combo.currentData()
        if self._endpoint_id and self._selected_model:
            set_active_model(self._endpoint_id, self._selected_model)

    def set_include_context(self, include: bool):
        """Set the include context checkbox."""
        self.include_context_checkbox.setChecked(include)

    def is_selected(self) -> bool:
        """Check if this tab is selected for multi-tab operations."""
        return self.tab_checkbox.isChecked()

    def set_selected(self, selected: bool):
        """Set the tab selection state."""
        self.tab_checkbox.setChecked(selected)

    def set_dark_mode(self, is_dark: bool):
        """Update theme for dark/light mode."""
        self.chat_display.set_dark_mode(is_dark)

    def _send_message(self):
        """Send message to the AI."""
        content = self.input_text.toPlainText().strip()
        if not content:
            return

        # Clear input
        self.input_text.clear()

        # Add user message to history
        self._chat_history.append({"role": "user", "content": content})
        self.chat_display.append_message("user", content)

        # Disable UI during request
        self._is_streaming = True
        self.send_button.setEnabled(False)
        self.input_text.setEnabled(False)
        self.model_combo.setEnabled(False)
        self.status_label.setText("Thinking...")

        # Build message content
        messages = self._build_messages()

        # Start async response
        self._streaming_response(messages)

    def _build_messages(self) -> list:
        """Build messages list with optional context."""
        messages = [{"role": m["role"], "content": m["content"]} for m in self._chat_history]
        return messages

    def _streaming_response(self, messages: list):
        """Handle AI response."""
        # Use AIClient for API calls
        client = AIClient()
        url = self._endpoint_config.get("url", "")
        api_key = self._endpoint_config.get("api_key", "")
        model = self._selected_model

        if not url or not model:
            self._on_response_error("No endpoint URL or model selected")
            return

        def run_completion():
            try:
                response = client.chat(
                    model=model,
                    messages=messages,
                    base_url=url,
                    api_key=api_key,
                    timeout=60
                )
                self._on_response_complete(response)
            except Exception as e:
                self._on_response_error(str(e))

        thread = threading.Thread(target=run_completion, daemon=True)
        thread.start()

    def _on_response_complete(self, response: str):
        """Handle successful response."""
        QtCore.QMetaObject.invokeMethod(self, "_finish_response",
            QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, response))

    def _on_response_error(self, error: str):
        """Handle response error."""
        QtCore.QMetaObject.invokeMethod(self, "_finish_response",
            QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, f"Error: {error}"))

    @QtCore.Slot(str)
    def _finish_streaming(self, response: str):
        """Finish response and update UI (called on main thread)."""
        self._finish_response(response)

    @QtCore.Slot(str)
    def _finish_response(self, response: str):
        """Finish response and update UI (called on main thread)."""
        self._is_streaming = False
        self.send_button.setEnabled(True)
        self.input_text.setEnabled(True)
        self.model_combo.setEnabled(True)
        self.status_label.clear()

        if response.startswith("Error:"):
            error_msg = response[6:].strip()
            self.status_label.setText(f"Error: {error_msg}")
            self.status_label.setStyleSheet("color: #FF4444;")
            return

        # Add assistant message to history
        self._chat_history.append({"role": "assistant", "content": response})
        self.chat_display.append_message("assistant", response)

    def send_context(self, context_text: str):
        """
        Send context text to this chat (e.g., from "Generate Context to AI" button).
        Appends context as a user message with optional instruction.
        """
        if not context_text:
            return

        # Create a user message with context
        message = f"Context:\n{context_text}\n\nPlease analyze this context and be ready to answer questions about it."

        # Add to history
        self._chat_history.append({"role": "user", "content": message})
        self.chat_display.append_message("user", message)

    def clear_chat(self):
        """Clear chat history."""
        self._chat_history = []
        self.chat_display.clear()
        self.status_label.clear()
