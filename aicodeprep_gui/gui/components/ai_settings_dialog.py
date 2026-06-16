import os
import re

from PySide6 import QtWidgets, QtCore, QtGui
from aicodeprep_gui.pro.ai_assist.endpoint_config import (
    load_endpoints,
    save_endpoints,
)
from aicodeprep_gui.pro.ai_assist.ai_client import AIClient
import logging

logger = logging.getLogger(__name__)


def _process_events_for_ui_feedback():
    if os.environ.get("AICODEPREP_TEST_MODE") == "1":
        return
    QtWidgets.QApplication.processEvents()


class AIEndpointSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("AI Endpoint Settings"))
        self.resize(600, 450)

        # Data state
        self.config_data = load_endpoints()
        self.current_endpoint_id = None
        self.ignore_changes = False

        # --- Build layout from scratch (single root VBoxLayout) ---
        root_layout = QtWidgets.QVBoxLayout(self)

        # Content area: left panel + right panel
        content_layout = QtWidgets.QHBoxLayout()

        # --- Left Panel ---
        left_layout = QtWidgets.QVBoxLayout()
        self.endpoint_list = QtWidgets.QListWidget()
        self.endpoint_list.itemSelectionChanged.connect(
            self._on_selection_changed)
        left_layout.addWidget(self.endpoint_list)

        left_btn_layout = QtWidgets.QHBoxLayout()
        add_btn = QtWidgets.QPushButton(self.tr("+ Add"))
        add_btn.clicked.connect(self._on_add_endpoint)
        remove_btn = QtWidgets.QPushButton(self.tr("- Remove"))
        remove_btn.clicked.connect(self._on_remove_endpoint)
        left_btn_layout.addWidget(add_btn)
        left_btn_layout.addWidget(remove_btn)
        left_layout.addLayout(left_btn_layout)

        content_layout.addLayout(left_layout, 1)

        # --- Right Panel (Form) ---
        right_layout = QtWidgets.QVBoxLayout()
        form_layout = QtWidgets.QFormLayout()

        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.textEdited.connect(self._marked_changed)
        form_layout.addRow(self.tr("Name:"), self.name_edit)

        self.url_edit = QtWidgets.QLineEdit()
        self.url_edit.setPlaceholderText("https://your-endpoint.example/v1")
        self.url_edit.textEdited.connect(self._marked_changed)
        form_layout.addRow(self.tr("URL:"), self.url_edit)

        self.key_edit = QtWidgets.QLineEdit()
        self.key_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.key_edit.textEdited.connect(self._marked_changed)
        form_layout.addRow(self.tr("API Key:"), self.key_edit)

        right_layout.addLayout(form_layout)

        test_conn_layout = QtWidgets.QHBoxLayout()
        self.test_btn = QtWidgets.QPushButton(self.tr("Test Connection"))
        self.test_btn.clicked.connect(self._on_test_connection)
        self.status_label = QtWidgets.QLabel("")
        test_conn_layout.addWidget(self.test_btn)
        test_conn_layout.addWidget(self.status_label)
        test_conn_layout.addStretch()
        right_layout.addLayout(test_conn_layout)

        right_layout.addSpacing(10)

        models_layout = QtWidgets.QHBoxLayout()
        models_label = QtWidgets.QLabel(self.tr("Model:"))
        self.models_combo = QtWidgets.QComboBox()
        self.models_combo.setEditable(True)  # Allow custom entry
        self.models_combo.currentTextChanged.connect(self._marked_changed)
        self.refresh_btn = QtWidgets.QPushButton(self.tr("Refresh Models"))
        self.refresh_btn.clicked.connect(self._on_refresh_models)
        models_layout.addWidget(models_label)
        models_layout.addWidget(self.models_combo, 1)
        models_layout.addWidget(self.refresh_btn)
        right_layout.addLayout(models_layout)

        actions_layout = QtWidgets.QHBoxLayout()
        self.set_active_btn = QtWidgets.QPushButton(self.tr("Set Active"))
        self.set_active_btn.setToolTip(
            self.tr("Make this endpoint the one used by AI Chat and compatible Flow nodes"))
        self.set_active_btn.clicked.connect(self._on_set_active)
        actions_layout.addWidget(self.set_active_btn)
        actions_layout.addStretch()
        right_layout.addLayout(actions_layout)

        right_layout.addStretch()

        content_layout.addLayout(right_layout, 2)

        root_layout.addLayout(content_layout)

        # --- Bottom Buttons ---
        bottom_btns = QtWidgets.QHBoxLayout()
        save_btn = QtWidgets.QPushButton(self.tr("Save && Close"))
        save_btn.clicked.connect(self._on_save)
        cancel_btn = QtWidgets.QPushButton(self.tr("Cancel"))
        cancel_btn.clicked.connect(self._on_cancel)
        bottom_btns.addStretch()
        bottom_btns.addWidget(save_btn)
        bottom_btns.addWidget(cancel_btn)
        root_layout.addLayout(bottom_btns)

        # Load Data
        self._refresh_list()

    @staticmethod
    def _slugify_endpoint_id(label: str) -> str:
        cleaned = re.sub(r"[^a-z0-9]+", "-", (label or "").strip().lower())
        return cleaned.strip("-") or "endpoint"

    def _generate_unique_endpoint_id(self, label: str = "New Endpoint") -> str:
        endpoints = self.config_data.get("endpoints", {})
        base_id = self._slugify_endpoint_id(label)
        candidate = base_id
        suffix = 2
        while candidate in endpoints:
            candidate = f"{base_id}-{suffix}"
            suffix += 1
        return candidate

    @staticmethod
    def _new_endpoint_data(name: str = "New Endpoint") -> dict:
        return {
            "name": name,
            "url": "",
            "api_key": "",
            "selected_model": "",
        }

    def _refresh_list(self):
        """Reloads list from self.config_data."""
        self.ignore_changes = True
        current_id = self.current_endpoint_id

        self.endpoint_list.clear()

        endpoints = self.config_data.get("endpoints", {})
        active_id = self.config_data.get("active_endpoint", "")

        # Sort by ID or Name? Let's sort by ID for stability
        for eid in sorted(endpoints.keys()):
            data = endpoints[eid]
            name = data.get("name", eid)

            display_text = name
            if eid == active_id:
                display_text = f"► {name}"

            item = QtWidgets.QListWidgetItem(display_text)
            item.setData(QtCore.Qt.UserRole, eid)

            if eid == active_id:
                font = item.font()
                font.setBold(True)
                item.setFont(font)

            self.endpoint_list.addItem(item)

            if eid == current_id:
                self.endpoint_list.setCurrentItem(item)

        # If nothing selected, select first or active
        if not self.endpoint_list.currentItem() and self.endpoint_list.count() > 0:
            # Try to select active
            for i in range(self.endpoint_list.count()):
                item = self.endpoint_list.item(i)
                if item.data(QtCore.Qt.UserRole) == active_id:
                    self.endpoint_list.setCurrentItem(item)
                    break

            # If still nothing
            if not self.endpoint_list.currentItem():
                self.endpoint_list.setCurrentRow(0)

        self.ignore_changes = False

        # Set current_endpoint_id from the selected list item
        # (itemSelectionChanged was blocked by ignore_changes, so we must do it here)
        selected_item = self.endpoint_list.currentItem()
        if selected_item:
            self.current_endpoint_id = selected_item.data(QtCore.Qt.UserRole)
            self._populate_form(self.current_endpoint_id)
        else:
            self.current_endpoint_id = None

    def _marked_changed(self):
        """Called when text fields change."""
        if self.ignore_changes:
            return

        # Save to memory immediately
        eid = self._get_selected_endpoint_id()
        if not eid:
            return

        if eid in self.config_data.get("endpoints", {}):
            self.config_data["endpoints"][eid]["name"] = self.name_edit.text()
            self.config_data["endpoints"][eid]["url"] = self.url_edit.text()
            self.config_data["endpoints"][eid]["api_key"] = self.key_edit.text()
            self.config_data["endpoints"][eid]["selected_model"] = self.models_combo.currentText(
            )
            self.current_endpoint_id = eid
            self._update_list_item_display(eid)

    def _get_selected_endpoint_id(self):
        if self.current_endpoint_id:
            return self.current_endpoint_id

        item = self.endpoint_list.currentItem()
        if item is not None:
            endpoint_id = item.data(QtCore.Qt.UserRole)
            if endpoint_id:
                return endpoint_id
        return self.current_endpoint_id

    def _update_list_item_display(self, endpoint_id: str):
        active_id = self.config_data.get("active_endpoint", "")
        for i in range(self.endpoint_list.count()):
            item = self.endpoint_list.item(i)
            if item.data(QtCore.Qt.UserRole) != endpoint_id:
                continue

            endpoint_data = self.config_data.get(
                "endpoints", {}).get(endpoint_id, {})
            name = endpoint_data.get("name", endpoint_id) or endpoint_id
            item.setText(f"► {name}" if endpoint_id == active_id else name)

            font = item.font()
            font.setBold(endpoint_id == active_id)
            item.setFont(font)
            break

    def _save_current_selection(self):
        """Flush ALL current form fields into the in-memory config_data."""
        eid = self._get_selected_endpoint_id()
        if not eid:
            return

        if eid in self.config_data.get("endpoints", {}):
            self.config_data["endpoints"][eid]["name"] = self.name_edit.text()
            self.config_data["endpoints"][eid]["url"] = self.url_edit.text(
            ).strip()
            self.config_data["endpoints"][eid]["api_key"] = self.key_edit.text(
            ).strip()
            self.config_data["endpoints"][eid]["selected_model"] = self.models_combo.currentText(
            )
            self.current_endpoint_id = eid

    def _on_selection_changed(self):
        if self.ignore_changes:
            return

        # Save current form edits before switching to another endpoint
        self._save_current_selection()

        item = self.endpoint_list.currentItem()
        if not item:
            self._clear_form()
            self.current_endpoint_id = None
            return

        eid = item.data(QtCore.Qt.UserRole)
        self.current_endpoint_id = eid
        self._populate_form(eid)

    def _clear_form(self):
        self.ignore_changes = True
        self.name_edit.clear()
        self.url_edit.clear()
        self.key_edit.clear()
        self.models_combo.clear()
        self.status_label.setText("")
        self.ignore_changes = False

    def _populate_form(self, eid):
        self.ignore_changes = True
        self.current_endpoint_id = eid
        data = self.config_data.get("endpoints", {}).get(eid, {})

        self.name_edit.setText(data.get("name", ""))
        self.url_edit.setText(data.get("url", ""))
        self.key_edit.setText(data.get("api_key", ""))

        self.models_combo.clear()
        selected = data.get("selected_model", "")
        if selected:
            self.models_combo.addItem(selected)

        self.status_label.setText("")
        self.ignore_changes = False

    def _persist_memory_to_disk(self):
        """Saves current self.config_data to disk."""
        self._save_current_selection()
        save_endpoints(self.config_data)

    def _on_add_endpoint(self):
        self._save_current_selection()

        eid = self._generate_unique_endpoint_id(self.tr("New Endpoint"))
        self.config_data.setdefault("endpoints", {})[eid] = self._new_endpoint_data(
            self.tr("New Endpoint")
        )
        self.current_endpoint_id = eid
        self._refresh_list()

        # Focus name edit
        self.name_edit.setFocus()
        self.name_edit.selectAll()

    def _on_remove_endpoint(self):
        item = self.endpoint_list.currentItem()
        if not item:
            return
        eid = item.data(QtCore.Qt.UserRole)

        # Check if last one
        endpoints = self.config_data.get("endpoints", {})
        if len(endpoints) <= 1:
            QtWidgets.QMessageBox.warning(self, self.tr(
                "Warning"), self.tr("Cannot remove the last endpoint."))
            return

        confirm = QtWidgets.QMessageBox.question(
            self, self.tr("Confirm Remove"),
            self.tr(f"Are you sure you want to remove '{eid}'?"),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if confirm != QtWidgets.QMessageBox.Yes:
            return

        self._save_current_selection()

        endpoints = self.config_data.get("endpoints", {})
        if eid not in endpoints:
            return

        del endpoints[eid]

        if self.config_data.get("active_endpoint") == eid:
            self.config_data["active_endpoint"] = next(iter(endpoints), "")

        self.current_endpoint_id = None  # Let refresh logic decide
        self._refresh_list()

    def _on_set_active(self):
        item = self.endpoint_list.currentItem()
        if not item:
            return
        eid = item.data(QtCore.Qt.UserRole)

        # Save current form values to memory, then flip active endpoint and
        # write everything to disk in a single save_endpoints() call.
        # Avoid calling set_active_endpoint() (which re-reads disk and runs
        # migrations) because that round-trip can overwrite freshly typed data.
        self._save_current_selection()
        self.config_data["active_endpoint"] = eid
        logger.info("AI endpoint set active: %s", eid)

        # Refresh the list from the in-memory state.
        self._refresh_list()

    def _on_test_connection(self):
        # Flush form edits to memory first so nothing reverts
        self._save_current_selection()

        url = self.url_edit.text().strip()
        key = self.key_edit.text().strip()

        if not url:
            self.status_label.setText(self.tr("URL required"))
            self.status_label.setStyleSheet("color: orange;")
            return

        self.status_label.setText(self.tr("Testing..."))
        self.status_label.setStyleSheet("")
        self.test_btn.setEnabled(False)
        self.setCursor(QtCore.Qt.WaitCursor)
        _process_events_for_ui_feedback()

        try:
            client = AIClient()
            # Use single attempt with short timeout to avoid long freeze
            models = client.list_models(url, api_key=key, timeout=5, retries=1)
        except Exception:
            models = []
        finally:
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.test_btn.setEnabled(True)

        if models:
            self.status_label.setText(
                self.tr(f"Connected ✓ ({len(models)} models)"))
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText(
                self.tr("Failed ✗ — check URL and try again"))
            self.status_label.setStyleSheet("color: red;")

    def _on_refresh_models(self):
        # Flush form edits to memory first
        self._save_current_selection()

        url = self.url_edit.text().strip()
        key = self.key_edit.text().strip()

        if not url:
            QtWidgets.QMessageBox.warning(self, self.tr(
                "Error"), self.tr("Please enter a URL first."))
            return

        self.refresh_btn.setEnabled(False)
        self.setCursor(QtCore.Qt.WaitCursor)
        _process_events_for_ui_feedback()

        try:
            client = AIClient()
            models = client.list_models(url, api_key=key, timeout=5, retries=1)
        except Exception:
            models = []
        finally:
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.refresh_btn.setEnabled(True)

        self.setCursor(QtCore.Qt.ArrowCursor)

        if models:
            current = self.models_combo.currentText()
            self.models_combo.clear()
            ids = [m["id"] for m in models]
            self.models_combo.addItems(ids)

            # Restore selection if exists
            index = self.models_combo.findText(current)
            if index >= 0:
                self.models_combo.setCurrentIndex(index)
            else:
                if ids:
                    self.models_combo.setCurrentIndex(0)

            # Update memory
            self._save_current_selection()
            self.status_label.setText(self.tr("Models Refreshed"))
        else:
            QtWidgets.QMessageBox.warning(self, self.tr("Error"), self.tr(
                "Failed to fetch models or no models found."))

    def _on_save(self):
        self._save_current_selection()
        self._persist_memory_to_disk()
        logger.info("AI endpoint settings saved. active=%s",
                    self.config_data.get("active_endpoint"))
        self.accept()

    def _on_cancel(self):
        self.reject()


EndpointSettingsDialog = AIEndpointSettingsDialog
