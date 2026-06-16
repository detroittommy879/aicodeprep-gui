"""
Individual chat tab widget for AI Chat Dock.
Uses AIClient for OpenAI-compatible API calls.
"""
from PySide6 import QtWidgets, QtGui, QtCore
from ..ai_assist.endpoint_config import get_active_endpoint, set_active_model, load_endpoints, get_all_endpoint_ids
from ..ai_assist.ai_client import AIClient, AIClientError
from .markdown_renderer import ChatMessageDisplay
import logging
import threading


class SearchableComboBox(QtWidgets.QComboBox):
    """
    ComboBox with built-in search/filter functionality.
    Allows typing to filter models in the dropdown.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.setDuplicatesEnabled(False)

        # Set up the line edit for searching
        self.lineEdit().setPlaceholderText("Search models...")

        # Use a filter proxy for searching
        self._filter_proxy = QtCore.QSortFilterProxyModel(self)
        self._filter_proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._filter_proxy.setSourceModel(self.model())

        # Connect text changes to filter
        self.lineEdit().textEdited.connect(self._on_search_text)

    def _on_search_text(self, text):
        """Filter models based on search text."""
        self._filter_proxy.setFilterWildcard(f"*{text}*")
        # Show all if search is empty
        if not text.strip():
            self._filter_proxy.setFilterWildcard("")

    def setModel(self, model):
        """Set the source model."""
        self._filter_proxy.setSourceModel(model)
        super().setModel(self._filter_proxy)

    def addItem(self, text, userData=None):
        """Add item through the proxy model."""
        super().addItem(text, userData)

    def findData(self, data, role=QtCore.Qt.UserRole):
        """Find data in source model."""
        # Search in source model and map through proxy
        source_model = self._filter_proxy.sourceModel()
        if not source_model:
            return -1

        for row in range(source_model.rowCount()):
            index = source_model.index(row, 0)
            if source_model.data(index, role) == data:
                # Map to proxy index
                proxy_index = self._filter_proxy.mapFromSource(index)
                return self.model().indexToRow(proxy_index)
        return -1


class StreamingChatDisplay(ChatMessageDisplay):
    """
    Extended ChatMessageDisplay with streaming support.
    Allows appending content incrementally and auto-scrolling.
    """

    def __init__(self, parent=None, is_dark_mode: bool = None):
        super().__init__(parent, is_dark_mode)
        self._streaming_content = ""
        self._streaming_role = ""

    def start_streaming(self, role: str):
        """Start a streaming response from the AI."""
        self._streaming_role = role
        self._streaming_content = ""

        # Style based on role
        colors = self._renderer._colors
        if role == 'user':
            header = f'<div style="color:{colors["heading"]}; font-weight:bold; margin-bottom:8px;">User</div>'
            bg_style = f'background:{colors["code_bg"]};'
        else:
            header = f'<div style="color:#4CAF50; font-weight:bold; margin-bottom:8px;">AI</div>'
            bg_style = ''

        # Store cursor position for auto-scroll
        cursor = self.textCursor()
        self._was_at_bottom = cursor.atEnd()

        # Create placeholder message
        message_html = f'''
        <div style="{bg_style} padding:10px; margin:8px 0; border-radius:5px; line-height:1.6;">
            {header}
            <div style="color:{colors["text"]};">
            </div>
        </div>
        '''
        self.append(message_html)

    def append_stream_chunk(self, chunk: str):
        """Append a chunk of content to the streaming message."""
        self._streaming_content += chunk

        # Escape HTML but preserve line breaks
        escaped = chunk.replace('&', '&amp;').replace(
            '<', '&lt;').replace('>', '&gt;')

        # Get the last block and update its content div
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)

        # Move to the content div (second div inside the message div)
        # Find and update the content
        html = self.toHtml()

        # Since QTextEdit doesn't easily support partial HTML updates,
        # we'll append and use a different approach - append to a temporary
        # message div pattern

        # Actually, let's just re-render the entire message
        # For streaming, we'll just append chunks as they come
        pass  # We'll use a simpler approach below


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
        # List of {"role": "user" | "assistant", "content": str}
        self._chat_history = []
        self._is_streaming = False
        self._request_serial = 0
        self._active_request_token = ""
        self._all_endpoints = {}  # Store all endpoints for per-tab selection

        self._setup_ui()
        self.load_endpoint_config()

        # Set size constraints to prevent stuck/giant windows
        self.setMinimumSize(200, 200)
        self.setMaximumSize(4000, 4000)

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Top bar: Endpoint selector, Model selector, and include context checkbox
        top_bar = QtWidgets.QHBoxLayout()

        # Endpoint selector label
        endpoint_label = QtWidgets.QLabel("Endpoint:")
        endpoint_label.setFixedWidth(60)
        top_bar.addWidget(endpoint_label)

        # Endpoint dropdown - NEW: per-tab endpoint selection
        self.endpoint_combo = QtWidgets.QComboBox()
        self.endpoint_combo.setMinimumWidth(120)
        self.endpoint_combo.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.endpoint_combo.currentIndexChanged.connect(
            self._on_endpoint_changed)
        top_bar.addWidget(self.endpoint_combo)

        # Searchable Model dropdown
        self.model_combo = SearchableComboBox()
        self.model_combo.setMinimumWidth(150)
        self.model_combo.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        top_bar.addWidget(self.model_combo)

        # Separator
        sep = QtWidgets.QLabel("|")
        sep.setStyleSheet("color: #888;")
        top_bar.addWidget(sep)

        # Random buttons for OpenRouter
        self.random_btn = QtWidgets.QPushButton("Random")
        self.random_btn.setFixedWidth(60)
        self.random_btn.setToolTip("Pick a random model")
        self.random_btn.clicked.connect(self._pick_random_model)
        top_bar.addWidget(self.random_btn)

        self.random_free_btn = QtWidgets.QPushButton("Free")
        self.random_free_btn.setFixedWidth(40)
        self.random_free_btn.setToolTip(
            "Pick a random free model (OpenRouter)")
        self.random_free_btn.clicked.connect(self._pick_random_free_model)
        top_bar.addWidget(self.random_free_btn)

        # Include context checkbox
        self.include_context_checkbox = QtWidgets.QCheckBox("Include context")
        self.include_context_checkbox.setChecked(True)
        self.include_context_checkbox.setToolTip(
            "Include the current context block in messages to AI")
        top_bar.addWidget(self.include_context_checkbox)

        # Tab checkbox (for multi-select when sending context to AI)
        self.tab_checkbox = QtWidgets.QCheckBox()
        self.tab_checkbox.setChecked(True)
        self.tab_checkbox.setToolTip(
            "Select this tab when sending context to multiple tabs")
        top_bar.addWidget(self.tab_checkbox)

        # Refresh models button
        self._refresh_button = QtWidgets.QPushButton("↻")
        self._refresh_button.setFixedWidth(25)
        self._refresh_button.setToolTip("Refresh model list")
        self._refresh_button.clicked.connect(self.load_endpoint_config)
        top_bar.addWidget(self._refresh_button)

        layout.addLayout(top_bar)

        # Chat history display - with size policy to prevent giant windows
        self.chat_display = ChatMessageDisplay()
        self.chat_display.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # Set minimum and maximum heights to prevent extreme sizing
        self.chat_display.setMinimumHeight(100)
        self.chat_display.setMaximumHeight(2000)
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

        # Status label - limit height to prevent giant windows
        self.status_label = QtWidgets.QLabel()
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setStyleSheet(
            "color: #FF4444; background: #3a1a1a; padding: 5px; border-radius: 3px;")
        self.status_label.setWordWrap(True)
        # Limit height to prevent giant windows
        self.status_label.setMaximumHeight(80)
        self.status_label.hide()  # Hidden by default
        layout.addWidget(self.status_label)

    def load_endpoint_config(self):
        """Load endpoint configuration and populate endpoint/model dropdowns."""
        # Load ALL endpoints for the dropdown
        self._all_endpoints = load_endpoints()
        endpoints = self._all_endpoints.get("endpoints", {})
        active_id = self._all_endpoints.get("active_endpoint", "local")

        # Populate endpoint dropdown
        self.endpoint_combo.blockSignals(True)
        self.endpoint_combo.clear()

        for endpoint_id, config in endpoints.items():
            name = config.get("name", endpoint_id)
            self.endpoint_combo.addItem(name, endpoint_id)

        # Set to active endpoint (or first one)
        idx = self.endpoint_combo.findData(active_id)
        if idx < 0 and self.endpoint_combo.count() > 0:
            idx = 0
        if idx >= 0:
            self.endpoint_combo.setCurrentIndex(idx)

        self.endpoint_combo.blockSignals(False)

        # Use selected endpoint for this tab
        self._on_endpoint_changed(self.endpoint_combo.currentIndex())

    def _on_endpoint_changed(self, index: int):
        """Handle endpoint selection change - load models for that endpoint."""
        endpoint_id = self.endpoint_combo.currentData()
        if not endpoint_id:
            return

        endpoints = self._all_endpoints.get("endpoints", {})
        if endpoint_id not in endpoints:
            return

        # Get this endpoint's config
        self._endpoint_config = endpoints[endpoint_id].copy()
        self._endpoint_config["id"] = endpoint_id
        self._endpoint_id = endpoint_id

        # Update model dropdown for this specific endpoint
        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        self.model_combo.addItem("-- Loading models --", "")

        # Load models from THIS endpoint only (not all)
        self._load_models_for_endpoint(endpoint_id, self._endpoint_config)

        self.model_combo.blockSignals(False)

    def _load_models_for_endpoint(self, endpoint_id: str, endpoint_config: dict):
        """Load models from a specific endpoint."""
        url = endpoint_config.get("url", "")
        api_key = endpoint_config.get("api_key", "")

        if not url:
            self._update_models_list("ERROR")
            return

        def fetch_and_update():
            try:
                client = AIClient()
                models = client.list_models(
                    url, api_key=api_key, timeout=5, retries=1)

                model_ids = []
                for m in models:
                    model_id = m.get("id", "")
                    if model_id:
                        # Use endpoint prefix to avoid collisions
                        prefixed = f"{endpoint_id}:{model_id}"
                        model_ids.append(prefixed)

                if model_ids:
                    model_str = ",".join(model_ids)
                else:
                    model_str = "ERROR"

                QtCore.QMetaObject.invokeMethod(self, "_update_models_list",
                                                QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, model_str))
            except Exception as e:
                logging.warning(
                    f"Could not load models from {endpoint_id}: {e}")
                QtCore.QMetaObject.invokeMethod(self, "_update_models_list",
                                                QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, "ERROR"))

        # Fetch in background thread
        thread = threading.Thread(target=fetch_and_update, daemon=True)
        thread.start()

    def _load_models_from_endpoint(self, endpoint_id: str, url: str, api_key: str):
        """Load models from a specific endpoint URL using AIClient."""
        if not url:
            return []

        def fetch_models():
            try:
                client = AIClient()
                models = client.list_models(
                    url, api_key=api_key, timeout=5, retries=1)

                # Store model IDs with endpoint prefix
                model_ids = []
                for m in models:
                    model_id = m.get("id", "")
                    if model_id:
                        # Prefix with endpoint ID to avoid collisions
                        prefixed = f"{endpoint_id}:{model_id}"
                        model_ids.append(prefixed)
                return model_ids
            except Exception as e:
                logging.warning(
                    f"Could not load models from {endpoint_id}: {e}")
                return []

        # Fetch models in background and return immediately
        return fetch_models()

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
            # Track seen model names to avoid duplicates
            seen = set()
            models_with_prefix = []
            for model_id in model_ids:
                if model_id:
                    # Extract base model name for deduplication
                    base_name = model_id.split(
                        ':', 1)[1] if ':' in model_id else model_id
                    if base_name not in seen:
                        seen.add(base_name)
                        models_with_prefix.append(model_id)

            # Sort alphabetically by base model name
            models_with_prefix.sort(key=lambda x: x.split(':', 1)[1].lower())

            for model_id in models_with_prefix:
                self.model_combo.addItem(model_id, model_id)
            logging.info(
                f"Loaded {len(models_with_prefix)} unique models (sorted A-Z)")
        else:
            logging.warning("No models returned from endpoint")

    def _on_model_changed(self, index: int):
        """Handle model selection change."""
        model_data = self.model_combo.currentData()
        # Strip prefix if present (e.g., "openrouter:gpt-4" -> "gpt-4")
        if model_data and ':' in model_data:
            self._selected_model = model_data.split(':', 1)[1]
        else:
            self._selected_model = model_data

        # Save the model selection for THIS endpoint (per-tab)
        if self._endpoint_id and self._selected_model:
            set_active_model(self._endpoint_id, self._selected_model)

    def _pick_random_model(self):
        """Pick a random model from the dropdown."""
        count = self.model_combo.count()
        if count > 0:
            import random
            idx = random.randint(0, count - 1)
            self.model_combo.setCurrentIndex(idx)

    def _pick_random_free_model(self):
        """Pick a random free model (OpenRouter models ending with :free)."""
        count = self.model_combo.count()
        free_indices = []
        for i in range(count):
            model_id = self.model_combo.itemData(i)
            if model_id and model_id.endswith(':free'):
                free_indices.append(i)

        if free_indices:
            import random
            idx = random.choice(free_indices)
            self.model_combo.setCurrentIndex(idx)
        else:
            # Fallback to regular random if no free models
            self._pick_random_model()

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
        if self._is_streaming:
            return

        content = self.input_text.toPlainText().strip()
        if not content:
            return

        # Clear input
        self.input_text.clear()

        # Add user message to history and re-render display
        self._chat_history.append({"role": "user", "content": content})
        self.chat_display.set_messages(self._chat_history)

        self._dispatch_ai_request()

    def _dispatch_ai_request(self):
        """Lock UI and start a streaming request using the current chat history."""
        if self._is_streaming:
            return False

        self._request_serial += 1
        request_token = str(self._request_serial)
        self._active_request_token = request_token
        self._is_streaming = True
        self.send_button.setEnabled(False)
        self.input_text.setEnabled(False)
        self.model_combo.setEnabled(False)
        self.status_label.setText("Thinking...")
        self.status_label.show()
        self._emit_metric(
            "ai_chat_request_started",
            {
                "feature": "ai_chat",
                "endpoint_id": self._endpoint_id or "",
                "model": self.get_selected_model(),
                "message_count": len(self._chat_history),
            },
        )
        self._streaming_response(self._build_messages(), request_token)
        return True

    def _find_metrics_target(self):
        widget = self.parentWidget()
        while widget is not None:
            if hasattr(widget, "_send_metric_event"):
                return widget
            widget = widget.parentWidget()
        return None

    def _emit_metric(self, event_type: str, details: dict | None = None):
        target = self._find_metrics_target()
        if target is not None:
            target._send_metric_event(event_type, details=details)

    def get_selected_model(self) -> str:
        return str(self._selected_model or "").strip()

    def _build_messages(self) -> list:
        """Build messages list with optional context."""
        messages = [{"role": m["role"], "content": m["content"]}
                    for m in self._chat_history]
        return messages

    def _streaming_response(self, messages: list, request_token: str):
        """Handle AI response with streaming."""
        # Use AIClient for API calls
        client = AIClient()
        url = self._endpoint_config.get("url", "")
        api_key = self._endpoint_config.get("api_key", "")
        model = self._selected_model

        if not url or not model:
            self._on_response_error(
                request_token, "No endpoint URL or model selected")
            return

        # Create streaming assistant message placeholder
        self._streaming_response_text = ""
        self.chat_display.start_streaming("assistant")

        def run_stream():
            try:
                def on_chunk(chunk):
                    # Queue chunk to be added on main thread
                    QtCore.QMetaObject.invokeMethod(self, "_add_stream_chunk",
                                                    QtCore.Qt.QueuedConnection,
                                                    QtCore.Q_ARG(
                                                        str, request_token),
                                                    QtCore.Q_ARG(str, chunk))

                response = client.chat_stream(
                    model=model,
                    messages=messages,
                    base_url=url,
                    api_key=api_key,
                    timeout=120,
                    on_chunk=on_chunk
                )
                self._on_response_complete(request_token, response)
            except Exception as e:
                self._on_response_error(request_token, str(e))

        thread = threading.Thread(target=run_stream, daemon=True)
        thread.start()

    @QtCore.Slot(str, str)
    def _add_stream_chunk(self, request_token: str, chunk: str):
        """Add a streaming chunk to the display (called on main thread)."""
        if request_token != self._active_request_token:
            return

        self._streaming_response_text += chunk
        self.chat_display.append_stream_chunk(chunk)

    @QtCore.Slot(str, str)
    def _finish_response(self, request_token: str, response: str):
        """Finish response and update UI (called on main thread)."""
        if request_token != self._active_request_token:
            return

        self._active_request_token = ""
        self._is_streaming = False
        self.send_button.setEnabled(True)
        self.input_text.setEnabled(True)
        self.model_combo.setEnabled(True)
        self.status_label.hide()
        self.status_label.clear()

        if response.startswith("Error:"):
            error_msg = response[6:].strip()
            self.status_label.setText(f"Error: {error_msg}")
            self.status_label.show()  # Show error in constrained label
            self._emit_metric(
                "ai_chat_request_failed",
                {
                    "feature": "ai_chat",
                    "endpoint_id": self._endpoint_id or "",
                    "model": self.get_selected_model(),
                    "error": error_msg,
                },
            )
            return

        # Add assistant message to history then re-render the whole conversation
        # with proper markdown (streaming produced plain escaped text).
        self._chat_history.append({"role": "assistant", "content": response})
        self.chat_display.finish_streaming()
        self.chat_display.set_messages(self._chat_history)
        self._emit_metric(
            "ai_chat_request_completed",
            {
                "feature": "ai_chat",
                "endpoint_id": self._endpoint_id or "",
                "model": self.get_selected_model(),
                "response_length": len(response),
            },
        )

    def _on_response_complete(self, request_token: str, response: str):
        """Handle successful response."""
        QtCore.QMetaObject.invokeMethod(self, "_finish_response",
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(str, request_token),
                                        QtCore.Q_ARG(str, response))

    def _on_response_error(self, request_token: str, error: str):
        """Handle response error."""
        QtCore.QMetaObject.invokeMethod(self, "_finish_response",
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(str, request_token),
                                        QtCore.Q_ARG(str, f"Error: {error}"))

    def send_context(self, context_text: str, auto_send: bool = True):
        """
        Send context text to this chat (e.g., from "Generate Context to AI" button).
        Appends context as a user message with optional instruction.

        Args:
            context_text: The context content to send
            auto_send: If True, immediately send to AI after adding context
        """
        if not context_text or self._is_streaming:
            return

        message = f"Context:\n{context_text}\n\nPlease analyze this context and be ready to answer questions about it."
        self._chat_history.append({"role": "user", "content": message})
        self.chat_display.set_messages(self._chat_history)

        if auto_send:
            self._dispatch_ai_request()

    def send_context_and_question(self, context_text: str, question: str):
        """
        Send context text with a follow-up question to this chat.
        Appends context and question as a user message.
        """
        if not context_text or self._is_streaming:
            return

        if question:
            message = f"Context:\n{context_text}\n\nQuestion:\n{question}"
        else:
            message = f"Context:\n{context_text}\n\nPlease analyze this context and be ready to answer questions about it."

        self._chat_history.append({"role": "user", "content": message})
        self.chat_display.set_messages(self._chat_history)
        self._dispatch_ai_request()

    def clear_chat(self):
        """Clear chat history."""
        self._chat_history = []
        self.chat_display.clear()
        self.status_label.clear()
