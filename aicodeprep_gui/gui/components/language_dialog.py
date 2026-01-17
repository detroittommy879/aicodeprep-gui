"""
Language selection dialog for aicodeprep-gui.

Allows users to select the UI language from bundled and downloadable options.
"""
import logging
from PySide6 import QtWidgets, QtCore, QtGui


logger = logging.getLogger(__name__)


class LanguageSelectionDialog(QtWidgets.QDialog):
    """Dialog for selecting the application UI language."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_language = None
        self.translation_manager = None

        # Get translation manager from app
        app = QtWidgets.QApplication.instance()
        if hasattr(app, 'translation_manager'):
            self.translation_manager = app.translation_manager

        self.setWindowTitle(
            self.tr("Select Language / Seleccionar idioma / 选择语言"))
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        self.setup_ui()
        self.load_languages()

    def setup_ui(self):
        """Setup the dialog UI."""
        layout = QtWidgets.QVBoxLayout(self)

        # Header
        self.header_label = QtWidgets.QLabel(
            self.tr("Select Application Language:"))
        header_font = QtGui.QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        self.header_label.setFont(header_font)
        layout.addWidget(self.header_label)

        # Description
        self.desc_label = QtWidgets.QLabel(
            self.tr(
                "Choose the language for the user interface. "
                "Bundled languages are available immediately. "
                "Other languages can be downloaded on demand."
            )
        )
        self.desc_label.setWordWrap(True)
        layout.addWidget(self.desc_label)

        layout.addSpacing(10)

        # Language list
        self.language_list = QtWidgets.QListWidget()
        self.language_list.setSelectionMode(
            QtWidgets.QListWidget.SingleSelection)
        self.language_list.itemDoubleClicked.connect(
            self.on_language_double_clicked)
        layout.addWidget(self.language_list)

        # Bundled vs Downloadable indicator
        indicator_layout = QtWidgets.QHBoxLayout()
        self.bundled_label = QtWidgets.QLabel(
            self.tr("✓ = Downloaded / Bundled"))
        self.bundled_label.setStyleSheet("color: green;")
        indicator_layout.addWidget(self.bundled_label)

        self.download_label = QtWidgets.QLabel(
            self.tr("(download) = Needs download"))
        self.download_label.setStyleSheet("color: gray;")
        indicator_layout.addWidget(self.download_label)

        indicator_layout.addStretch()
        layout.addLayout(indicator_layout)

        # Current language info
        self.current_label = None
        if self.translation_manager:
            current_lang = self.translation_manager.get_current_language()
            self.current_label = QtWidgets.QLabel(
                self.tr("Current language: {code}").format(code=current_lang)
            )
            self.current_label.setStyleSheet("font-style: italic;")
            layout.addWidget(self.current_label)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()

        self.select_button = QtWidgets.QPushButton(self.tr("Select"))
        self.select_button.clicked.connect(self.on_select_clicked)
        self.select_button.setEnabled(False)
        button_layout.addWidget(self.select_button)

        self.cancel_button = QtWidgets.QPushButton(self.tr("Cancel"))
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Enable select button when selection changes
        self.language_list.itemSelectionChanged.connect(
            self.on_selection_changed)

    def load_languages(self):
        """Load available languages into the list."""
        if not self.translation_manager:
            logger.warning("Translation manager not available")
            return

        languages = self.translation_manager.get_available_languages()
        current_lang = self.translation_manager.get_current_language()

        for code, name in languages:
            item = QtWidgets.QListWidgetItem(name)
            item.setData(QtCore.Qt.UserRole, code)

            # Highlight current language
            if code == current_lang:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setBackground(QtGui.QColor(200, 230, 255))

            self.language_list.addItem(item)

    def on_selection_changed(self):
        """Enable select button when a language is selected."""
        self.select_button.setEnabled(
            len(self.language_list.selectedItems()) > 0)

    def on_language_double_clicked(self, item):
        """Handle double-click on a language."""
        self.on_select_clicked()

    def on_select_clicked(self):
        """Handle Select button click."""
        selected_items = self.language_list.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        lang_code = item.data(QtCore.Qt.UserRole)
        lang_name = item.text()

        # Check if download is needed
        if "(download)" in lang_name and self.translation_manager:
            reply = QtWidgets.QMessageBox.question(
                self,
                self.tr("Download Language"),
                self.tr(
                    "The language '{name}' needs to be downloaded.\n\n"
                    "Download functionality is not yet implemented. "
                    "Only bundled languages can be used for now.\n\n"
                    "Would you like to continue anyway?"
                ).format(name=lang_name),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )

            if reply == QtWidgets.QMessageBox.No:
                return

        self.selected_language = lang_code

        # Apply language immediately
        if self.translation_manager:
            success = self.translation_manager.set_language(lang_code)
            if success:
                QtWidgets.QMessageBox.information(
                    self,
                    self.tr("Language Changed"),
                    self.tr("Language changed to: {name}").format(
                        name=lang_name)
                )
                if self.current_label:
                    self.current_label.setText(
                        self.tr("Current language: {code}").format(
                            code=lang_code)
                    )
                self.accept()
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    self.tr("Language Change Failed"),
                    self.tr(
                        "Failed to change language to: {name}\n\n"
                        "The language files may not be available."
                    ).format(name=lang_name)
                )
        else:
            self.accept()

    def changeEvent(self, event):
        """Handle runtime language changes without requiring restart."""
        try:
            if event.type() == QtCore.QEvent.LanguageChange:
                self._retranslate_ui()
        except Exception:
            pass
        return super(LanguageSelectionDialog, self).changeEvent(event)

    def _retranslate_ui(self):
        self.setWindowTitle(
            self.tr("Select Language / Seleccionar idioma / 选择语言"))
        if hasattr(self, "header_label"):
            self.header_label.setText(self.tr("Select Application Language:"))
        if hasattr(self, "desc_label"):
            self.desc_label.setText(
                self.tr(
                    "Choose the language for the user interface. "
                    "Bundled languages are available immediately. "
                    "Other languages can be downloaded on demand."
                )
            )
        if hasattr(self, "bundled_label"):
            self.bundled_label.setText(self.tr("✓ = Downloaded / Bundled"))
        if hasattr(self, "download_label"):
            self.download_label.setText(self.tr("(download) = Needs download"))
        if hasattr(self, "select_button"):
            self.select_button.setText(self.tr("Select"))
        if hasattr(self, "cancel_button"):
            self.cancel_button.setText(self.tr("Cancel"))
        if self.translation_manager and self.current_label:
            current_lang = self.translation_manager.get_current_language()
            self.current_label.setText(
                self.tr("Current language: {code}").format(code=current_lang)
            )

    def get_selected_language(self):
        """Get the selected language code."""
        return self.selected_language
