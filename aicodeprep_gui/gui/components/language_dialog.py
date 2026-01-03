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
        
        self.setWindowTitle("Select Language / Seleccionar idioma / 选择语言")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self.setup_ui()
        self.load_languages()
    
    def setup_ui(self):
        """Setup the dialog UI."""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Header
        header = QtWidgets.QLabel("Select Application Language:")
        header_font = QtGui.QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)
        
        # Description
        desc = QtWidgets.QLabel(
            "Choose the language for the user interface. "
            "Bundled languages are available immediately. "
            "Other languages can be downloaded on demand."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        layout.addSpacing(10)
        
        # Language list
        self.language_list = QtWidgets.QListWidget()
        self.language_list.setSelectionMode(QtWidgets.QListWidget.SingleSelection)
        self.language_list.itemDoubleClicked.connect(self.on_language_double_clicked)
        layout.addWidget(self.language_list)
        
        # Bundled vs Downloadable indicator
        indicator_layout = QtWidgets.QHBoxLayout()
        bundled_label = QtWidgets.QLabel("✓ = Downloaded / Bundled")
        bundled_label.setStyleSheet("color: green;")
        indicator_layout.addWidget(bundled_label)
        
        download_label = QtWidgets.QLabel("(download) = Needs download")
        download_label.setStyleSheet("color: gray;")
        indicator_layout.addWidget(download_label)
        
        indicator_layout.addStretch()
        layout.addLayout(indicator_layout)
        
        # Current language info
        if self.translation_manager:
            current_lang = self.translation_manager.get_current_language()
            current_label = QtWidgets.QLabel(f"Current language: {current_lang}")
            current_label.setStyleSheet("font-style: italic;")
            layout.addWidget(current_label)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.select_button = QtWidgets.QPushButton("Select")
        self.select_button.clicked.connect(self.on_select_clicked)
        self.select_button.setEnabled(False)
        button_layout.addWidget(self.select_button)
        
        cancel_button = QtWidgets.QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Enable select button when selection changes
        self.language_list.itemSelectionChanged.connect(self.on_selection_changed)
    
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
        self.select_button.setEnabled(len(self.language_list.selectedItems()) > 0)
    
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
                "Download Language",
                f"The language '{lang_name}' needs to be downloaded.\n\n"
                "Download functionality is not yet implemented. "
                "Only bundled languages can be used for now.\n\n"
                "Would you like to continue anyway?",
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
                    "Language Changed",
                    f"Language changed to: {lang_name}\n\n"
                    "Note: Some UI elements may require an application restart to fully update."
                )
                self.accept()
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Language Change Failed",
                    f"Failed to change language to: {lang_name}\n\n"
                    "The language files may not be available."
                )
        else:
            self.accept()
    
    def get_selected_language(self):
        """Get the selected language code."""
        return self.selected_language
