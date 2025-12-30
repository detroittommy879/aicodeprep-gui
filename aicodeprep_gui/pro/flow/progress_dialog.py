"""Progress dialog for flow execution feedback."""

from PySide6 import QtWidgets, QtCore
from typing import Optional


class FlowProgressDialog(QtWidgets.QDialog):
    """Non-blocking progress dialog showing flow execution status."""

    def __init__(self, parent=None, total_nodes: int = 0):
        super().__init__(parent)
        self.setWindowTitle("Flow Execution")
        self.setModal(False)
        self.setMinimumWidth(450)
        self.resize(500, 300)

        self.total_nodes = total_nodes
        self.completed_nodes = 0
        self.cancelled = False

        # Layout
        layout = QtWidgets.QVBoxLayout(self)

        # Status label
        self.status_label = QtWidgets.QLabel("Initializing flow execution...")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, total_nodes if total_nodes > 0 else 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Node list
        list_label = QtWidgets.QLabel("Node Status:")
        layout.addWidget(list_label)

        self.node_list = QtWidgets.QTextEdit()
        self.node_list.setReadOnly(True)
        self.node_list.setMaximumHeight(150)
        layout.addWidget(self.node_list)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)

        button_layout.addStretch()

        self.close_button = QtWidgets.QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setEnabled(False)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

        # Center on parent
        if parent:
            self.move(parent.geometry().center() - self.rect().center())

    def _on_cancel(self):
        """Handle cancel button click."""
        self.cancelled = True
        self.cancel_button.setEnabled(False)
        self.status_label.setText(
            "Cancelling... waiting for current node to finish.")
        QtWidgets.QApplication.processEvents()

    def is_cancelled(self) -> bool:
        """Check if user requested cancellation."""
        return self.cancelled

    def set_status(self, message: str):
        """Update the main status message."""
        self.status_label.setText(message)
        QtWidgets.QApplication.processEvents()

    def add_node_status(self, node_name: str, status: str, color: str = "black"):
        """Add a node status line to the list."""
        html = f'<span style="color: {color};">{node_name}: {status}</span><br>'
        self.node_list.append(html)
        QtWidgets.QApplication.processEvents()

    def update_node_status(self, node_name: str, status: str, color: str = "black"):
        """Update status for a specific node (replaces last line)."""
        # For simplicity, just append
        self.add_node_status(node_name, status, color)

    def increment_progress(self):
        """Increment progress by one node."""
        self.completed_nodes += 1
        self.progress_bar.setValue(self.completed_nodes)
        QtWidgets.QApplication.processEvents()

    def set_progress(self, current: int, total: Optional[int] = None):
        """Set progress to specific value."""
        if total is not None:
            self.progress_bar.setRange(0, total)
            self.total_nodes = total
        self.progress_bar.setValue(current)
        self.completed_nodes = current
        QtWidgets.QApplication.processEvents()

    def execution_complete(self, success: bool = True):
        """Mark execution as complete."""
        self.cancel_button.setEnabled(False)
        self.close_button.setEnabled(True)

        if success:
            self.status_label.setText(
                f"✓ Flow execution completed successfully! ({self.completed_nodes}/{self.total_nodes} nodes)")
            self.progress_bar.setValue(self.total_nodes)
        else:
            self.status_label.setText(
                "✗ Flow execution failed or was cancelled.")

        QtWidgets.QApplication.processEvents()
