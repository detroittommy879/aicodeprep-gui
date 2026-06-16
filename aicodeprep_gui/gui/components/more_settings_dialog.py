from PySide6 import QtWidgets

from aicodeprep_gui.rust_backend import download_worker_binary, get_worker_path
from aicodeprep_gui.user_settings import get_section, get_setting, set_section, set_setting


class MoreSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("More Settings")
        self.resize(720, 420)

        root = QtWidgets.QVBoxLayout(self)

        rust_cfg = get_section("rust_backend")
        secret_cfg = rust_cfg.get("secret_guard", {}) if isinstance(
            rust_cfg.get("secret_guard", {}), dict) else {}

        performance_group = QtWidgets.QGroupBox("Performance Engine")
        performance_layout = QtWidgets.QFormLayout(performance_group)

        self.rust_enabled = QtWidgets.QCheckBox(
            "Use Rust acceleration for folder scans and context generation")
        self.rust_enabled.setChecked(
            bool(rust_cfg.get("enabled", True))
            and bool(get_setting("pro_options", "rust_fast_processing", True))
        )

        worker = get_worker_path()
        status_text = (
            f"Ready: {worker}"
            if worker.exists()
            else f"Not installed: {worker}"
        )
        self.worker_status = QtWidgets.QLabel(status_text)
        self.worker_status.setWordWrap(True)

        performance_layout.addRow(self.rust_enabled)
        performance_layout.addRow("Worker status", self.worker_status)
        root.addWidget(performance_group)

        advanced_group = QtWidgets.QGroupBox("Advanced Worker Setup")
        exp_layout = QtWidgets.QFormLayout(advanced_group)

        self.auto_download = QtWidgets.QCheckBox(
            "Auto-download worker if missing")
        self.auto_download.setChecked(
            bool(rust_cfg.get("auto_download", True)))

        self.worker_path = QtWidgets.QLineEdit(
            str(rust_cfg.get("worker_path", "")))
        browse = QtWidgets.QPushButton("Browse…")
        browse.clicked.connect(self._browse_worker)
        path_row = QtWidgets.QHBoxLayout()
        path_row.addWidget(self.worker_path)
        path_row.addWidget(browse)
        path_widget = QtWidgets.QWidget()
        path_widget.setLayout(path_row)

        self.download_url = QtWidgets.QLineEdit(
            str(rust_cfg.get("download_url", "")))
        self.download_url.setPlaceholderText(
            "https://.../{platform}/aicp-rust-worker")

        self.sha256 = QtWidgets.QLineEdit(
            str(rust_cfg.get("download_sha256", "")))
        self.sha256.setPlaceholderText("Optional SHA256")

        self.secret_guard = QtWidgets.QCheckBox(
            "Replace detected secrets with placeholders")
        self.secret_guard.setChecked(bool(secret_cfg.get("enabled", False)))

        self.placeholder_prefix = QtWidgets.QLineEdit(
            str(secret_cfg.get("placeholder_prefix", "REDACTED_SECRET_")))

        download_btn = QtWidgets.QPushButton("Download/Update Worker")
        download_btn.clicked.connect(self._download_worker)

        exp_layout.addRow(self.auto_download)
        exp_layout.addRow("Worker binary path", path_widget)
        exp_layout.addRow("Download URL", self.download_url)
        exp_layout.addRow("Checksum (SHA256)", self.sha256)
        exp_layout.addRow(download_btn)

        root.addWidget(advanced_group)

        secret_group = QtWidgets.QGroupBox("Secret Handling")
        secret_layout = QtWidgets.QFormLayout(secret_group)
        secret_layout.addRow(self.secret_guard)
        secret_layout.addRow("Placeholder prefix", self.placeholder_prefix)
        root.addWidget(secret_group)

        help_label = QtWidgets.QLabel(
            "If the Rust worker is missing or fails, aicodeprep-gui automatically uses the Python fallback."
        )
        help_label.setWordWrap(True)
        root.addWidget(help_label)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def _browse_worker(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Rust Worker Binary",
            "",
            "Executables (*.exe);;All Files (*)",
        )
        if file_path:
            self.worker_path.setText(file_path)

    def _download_worker(self):
        ok, message = download_worker_binary(
            self.download_url.text().strip(),
            self.sha256.text().strip(),
        )
        if ok:
            self.worker_path.setText(message)
            self.worker_status.setText(f"Ready: {message}")
            QtWidgets.QMessageBox.information(
                self, "Rust Worker", f"Downloaded worker:\n{message}")
        else:
            QtWidgets.QMessageBox.warning(
                self, "Rust Worker", f"Download failed:\n{message}")

    def accept(self):
        rust_cfg = get_section("rust_backend")
        if not isinstance(rust_cfg, dict):
            rust_cfg = {}

        rust_cfg.update(
            {
                "enabled": bool(self.rust_enabled.isChecked()),
                "auto_download": bool(self.auto_download.isChecked()),
                "worker_path": self.worker_path.text().strip(),
                "download_url": self.download_url.text().strip(),
                "download_sha256": self.sha256.text().strip(),
                "secret_guard": {
                    "enabled": bool(self.secret_guard.isChecked()),
                    "placeholder_prefix": self.placeholder_prefix.text().strip() or "REDACTED_SECRET_",
                },
            }
        )
        set_section("rust_backend", rust_cfg)
        set_setting("pro_options", "rust_fast_processing",
                    bool(self.rust_enabled.isChecked()))
        super().accept()
