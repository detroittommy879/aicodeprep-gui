# All imports from the original gui.py
import os
import sys
import platform
import logging
import uuid
import json
from datetime import datetime, date
from PySide6 import QtWidgets, QtCore, QtGui, QtNetwork
from aicodeprep_gui import __version__  # Keep one of these, remove duplicate
from aicodeprep_gui import update_checker
from PySide6.QtCore import QTemporaryDir
from importlib import resources
from aicodeprep_gui.apptheme import (
    system_pref_is_dark, apply_dark_palette, apply_light_palette,
    get_checkbox_style_dark, get_checkbox_style_light,
    create_arrow_pixmap, get_groupbox_style
)
from typing import List, Tuple
from aicodeprep_gui import smart_logic
from aicodeprep_gui.file_processor import process_files
# from aicodeprep_gui import __version__ # Duplicate import, removed
from aicodeprep_gui import pro  # Keep one of these, remove duplicate

# New modular imports
from .components.layouts import FlowLayout
from .components.dialogs import DialogManager, VoteDialog
from .components.tree_widget import FileTreeManager
from .components.preset_buttons import PresetButtonManager
# Level delegate is provided via Pro getter when enabled
# from aicodeprep_gui import pro # Duplicate import, removed
from .settings.presets import global_preset_manager
from .settings.preferences import PreferencesManager
from .settings.ui_settings import UISettingsManager
from .handlers.update_events import UpdateCheckWorker
from .handlers.keyboard_handler import KeyboardShortcutManager
from .utils.metrics import MetricsManager
from .utils.helpers import WindowHelpers


class LogoTreeWidget(QtWidgets.QTreeWidget):
    """Custom QTreeWidget with keyboard navigation support."""

    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        """Handle keyboard navigation for tree widget."""
        key = event.key()

        # Space key: toggle checkbox of current item(s)
        if key == QtCore.Qt.Key.Key_Space:
            selected_items = self.selectedItems()
            if selected_items:
                # Toggle all selected items
                for item in selected_items:
                    if item.flags() & QtCore.Qt.ItemIsUserCheckable and item.flags() & QtCore.Qt.ItemIsEnabled:
                        current_state = item.checkState(0)
                        new_state = QtCore.Qt.Unchecked if current_state == QtCore.Qt.Checked else QtCore.Qt.Checked
                        item.setCheckState(0, new_state)
                event.accept()
                return

        # Arrow keys: handled by default QTreeWidget behavior for Up/Down
        # Right arrow: expand folders, Left arrow: collapse folders
        elif key == QtCore.Qt.Key.Key_Right:
            current_item = self.currentItem()
            if current_item:
                abs_path = current_item.data(0, QtCore.Qt.UserRole)
                if abs_path and os.path.isdir(abs_path):
                    if not current_item.isExpanded():
                        self.expandItem(current_item)
                        event.accept()
                        return

        elif key == QtCore.Qt.Key.Key_Left:
            current_item = self.currentItem()
            if current_item:
                abs_path = current_item.data(0, QtCore.Qt.UserRole)
                if abs_path and os.path.isdir(abs_path):
                    if current_item.isExpanded():
                        self.collapseItem(current_item)
                        event.accept()
                        return

        # Let parent handle all other keys (Up/Down navigation, etc.)
        super().keyPressEvent(event)


class LogoCentralWidget(QtWidgets.QWidget):
    """Custom central widget that draws a logo watermark in the bottom-left corner."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logo_pixmap = None
        self.logo_opacity = 0.48
        self.logo_padding = 5  # Padding from edges

    def set_logo(self, pixmap, opacity=0.48):
        """Set the logo pixmap and opacity for the background watermark."""
        self.logo_pixmap = pixmap
        self.logo_opacity = opacity
        self.update()

    def paintEvent(self, event):
        """Override paint event to draw logo in the background."""
        super().paintEvent(event)

        # Draw the logo as a watermark in bottom-left corner
        if self.logo_pixmap and not self.logo_pixmap.isNull():
            # Calculate position for bottom-left corner
            widget_rect = self.rect()
            logo_width = self.logo_pixmap.width()
            logo_height = self.logo_pixmap.height()

            # Position in bottom-left with padding
            x = self.logo_padding
            y = widget_rect.height() - logo_height - self.logo_padding

            # Create a temporary pixmap to apply opacity
            temp_pixmap = QtGui.QPixmap(self.logo_pixmap.size())
            temp_pixmap.fill(QtCore.Qt.transparent)

            # Draw the logo onto the temp pixmap with opacity
            temp_painter = QtGui.QPainter(temp_pixmap)
            temp_painter.setOpacity(self.logo_opacity)
            temp_painter.drawPixmap(0, 0, self.logo_pixmap)
            temp_painter.end()

            # Now draw the temp pixmap with applied opacity
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
            painter.drawPixmap(x, y, temp_pixmap)
            painter.end()


class FileSelectionGUI(QtWidgets.QMainWindow):
    GUMROAD_PRODUCT_ID = "KpjO4PdY2mQNCZC1k_ZkPQ=="  # set your Gumroad product_id
    GUMROAD_PRODUCT_ID_2 = "O1LkPokDSKDZdhSitEvvrA=="  # set your Gumroad product_id

    def __init__(self, files):
        super().__init__()
        self.dialog_manager = DialogManager(self)
        self.preferences_manager = PreferencesManager(self)
        self.ui_settings_manager = UISettingsManager(self)
        self.tree_manager = FileTreeManager(self)
        self.preset_manager = PresetButtonManager(self)
        self.metrics_manager = MetricsManager(self)
        self.window_helpers = WindowHelpers(self)
        self.keyboard_manager = KeyboardShortcutManager(self)
        self.flow_dock = None

        self.initial_show_event = True
        self.temp_dir = QTemporaryDir()
        self.arrow_pixmap_paths = {}
        if self.temp_dir.isValid():
            self._generate_arrow_pixmaps()
        else:
            logging.warning(
                "Could not create temporary directory for theme assets.")

        try:
            with resources.path('aicodeprep_gui.images', 'favicon.ico') as icon_path:
                app_icon = QtGui.QIcon(str(icon_path))
            self.setWindowIcon(app_icon)
            # Imports moved here for minimal change, but ideally these would be at top of file or within a dedicated setup method.
            from PySide6.QtWidgets import QSystemTrayIcon, QMenu
            from PySide6.QtGui import QAction
            tray = QSystemTrayIcon(app_icon, parent=self)
            menu = QMenu()
            self.tray_show_act = QAction(self.tr("Show"), self)
            self.tray_quit_act = QAction(self.tr("Quit"), self)
            self.tray_show_act.triggered.connect(self.show)
            self.tray_quit_act.triggered.connect(self.quit_without_processing)
            menu.addAction(self.tray_show_act)
            menu.addSeparator()
            menu.addAction(self.tray_quit_act)
            tray.setContextMenu(menu)
            tray.show()
            self.tray_icon = tray
        except FileNotFoundError:
            logging.warning(
                "Application icon 'favicon.ico' not found in package resources.")

        self.presets = []
        self.setAcceptDrops(True)
        self.files = files
        self.latest_pypi_version = None
        self.network_manager = QtNetwork.QNetworkAccessManager(self)

        settings = QtCore.QSettings("aicodeprep-gui", "UserIdentity")
        self.user_uuid = settings.value("user_uuid")
        if not self.user_uuid:
            self.user_uuid = str(uuid.uuid4())
            settings.setValue("user_uuid", self.user_uuid)
            logging.info(
                f"Generated new anonymous user UUID: {self.user_uuid}")

        app_open_count = settings.value("app_open_count", 0, type=int)
        try:
            app_open_count = int(app_open_count)
        except Exception:
            app_open_count = 0
        app_open_count += 1
        settings.setValue("app_open_count", app_open_count)
        self.app_open_count = app_open_count

        self._send_metric_event("open")

        # Track generate context clicks for share dialog
        generate_count = settings.value("generate_count", 0, type=int)
        try:
            generate_count = int(generate_count)
        except Exception:
            generate_count = 0
        self.generate_count = generate_count

        install_date_str = settings.value("install_date")
        if not install_date_str:
            today_iso = date.today().isoformat()
            settings.setValue("install_date", today_iso)
            install_date_str = today_iso
        logging.debug(f"Stored install_date: {install_date_str}")

        now = datetime.now()
        time_str = f"{now.strftime('%I').lstrip('0') or '12'}{now.strftime('%M')}{now.strftime('%p').lower()}"
        request = QtNetwork.QNetworkRequest(QtCore.QUrl(
            f"https://wuu73.org/dixels/newaicp.html?t={time_str}&user={self.user_uuid}"))
        self.network_manager.get(request)

        self.update_thread = None
        self.setWindowTitle(self.tr("aicodeprep-gui - File Selection"))
        self.app = QtWidgets.QApplication.instance()
        if self.app is None:
            self.app = QtWidgets.QApplication([])
        self.action = 'quit'

        self.prefs_filename = ".aicodeprep-gui"
        self.remember_checkbox = None
        self.preferences_manager.load_prefs_if_exists()

        if platform.system() == 'Windows':
            scale_factor = self.app.primaryScreen().logicalDotsPerInch() / 96.0
        else:
            scale_factor = self.app.primaryScreen().devicePixelRatio()

        default_font_size = 9
        # Font size multiplier for adjusting all font sizes in the app
        # 0 means no adjustment, positive values increase size, negative values decrease size
        self.font_size_multiplier = 0
        # Best Practice for Your App (aicodeprep GUI)
        # UI font stack for multilingual users
        font_stack = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans", "Noto Sans Arabic", Arial, sans-serif'
        adjusted_font_size = default_font_size + self.font_size_multiplier
        adjusted_font_size = int(adjusted_font_size * scale_factor)
        # Use system font instead of JetBrains Mono for main UI
        self.default_font = QtGui.QFont()
        self.default_font.setPointSize(adjusted_font_size)
        self.setFont(self.default_font)
        self.setStyleSheet(f"font-family: {font_stack};")
        # Font debug info
        from aicodeprep_gui.apptheme import load_custom_fonts
        loaded_fonts = load_custom_fonts()
        print("Font debug info: Loaded font families:", loaded_fonts)
        style = self.style()
        self.folder_icon = style.standardIcon(QtWidgets.QStyle.SP_DirIcon)
        self.file_icon = style.standardIcon(QtWidgets.QStyle.SP_FileIcon)

        if self.preferences_manager.window_size_from_prefs:
            w, h = self.preferences_manager.window_size_from_prefs
            self.setGeometry(100, 100, w, h)
        else:
            self.setGeometry(100, 100, int(600 * scale_factor),
                             int(400 * scale_factor))

        self.is_dark_mode = self.ui_settings_manager._load_dark_mode_setting()
        if self.is_dark_mode:
            apply_dark_palette(self.app)

        central = LogoCentralWidget()
        self.setCentralWidget(central)
        # Prefer palette-based gradient painting to reduce banding and allow multiple stops.
        # Store central as an attribute so helper can reapply on resize.
        self.central_widget = central

        # Initial application
        self.apply_gradient_to_central()

        # Reapply gradient on resize to ensure accurate object-bounding coordinates.
        # Wrap existing resizeEvent to preserve default behavior.
        original_resize = getattr(self.central_widget, "resizeEvent", None)

        def _resize_event(event):
            try:
                self.apply_gradient_to_central()
                self.update_logo_size()  # Update logo size based on window width
            except Exception:
                pass
            if original_resize:
                try:
                    original_resize(event)
                except Exception:
                    QtWidgets.QWidget.resizeEvent(self.central_widget, event)
            else:
                QtWidgets.QWidget.resizeEvent(self.central_widget, event)

        self.central_widget.resizeEvent = _resize_event

        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(20, 10, 20, 10)

        mb = self.menuBar()
        self.file_menu = mb.addMenu(self.tr("&File"))

        # Add OS-specific installer menu items
        if platform.system() == "Windows":
            from .components.installer_dialogs import RegistryManagerDialog

            def open_registry_manager():
                dialog = RegistryManagerDialog(self)
                dialog.exec()
            install_menu_act = QtGui.QAction(
                self.tr("Install Right-Click Menu..."), self)
            install_menu_act.triggered.connect(open_registry_manager)
            self.file_menu.addAction(install_menu_act)
            self.file_menu.addSeparator()

        elif platform.system() == "Darwin":
            from .components.installer_dialogs import MacInstallerDialog

            def open_mac_installer():
                dialog = MacInstallerDialog(self)
                dialog.exec()
            install_menu_act = QtGui.QAction(
                self.tr("Install Finder Quick Action..."), self)
            install_menu_act.triggered.connect(open_mac_installer)
            self.file_menu.addAction(install_menu_act)
            self.file_menu.addSeparator()

        elif platform.system() == "Linux":
            from .components.installer_dialogs import LinuxInstallerDialog

            def open_linux_installer():
                dialog = LinuxInstallerDialog(self)
                dialog.exec()
            install_menu_act = QtGui.QAction(
                self.tr("Install File Manager Action..."), self)
            install_menu_act.triggered.connect(open_linux_installer)
            self.file_menu.addAction(install_menu_act)
            self.file_menu.addSeparator()

        self.quit_act = QtGui.QAction(self.tr("&Quit"), self)
        self.quit_act.triggered.connect(self.quit_without_processing)
        self.file_menu.addAction(self.quit_act)

        self.edit_menu = mb.addMenu(self.tr("&Edit"))
        self.new_preset_act = QtGui.QAction(self.tr("&New Preset…"), self)
        self.new_preset_act.triggered.connect(self.add_new_preset_dialog)
        self.edit_menu.addAction(self.new_preset_act)

        self.open_settings_folder_act = QtGui.QAction(
            self.tr("&Open Settings Folder…"), self)
        self.open_settings_folder_act.triggered.connect(
            self.open_settings_folder)
        self.edit_menu.addAction(self.open_settings_folder_act)

        self.edit_menu.addSeparator()

        self.language_act = QtGui.QAction(
            self.tr("&Language / Idioma / 语言…"), self)
        self.language_act.triggered.connect(self.open_language_dialog)
        self.edit_menu.addAction(self.language_act)

        # Flow menu (Phase 2)
        self.flow_menu = mb.addMenu(self.tr("&Flow"))

        self.flow_import_act = QtGui.QAction(
            self.tr("&Import Flow JSON…"), self)
        self.flow_import_act.triggered.connect(self._flow_import_action)
        self.flow_menu.addAction(self.flow_import_act)

        self.flow_export_act = QtGui.QAction(
            self.tr("&Export Flow JSON…"), self)
        self.flow_export_act.triggered.connect(self._flow_export_action)
        self.flow_menu.addAction(self.flow_export_act)

        self.flow_reset_act = QtGui.QAction(
            self.tr("&Reset to Default Flow"), self)
        self.flow_reset_act.triggered.connect(self._flow_reset_action)
        self.flow_menu.addAction(self.flow_reset_act)

        self.flow_menu.addSeparator()

        flow_bestof5_act = QtGui.QAction(
            self.tr("Load Built-in: Best-of-5 (Blank)"), self)

        def _load_bestof5():
            if not self._ensure_flow_dock():
                QtWidgets.QMessageBox.warning(
                    self, "Flow Studio", "Flow Studio could not be initialized.")
                return
            if hasattr(self.flow_dock, "load_template_best_of_5_openrouter"):
                self.flow_dock.load_template_best_of_5_openrouter()
                self.flow_dock.show()
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Flow Studio", "Dock missing 'load_template_best_of_5_openrouter'.")

        flow_bestof5_act.triggered.connect(_load_bestof5)
        self.flow_menu.addAction(flow_bestof5_act)

        # Add configured Best-of-5 template
        flow_bestof5_config_act = QtGui.QAction(
            self.tr("Load Built-in: Best-of-5 (Configured)"), self)

        def _load_bestof5_configured():
            if not self._ensure_flow_dock():
                QtWidgets.QMessageBox.warning(
                    self, "Flow Studio", "Flow Studio could not be initialized.")
                return
            if hasattr(self.flow_dock, "load_template_best_of_5_configured"):
                self.flow_dock.load_template_best_of_5_configured()
                self.flow_dock.show()
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Flow Studio", "Dock missing 'load_template_best_of_5_configured'.")

        flow_bestof5_config_act.triggered.connect(_load_bestof5_configured)
        self.flow_menu.addAction(flow_bestof5_config_act)

        # Add configured Best-of-3 template
        flow_bestof3_config_act = QtGui.QAction(
            self.tr("Load Built-in: Best-of-3 (Configured)"), self)

        def _load_bestof3_configured():
            if not self._ensure_flow_dock():
                QtWidgets.QMessageBox.warning(
                    self, "Flow Studio", "Flow Studio could not be initialized.")
                return
            if hasattr(self.flow_dock, "load_template_best_of_3_configured"):
                self.flow_dock.load_template_best_of_3_configured()
                self.flow_dock.show()
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Flow Studio", "Dock missing 'load_template_best_of_3_configured'.")

        flow_bestof3_config_act.triggered.connect(_load_bestof3_configured)
        self.flow_menu.addAction(flow_bestof3_config_act)

        self.flow_menu.addSeparator()

        flow_run_act = QtGui.QAction(self.tr("Run Current Flow"), self)

        def _run_current_flow():
            if not self._ensure_flow_dock():
                QtWidgets.QMessageBox.warning(
                    self, "Flow Studio", "Flow Studio could not be initialized.")
                return
            if hasattr(self.flow_dock, "_on_run_clicked"):
                self.flow_dock._on_run_clicked()
                self.flow_dock.show()
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Flow Studio", "Dock missing '_on_run_clicked'.")
        flow_run_act.triggered.connect(_run_current_flow)
        self.flow_menu.addAction(flow_run_act)

        self.help_menu = mb.addMenu(self.tr("&Help"))
        self.links_act = QtGui.QAction(
            self.tr("&Help / Links and Guides"), self)
        self.links_act.triggered.connect(self.open_links_dialog)
        self.help_menu.addAction(self.links_act)
        self.help_menu.addSeparator()

        self.about_act = QtGui.QAction(self.tr("&About"), self)
        self.about_act.triggered.connect(self.open_about_dialog)
        self.help_menu.addAction(self.about_act)

        self.complain_act = QtGui.QAction(
            self.tr("&Send Ideas, bugs, thoughts!"), self)
        self.complain_act.triggered.connect(self.open_complain_dialog)
        self.help_menu.addAction(self.complain_act)

        if not self._is_pro_enabled():
            self.activate_pro_act = QtGui.QAction(
                self.tr("Activate &Pro…"), self)
            self.activate_pro_act.triggered.connect(
                self.dialog_manager.open_activate_pro_dialog)
            self.help_menu.addAction(self.activate_pro_act)

        # Debug menu (always available for testing i18n/a11y)
        self.debug_menu = mb.addMenu(self.tr("&Debug"))
        self.screenshot_act = QtGui.QAction(self.tr("Take Screenshot"), self)
        self.screenshot_act.triggered.connect(self._take_debug_screenshot)
        self.debug_menu.addAction(self.screenshot_act)

        self.lang_info_act = QtGui.QAction(
            self.tr("Current Language Info"), self)
        self.lang_info_act.triggered.connect(self._show_language_info)
        self.debug_menu.addAction(self.lang_info_act)

        self.a11y_check_act = QtGui.QAction(
            self.tr("Accessibility Check"), self)
        self.a11y_check_act.triggered.connect(self._run_accessibility_check)
        self.debug_menu.addAction(self.a11y_check_act)

        self.format_combo = QtWidgets.QComboBox()
        self.format_combo.addItems(["XML <code>", "Markdown ###"])
        self.format_combo.setFixedWidth(130)
        self.format_combo.setItemData(0, 'xml')
        self.format_combo.setItemData(1, 'markdown')

        fmt = getattr(self.preferences_manager,
                      "output_format_from_prefs", "xml")
        idx = 0 if fmt == "xml" else 1
        self.format_combo.setCurrentIndex(idx)
        self.format_combo.currentIndexChanged.connect(self._save_format_choice)

        self.output_label = QtWidgets.QLabel(self.tr("&Output format:"))
        self.output_label.setBuddy(self.format_combo)

        self.dark_mode_box = QtWidgets.QCheckBox(self.tr("Dark mode"))
        self.dark_mode_box.setChecked(self.is_dark_mode)
        self.dark_mode_box.stateChanged.connect(self.toggle_dark_mode)

        self.token_label = QtWidgets.QLabel(self.tr("Estimated tokens: 0"))
        main_layout.addWidget(self.token_label)
        main_layout.addSpacing(2)

        # Use PNG logo with transparent background
        import os

        # Path to the PNG logo
        self.logo_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'images', 'aicp-transparent-min.png')
        self.logo_pixmap = QtGui.QPixmap(self.logo_path)

        self.vibe_label = QtWidgets.QLabel()
        self.vibe_label.setPixmap(self.logo_pixmap)
        # Don't force scaling, use pixmap scaling
        self.vibe_label.setScaledContents(False)
        self.vibe_label.setAlignment(QtCore.Qt.AlignCenter)
        # Let it maintain aspect ratio naturally
        self.vibe_label.setMaximumHeight(100)  # Maximum logo height
        self.vibe_label.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)

        # Set background based on dark mode
        if self.is_dark_mode:
            self.vibe_label.setStyleSheet(
                "background: #000000; "
                "padding: 10px; border-radius: 8px;"
            )
        else:
            self.vibe_label.setStyleSheet(
                "background: #d3d3d3; "
                "padding: 10px; border-radius: 8px;"
            )

        # Create toggle button for logo visibility
        self.logo_toggle_btn = QtWidgets.QPushButton("⏶")  # Up arrow
        self.logo_toggle_btn.setFixedSize(30, 30)
        self.logo_toggle_btn.setToolTip(self.tr("Hide/Show Logo"))
        self.logo_toggle_btn.clicked.connect(self.toggle_logo_visibility)
        self.logo_visible = True

        banner_wrap = QtWidgets.QWidget()
        banner_layout = QtWidgets.QHBoxLayout(banner_wrap)
        banner_layout.setContentsMargins(14, 0, 14, 0)
        banner_layout.addStretch()
        banner_layout.addWidget(self.vibe_label)
        banner_layout.addWidget(self.logo_toggle_btn)
        banner_layout.addStretch()

        self.banner_wrap = banner_wrap  # Store reference for hiding/showing
        # Hide the banner by default since logo is now in tree widget background
        self.banner_wrap.setVisible(False)
        self.logo_visible = False  # Logo banner is hidden by default
        self.logo_toggle_btn.setText("⏷")  # Down arrow (show)
        self.logo_toggle_btn.setToolTip(self.tr("Show Logo Banner"))

        main_layout.addWidget(banner_wrap)
        main_layout.addSpacing(1)

        self.info_label = QtWidgets.QLabel(self.tr(
            "The selected files will be added to the LLM Context Block along with your prompt, written to fullcode.txt and copied to clipboard, ready to paste into your AI assistant."))
        self.info_label.setWordWrap(True)
        self.info_label.setOpenExternalLinks(True)
        self.info_label.setAlignment(QtCore.Qt.AlignHCenter)
        main_layout.addWidget(self.info_label)

        self.text_label = QtWidgets.QLabel(self.tr(
            "Works great with: Claude (Sonnet, Opus), GPT-5.2, Gemini, DeepSeek, Qwen, GLM 4.7, Kimi K2, Minimax M2.1 and any other models"))
        self.text_label.setWordWrap(True)
        self.text_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.text_label.setStyleSheet(
            f"font-size: {11 + self.font_size_multiplier}px; color: {'#888888' if self.is_dark_mode else '#666666'}; font-style: italic;"
        )
        main_layout.addWidget(self.text_label)

        # Initialize some required attributes
        self.selected_files = []
        self.file_token_counts = {}
        self.total_tokens = 0

        # Preset buttons setup
        prompt_header_label = QtWidgets.QLabel(
            self.tr("Prompt Preset Buttons:"))
        main_layout.addWidget(prompt_header_label)

        presets_wrapper = QtWidgets.QHBoxLayout()
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFixedHeight(52)
        scroll_area.setAccessibleName(self.tr("Prompt Presets"))
        scroll_area.setAccessibleDescription(
            self.tr("Saved prompt templates that can be quickly applied"))

        scroll_widget = QtWidgets.QWidget()
        self.preset_strip = QtWidgets.QHBoxLayout(scroll_widget)
        self.preset_strip.setContentsMargins(0, 0, 0, 0)

        add_preset_btn = QtWidgets.QPushButton("✚")
        add_preset_btn.setFixedSize(24, 24)
        add_preset_btn.setToolTip(self.tr("New Preset…"))
        add_preset_btn.clicked.connect(self.add_new_preset_dialog)
        self.preset_strip.addWidget(add_preset_btn)

        delete_preset_btn = QtWidgets.QPushButton("🗑️")
        delete_preset_btn.setFixedSize(24, 24)
        delete_preset_btn.setToolTip(self.tr("Delete a preset…"))
        delete_preset_btn.clicked.connect(self.delete_preset_dialog)
        self.preset_strip.addWidget(delete_preset_btn)

        self.preset_strip.addStretch()

        scroll_area.setWidget(scroll_widget)
        presets_wrapper.addWidget(scroll_area)
        main_layout.addLayout(presets_wrapper)

        # Add explanation text below presets
        self.preset_explanation = QtWidgets.QLabel(
            self.tr("Presets help you save more time and will be saved for later use"))
        self.preset_explanation.setObjectName("preset_explanation")
        self.preset_explanation.setStyleSheet(
            f"font-size: {10 + self.font_size_multiplier}px; color: {'#fb9b0b' if self.is_dark_mode else '#44444'};"
        )
        main_layout.addWidget(self.preset_explanation)

        main_layout.addSpacing(8)

        # Tree widget and prompt setup
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)

        self.tree_widget = LogoTreeWidget()  # Use custom tree widget with logo support
        # Start with two columns but hide the second one initially (Pro feature)
        self.tree_widget.setHeaderLabels(["File/Folder", "Skeleton Level"])
        # Hide level column by default
        self.tree_widget.setColumnHidden(1, True)
        self.tree_widget.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        # Set accessible properties for screen readers
        self.tree_widget.setAccessibleName(self.tr("File Browser"))
        self.tree_widget.setAccessibleDescription(self.tr(
            "Navigate and select files and folders to include in context. Use arrow keys to navigate, Space to toggle selection."))

        # Pro level column state tracking
        self.pro_level_column_enabled = False

        base_style = """
            QTreeView, QTreeWidget {
                outline: 2; /* Remove focus rectangle */
            }
            QTreeView::item:selected, QTreeWidget::item:selected {
                background-color: #8B0000; /* Dark red instead of blue */
                color: #ffffff;
            }
        """
        checkbox_style = get_checkbox_style_dark(
        ) if self.is_dark_mode else get_checkbox_style_light()
        self.tree_widget.setStyleSheet(base_style + checkbox_style)

        # Set the logo as a background watermark on the main window (bottom-left corner)
        # Scale logo to small size for corner watermark (120px height)
        watermark_logo = self.logo_pixmap.scaledToHeight(
            120,
            QtCore.Qt.SmoothTransformation
        )
        # Subtle watermark in corner (adjust opacity in LogoCentralWidget.__init__)
        self.central_widget.set_logo(watermark_logo)

        self.splitter.addWidget(self.tree_widget)

        prompt_widget = QtWidgets.QWidget()
        prompt_layout = QtWidgets.QVBoxLayout(prompt_widget)
        prompt_layout.setContentsMargins(0, 0, 0, 0)
        self.prompt_label = QtWidgets.QLabel(
            self.tr("Optional prompt/question for LLM (will be appended to the end):"))
        prompt_layout.addWidget(self.prompt_label)
        prompt_layout.addSpacing(8)

        self.prompt_textbox = QtWidgets.QPlainTextEdit()
        self.prompt_textbox.setPlaceholderText(
            self.tr("Type your question or prompt here (optional)…"))
        self.prompt_textbox.setAccessibleName(self.tr("Prompt Input"))
        self.prompt_textbox.setAccessibleDescription(self.tr(
            "Enter an optional prompt or question that will be appended to the generated context"))
        prompt_layout.addWidget(self.prompt_textbox)

        self.clear_prompt_btn = QtWidgets.QPushButton(self.tr("Clear"))
        self.clear_prompt_btn.setToolTip(self.tr("Clear the prompt box"))
        self.clear_prompt_btn.clicked.connect(self.prompt_textbox.clear)
        prompt_layout.addWidget(self.clear_prompt_btn)

        self.splitter.addWidget(prompt_widget)
        self.splitter.setStretchFactor(0, 4)
        self.splitter.setStretchFactor(1, 1)
        main_layout.addWidget(self.splitter)

        # Build tree from files
        self.path_to_item = {}
        root_node = self.tree_widget.invisibleRootItem()
        for abs_path, rel_path, is_checked in files:
            parts = rel_path.split(os.sep)
            parent_node = root_node
            path_so_far = ""
            for part in parts[:-1]:
                # Ensure Level column default state for intermediate folders if created
                path_so_far = os.path.join(
                    path_so_far, part) if path_so_far else part
                if path_so_far in self.path_to_item:
                    parent_node = self.path_to_item[path_so_far]
                else:
                    # Always create with two columns since tree widget always has two columns
                    new_parent = QtWidgets.QTreeWidgetItem(
                        parent_node, [part, ""])
                    new_parent.setIcon(0, self.folder_icon)
                    new_parent.setFlags(new_parent.flags()
                                        | QtCore.Qt.ItemIsUserCheckable)
                    new_parent.setCheckState(0, QtCore.Qt.Unchecked)
                    self.path_to_item[path_so_far] = new_parent
                    parent_node = new_parent

            item_text = parts[-1]
            # Always create with two columns since tree widget always has two columns
            item = QtWidgets.QTreeWidgetItem(parent_node, [item_text, ""])
            item.setData(0, QtCore.Qt.UserRole, abs_path)
            self.path_to_item[rel_path] = item

            if self.preferences_manager.prefs_loaded:
                is_checked = rel_path in self.preferences_manager.checked_files_from_prefs

            if os.path.isdir(abs_path):
                item.setIcon(0, self.folder_icon)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(0, QtCore.Qt.Unchecked)
            else:
                item.setIcon(0, self.file_icon)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                if smart_logic.is_binary_file(abs_path):
                    is_checked = False

            item.setCheckState(
                0, QtCore.Qt.Checked if is_checked else QtCore.Qt.Unchecked)

        # Do not attach Level delegate by default; installed via Pro toggle
        self.level_delegate = None

        # Connect tree signals
        self.tree_widget.itemExpanded.connect(self.on_item_expanded)
        self.tree_widget.itemChanged.connect(self.handle_item_changed)

        # Auto-expand folders containing checked files
        if self.preferences_manager.prefs_loaded and self.preferences_manager.checked_files_from_prefs:
            self._expand_folders_for_paths(
                self.preferences_manager.checked_files_from_prefs)
        else:
            # On first load (no prefs), expand based on smart-selected files
            initial_checked_paths = {rel_path for _,
                                     rel_path, is_checked in files if is_checked}
            self._expand_folders_for_paths(initial_checked_paths)

        # Checkboxes for options
        self.remember_checkbox = QtWidgets.QCheckBox(
            self.tr("Remember checked files for this folder, window size information"))
        self.remember_checkbox.setChecked(True)

        self.prompt_top_checkbox = QtWidgets.QCheckBox(
            self.tr("Add prompt/question to top"))
        self.prompt_bottom_checkbox = QtWidgets.QCheckBox(
            self.tr("Add prompt/question to bottom"))

        # Load global prompt option settings
        self._load_prompt_options()

        # Save settings when toggled
        self.prompt_top_checkbox.stateChanged.connect(
            self._save_prompt_options)
        self.prompt_bottom_checkbox.stateChanged.connect(
            self._save_prompt_options)

        # Options group
        options_group_box = QtWidgets.QGroupBox(self.tr("Options"))
        options_group_box.setCheckable(True)
        self.options_group_box = options_group_box

        options_container = QtWidgets.QWidget()
        options_content_layout = QtWidgets.QVBoxLayout(options_container)
        options_content_layout.setContentsMargins(0, 5, 0, 5)

        options_top_row = QtWidgets.QHBoxLayout()
        options_top_row.addWidget(self.output_label)
        options_top_row.addWidget(self.format_combo)
        options_top_row.addStretch()
        options_top_row.addWidget(self.dark_mode_box)
        options_content_layout.addLayout(options_top_row)

        # Remember checkbox with help icon
        remember_help = QtWidgets.QLabel(
            "<b style='color:#0098e4; font-size:14px; cursor:help;'>?</b>")
        remember_help.setToolTip(
            self.tr("Saves which files are included in the context for this folder, so you don't have to keep doing it over and over"))
        remember_help.setAlignment(QtCore.Qt.AlignVCenter)
        remember_layout = QtWidgets.QHBoxLayout()
        remember_layout.setContentsMargins(0, 0, 0, 0)
        remember_layout.addWidget(self.remember_checkbox)
        remember_layout.addWidget(remember_help)
        remember_layout.addStretch()
        options_content_layout.addLayout(remember_layout)

        # (Prompt top checkbox moved to Pro Features section below)

        # (Prompt bottom checkbox moved to Pro Features section below)

        # Font size adjustment
        font_size_layout = QtWidgets.QHBoxLayout()
        font_size_layout.setContentsMargins(0, 0, 0, 0)
        self.font_size_label = QtWidgets.QLabel(self.tr("Font Size:"))
        self.font_size_combo = QtWidgets.QComboBox()
        # Allow adjustment from -5 to +10
        for i in range(-5, 11):
            self.font_size_combo.addItem(str(i), i)
        # Set current value
        current_index = self.font_size_combo.findData(
            self.font_size_multiplier)
        if current_index >= 0:
            self.font_size_combo.setCurrentIndex(current_index)
        self.font_size_combo.setMaximumWidth(80)

        font_size_layout.addWidget(self.font_size_label)
        font_size_layout.addWidget(self.font_size_combo)
        font_size_layout.addStretch()
        options_content_layout.addLayout(font_size_layout)

        # Connect combo box to update function
        self.font_size_combo.currentIndexChanged.connect(self.update_font_size)

        group_box_main_layout = QtWidgets.QVBoxLayout(options_group_box)
        group_box_main_layout.setContentsMargins(10, 5, 10, 10)
        group_box_main_layout.addWidget(options_container)

        options_group_box.toggled.connect(options_container.setVisible)
        options_group_box.toggled.connect(self._save_panel_visibility)
        self._update_groupbox_style(self.options_group_box)
        main_layout.addWidget(self.options_group_box)

        # --- New Pro Features Group ---
        # Create horizontal layout for "Pro Features" and "Buy Pro Lifetime License"
        pro_features_row = QtWidgets.QHBoxLayout()
        self.pro_features_label = QtWidgets.QLabel(self.tr("Pro Features"))
        self.pro_features_label.setFont(QtGui.QFont(self.default_font.family(),
                                                    self.default_font.pointSize() + 2, QtGui.QFont.Bold))
        pro_features_row.addWidget(self.pro_features_label)
        pro_features_row.addStretch()
        if not pro.enabled:
            buy_pro_label = QtWidgets.QLabel(
                '<a href="https://tombrothers.gumroad.com/l/zthvs" style="color: green;">Buy Pro Lifetime License</a>')
            buy_pro_label.setOpenExternalLinks(True)
            buy_pro_label.setAlignment(QtCore.Qt.AlignLeft)
            pro_features_row.addWidget(buy_pro_label)

        premium_group_box = QtWidgets.QGroupBox()
        premium_group_box.setCheckable(True)
        self.premium_group_box = premium_group_box

        premium_container = QtWidgets.QWidget()

        premium_content_layout = QtWidgets.QVBoxLayout(premium_container)
        premium_content_layout.setContentsMargins(0, 5, 0, 5)

        # Add Preview Window toggle to premium features (always visible)
        self.preview_toggle = QtWidgets.QCheckBox(
            self.tr("Enable file preview window"))
        # Tooltip will be set conditionally below
        preview_help = QtWidgets.QLabel(
            "<b style='color:#0098D4; font-size:14px; cursor:help;'>?</b>")
        preview_help.setToolTip(
            self.tr("Shows a docked window on the right that previews file contents when you select them in the tree"))
        preview_help.setAlignment(QtCore.Qt.AlignVCenter)

        preview_layout = QtWidgets.QHBoxLayout()
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.addWidget(self.preview_toggle)
        preview_layout.addWidget(preview_help)
        preview_layout.addStretch()

        premium_content_layout.addLayout(preview_layout)

        # Add Syntax Highlighting toggle to premium features
        self.syntax_highlight_toggle = QtWidgets.QCheckBox(
            self.tr("Enable syntax highlighting in preview"))
        syntax_highlight_help = QtWidgets.QLabel(
            "<b style='color:#0098D4; font-size:14px; cursor:help;'>?</b>")
        syntax_highlight_help.setToolTip(
            self.tr("Apply syntax highlighting to code in the preview window"))
        syntax_highlight_help.setAlignment(QtCore.Qt.AlignVCenter)

        syntax_highlight_layout = QtWidgets.QHBoxLayout()
        syntax_highlight_layout.setContentsMargins(0, 0, 0, 0)
        syntax_highlight_layout.addWidget(self.syntax_highlight_toggle)
        syntax_highlight_layout.addWidget(syntax_highlight_help)
        syntax_highlight_layout.addStretch()

        premium_content_layout.addLayout(syntax_highlight_layout)

        # Flow Studio toggle (Phase 1: visible for Free as read-only; editable for Pro)
        self.flow_studio_toggle = QtWidgets.QCheckBox(
            self.tr("Enable Flow Studio (currently testing alpha version - might be glitchy!)"))
        flow_help = QtWidgets.QLabel(
            "<b style='color:#0098D4; font-size:14px; cursor:help;'>?</b>")
        flow_help.setToolTip(
            self.tr("Show the Flow Studio dock. Free mode is read-only; Pro can edit and save flows."))
        flow_help.setAlignment(QtCore.Qt.AlignVCenter)

        flow_layout = QtWidgets.QHBoxLayout()
        flow_layout.setContentsMargins(0, 0, 0, 0)
        flow_layout.addWidget(self.flow_studio_toggle)
        flow_layout.addWidget(flow_help)
        flow_layout.addStretch()
        premium_content_layout.addLayout(flow_layout)

        # Configure gating and wiring
        if pro.enabled:
            self.flow_studio_toggle.setEnabled(True)
            self.flow_studio_toggle.setToolTip(
                "Show the Flow Studio dock (editable).")
        else:
            # Still visible in Free mode but read-only
            self.flow_studio_toggle.setEnabled(True)
            self.flow_studio_toggle.setToolTip(
                "Show the Flow Studio dock (read-only in Free mode).")
        self.flow_studio_toggle.toggled.connect(self.toggle_flow_studio)

        # # Add Font selection dropdown to premium features
        # font_layout = QtWidgets.QHBoxLayout()
        # font_layout.setContentsMargins(0, 0, 0, 0)
        # font_label = QtWidgets.QLabel("Preview Font:")
        # self.font_combo = QtWidgets.QComboBox()
        # # Populate font combo with available fonts
        # self._populate_font_combo()
        # font_help = QtWidgets.QLabel(
        #     "<b style='color:#0098D4; font-size:14px; cursor:help;'>?</b>")
        # font_help.setToolTip(
        #     "Select font for preview window")
        # font_help.setAlignment(QtCore.Qt.AlignVCenter)

        # font_layout.addWidget(font_label)
        # font_layout.addWidget(self.font_combo)
        # font_layout.addWidget(font_help)
        # font_layout.addStretch()
        # premium_content_layout.addLayout(font_layout)

        # Add Font weight slider to premium features
        font_weight_layout = QtWidgets.QHBoxLayout()
        font_weight_layout.setContentsMargins(0, 0, 0, 0)
        self.font_weight_label = QtWidgets.QLabel(self.tr("Font Weight:"))
        self.font_weight_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.font_weight_slider.setRange(100, 900)  # QFont weight range
        self.font_weight_slider.setValue(200)  # Default to 200 as requested
        self.font_weight_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.font_weight_slider.setTickInterval(100)
        self.font_weight_value_label = QtWidgets.QLabel("200")
        font_weight_help = QtWidgets.QLabel(
            "<b style='color:#0098D4; font-size:14px; cursor:help;'>?</b>")
        font_weight_help.setToolTip(
            self.tr("Adjust font weight for preview window"))
        font_weight_help.setAlignment(QtCore.Qt.AlignVCenter)

        self.font_weight_label.hide()
        self.font_weight_slider.hide()
        self.font_weight_value_label.hide()
        font_weight_help.hide()
        font_weight_layout.addWidget(self.font_weight_label)
        font_weight_layout.addWidget(self.font_weight_slider)
        font_weight_layout.addWidget(self.font_weight_value_label)
        font_weight_layout.addWidget(font_weight_help)
        font_weight_layout.addStretch()
        premium_content_layout.addLayout(font_weight_layout)

        # Add prompt/question checkboxes to Pro Features section
        prompt_top_text = self.tr(
            "Add prompt/question to top - Adding to top AND bottom often gets better responses from AI models")
        prompt_bottom_text = self.tr(
            "Add prompt/question to bottom - Adding to top AND bottom often gets better responses from AI models")

        self.prompt_top_checkbox.setText(prompt_top_text)
        self.prompt_bottom_checkbox.setText(prompt_bottom_text)

        # Help icons and tooltips
        prompt_top_help = QtWidgets.QLabel(
            "<b style='color:#0078D4; font-size:14px; cursor:help;'>?</b>")
        prompt_top_help.setToolTip(
            self.tr("Research shows that asking your question before AND after the code context, can improve quality and ability of the AI responses! Highly recommended to check both of these"))
        prompt_top_help.setAlignment(QtCore.Qt.AlignVCenter)
        prompt_top_layout = QtWidgets.QHBoxLayout()
        prompt_top_layout.setContentsMargins(0, 0, 0, 0)
        prompt_top_layout.addWidget(self.prompt_top_checkbox)
        prompt_top_layout.addWidget(prompt_top_help)
        prompt_top_layout.addStretch()
        premium_content_layout.addLayout(prompt_top_layout)

        prompt_bottom_help = QtWidgets.QLabel(
            "<b style='color:#0078D4; font-size:14px; cursor:help;'>?</b>")
        prompt_bottom_help.setToolTip(
            self.tr("Research shows that asking your question before AND after the code context, can improve quality and ability of the AI responses! Highly recommended to check both of these"))
        prompt_bottom_help.setAlignment(QtCore.Qt.AlignVCenter)
        prompt_bottom_layout = QtWidgets.QHBoxLayout()
        prompt_bottom_layout.setContentsMargins(0, 0, 0, 0)
        prompt_bottom_layout.addWidget(self.prompt_bottom_checkbox)
        prompt_bottom_layout.addWidget(prompt_bottom_help)
        prompt_bottom_layout.addStretch()
        premium_content_layout.addLayout(prompt_bottom_layout)

        # Set checkbox states and enabled/disabled based on Pro status
        if pro.enabled:
            self.prompt_top_checkbox.setEnabled(True)
            self.prompt_bottom_checkbox.setEnabled(True)
            self._load_prompt_options()
        else:
            self.prompt_top_checkbox.setChecked(False)
            self.prompt_bottom_checkbox.setChecked(True)
            self.prompt_top_checkbox.setEnabled(False)
            self.prompt_bottom_checkbox.setEnabled(False)

        # Connect font controls signals
        # self.font_combo.currentTextChanged.connect(self._on_font_changed)
        self.font_weight_slider.valueChanged.connect(
            self._on_font_weight_changed)

        if pro.enabled:
            self.preview_toggle.setEnabled(True)
            self.preview_toggle.setToolTip(
                "Show docked preview of selected files")
            # Initialize preview window with selected font
            # selected_font = self.font_combo.currentText() if hasattr(
            #     self, 'font_combo') else "Space Mono"
            self.preview_window = pro.get_preview_window(
                font_name="JetBrains Mono")
            if self.preview_window:
                self.addDockWidget(
                    QtCore.Qt.RightDockWidgetArea, self.preview_window)
                self.preview_toggle.toggled.connect(self.toggle_preview_window)
                # Connect syntax highlighting toggle
                self.syntax_highlight_toggle.toggled.connect(
                    self.toggle_syntax_highlighting)

            # Load saved preview window state from preferences
            self._load_preview_window_state()
            # Load saved syntax highlighting state from preferences
            self._load_syntax_highlight_state()

            # For pro users, enable syntax highlighting and set default to checked
            self.syntax_highlight_toggle.setEnabled(True)
            self.syntax_highlight_toggle.setToolTip(
                "Apply syntax highlighting to code in the preview window")
            self.syntax_highlight_toggle.setChecked(
                True)  # Default to enabled for pro users
        else:
            self.preview_toggle.setEnabled(False)
            self.preview_toggle.setToolTip(
                "Enable file preview window (Pro Feature)")

            # Disable syntax highlighting for non-pro users
            self.syntax_highlight_toggle.setEnabled(False)
            self.syntax_highlight_toggle.setToolTip(
                "Enable syntax highlighting (Pro Feature)")

        # The main layout for the QGroupBox itself. It will contain the collapsible widget.
        premium_group_box_main_layout = QtWidgets.QVBoxLayout(
            premium_group_box)
        premium_group_box_main_layout.setContentsMargins(10, 5, 10, 10)
        premium_group_box_main_layout.addWidget(premium_container)
        premium_group_box.toggled.connect(premium_container.setVisible)
        premium_group_box.toggled.connect(self._save_panel_visibility)

        # Pro: Enable Skeleton Level column toggle
        level_layout = QtWidgets.QHBoxLayout()
        level_layout.setContentsMargins(0, 0, 0, 0)

        self.pro_level_toggle = QtWidgets.QCheckBox(
            self.tr("Enable Context Compression Modes - does not work yet, still experimenting!"))
        level_help = QtWidgets.QLabel(
            "<b style='color:#0078D4; font-size:14px; cursor:help;'>?</b>")
        level_help.setToolTip(
            self.tr("Show a second column that marks skeleton level per item"))
        level_help.setAlignment(QtCore.Qt.AlignVCenter)
        level_layout.addWidget(self.pro_level_toggle)
        level_layout.addWidget(level_help)
        level_layout.addStretch()
        premium_content_layout.addLayout(level_layout)

        if pro.enabled:
            self.pro_level_toggle.setEnabled(True)
            self.pro_level_toggle.setToolTip(
                self.tr("Show a second column that marks skeleton level per item"))
            self.pro_level_toggle.toggled.connect(self.toggle_pro_level_column)
        else:
            self.pro_level_toggle.setEnabled(False)
            self.pro_level_toggle.setToolTip(self.tr("Pro Feature"))

        # Add the new green clickable link
        # buy_pro_label is now placed in the pro_features_row above the group box
        # Remove from premium_content_layout

        # Apply style and add to main layout
        main_layout.addLayout(pro_features_row)
        self._update_groupbox_style(self.premium_group_box)
        main_layout.addWidget(self.premium_group_box)

        # --- Load saved panel visibility states ---
        self._load_panel_visibility()

        # Button layouts
        button_layout1 = QtWidgets.QHBoxLayout()
        button_layout2 = QtWidgets.QHBoxLayout()

        button_layout1.addStretch()
        self.process_button = QtWidgets.QPushButton(
            self.tr("GENERATE CONTEXT!"))
        self.process_button.setAccessibleName(
            self.tr("Generate Context Button"))
        self.process_button.setAccessibleDescription(
            self.tr("Generate context from selected files and copy to clipboard"))
        self.process_button.clicked.connect(self.process_selected)
        button_layout1.addWidget(self.process_button)

        self.select_all_button = QtWidgets.QPushButton(self.tr("Select All"))
        self.select_all_button.setAccessibleName(self.tr("Select All Button"))
        self.select_all_button.setAccessibleDescription(
            self.tr("Select all non-excluded files in the tree"))
        self.select_all_button.clicked.connect(self.select_all)
        button_layout1.addWidget(self.select_all_button)

        self.deselect_all_button = QtWidgets.QPushButton(
            self.tr("Deselect All"))
        self.deselect_all_button.setAccessibleName(
            self.tr("Deselect All Button"))
        self.deselect_all_button.setAccessibleDescription(
            self.tr("Deselect all files in the tree"))
        self.deselect_all_button.clicked.connect(self.deselect_all)
        button_layout1.addWidget(self.deselect_all_button)

        button_layout2.addStretch()
        self.load_prefs_button = QtWidgets.QPushButton(
            self.tr("Load preferences"))
        self.load_prefs_button.clicked.connect(
            self.load_from_prefs_button_clicked)
        button_layout2.addWidget(self.load_prefs_button)

        self.scan_button = QtWidgets.QPushButton(self.tr("Quit"))
        self.scan_button.clicked.connect(self.quit_without_processing)
        button_layout2.addWidget(self.scan_button)

        main_layout.addLayout(button_layout1)
        main_layout.addLayout(button_layout2)

        # Update available label
        self.update_label = QtWidgets.QLabel()
        self.update_label.setAlignment(QtCore.Qt.AlignCenter)
        self.update_label.setVisible(False)
        self.update_label.setStyleSheet(
            "color: #28a745; font-weight: bold; padding: 5px;")
        self.update_label.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByMouse)
        main_layout.addWidget(self.update_label)

        # --- Footer Layout ---
        footer_layout = QtWidgets.QHBoxLayout()

        email_text = '<a href="mailto:tom@wuu73.org">tom@wuu73.org</a>'
        email_label = QtWidgets.QLabel(email_text)
        email_label.setOpenExternalLinks(True)
        footer_layout.addWidget(email_label)

        footer_layout.addStretch()

        website_label = QtWidgets.QLabel(
            '<a href="https://wuu73.org/aicp">aicodeprep-gui</a>')
        website_label.setOpenExternalLinks(True)
        footer_layout.addWidget(website_label)

        main_layout.addLayout(footer_layout)

        self.update_token_counter()
        self.preset_manager._load_global_presets()

        # Load font size multiplier setting
        self._load_font_size_setting()

        # Ensure initial Level column state (off by default)
        # Column remains hidden until the Pro toggle is enabled.

        # --- Setup keyboard navigation: focus management and tab order ---
        # Set initial focus to file tree for keyboard navigation
        self.tree_widget.setFocus()

        # Configure logical tab order: tree → prompt → generate button → other buttons
        self.setTabOrder(self.tree_widget, self.prompt_textbox)
        self.setTabOrder(self.prompt_textbox, self.process_button)
        self.setTabOrder(self.process_button, self.select_all_button)
        self.setTabOrder(self.select_all_button, self.deselect_all_button)

        # --- Setup global keyboard shortcuts ---
        # Create application-wide shortcuts that work regardless of focus
        self.keyboard_manager.create_shortcut(
            'generate', self.process_selected)
        self.keyboard_manager.create_shortcut('select_all', self.select_all)
        self.keyboard_manager.create_shortcut(
            'deselect_all', self.deselect_all)

        # Update button tooltips to show keyboard shortcuts
        generate_shortcut = self.keyboard_manager.get_shortcut_text('generate')
        self.process_button.setToolTip(
            self.tr(f"Generate context and copy to clipboard ({generate_shortcut})"))

        select_all_shortcut = self.keyboard_manager.get_shortcut_text(
            'select_all')
        self.select_all_button.setToolTip(
            self.tr(f"Select all files ({select_all_shortcut})"))

        deselect_all_shortcut = self.keyboard_manager.get_shortcut_text(
            'deselect_all')
        self.deselect_all_button.setToolTip(
            self.tr(f"Deselect all files ({deselect_all_shortcut})"))

        # --- Show v1.2.0 update notice on first run of this version ---
        try:
            settings = QtCore.QSettings("aicodeprep-gui", "UserIdentity")
            if not settings.value("v1.2.0_update_seen", False, type=bool):
                self.dialog_manager.open_update_notice_dialog()
                settings.setValue("v1.2.0_update_seen", True)
        except Exception as e:
            logging.error(f"Failed to show v1.2.0 update notice: {e}")

    def update_font_size(self, index):
        """Update all fonts in the application based on the font size multiplier."""
        value = self.font_size_combo.itemData(index)
        self.font_size_multiplier = value

        # Update the default font
        default_font_size = 9
        if hasattr(self, 'app') and self.app:
            if platform.system() == 'Windows':
                scale_factor = self.app.primaryScreen().logicalDotsPerInch() / 96.0
            else:
                scale_factor = self.app.primaryScreen().devicePixelRatio()
        else:
            scale_factor = 1.0

        adjusted_font_size = default_font_size + self.font_size_multiplier
        adjusted_font_size = int(adjusted_font_size * scale_factor)
        # Use system font instead of JetBrains Mono for main UI
        self.default_font = QtGui.QFont()
        self.default_font.setPointSize(adjusted_font_size)

        # Update font for the main window
        self.setFont(self.default_font)

        # Update font for all child widgets recursively
        self._update_all_widget_fonts(self.default_font)

        # Update the vibe label font
        vibe_font = QtGui.QFont(self.default_font)
        vibe_font.setBold(True)
        vibe_font.setPointSize(self.default_font.pointSize() + 8)
        self.vibe_label.setFont(vibe_font)

        # Update preview window font if it exists
        if hasattr(self, 'preview_window') and self.preview_window:
            # Update the preview window with the new font
            current_font = self.preview_window.text_edit.font()
            current_font.setPointSize(self.default_font.pointSize())
            self.preview_window.text_edit.setFont(current_font)
            # Update the preview to apply the new font
            self.update_file_preview()

        # Update all widgets with dynamic font sizes
        self._update_dynamic_fonts()

        # Save the setting
        self._save_font_size_setting()

    def _update_all_widget_fonts(self, font):
        """Recursively update fonts for all child widgets."""
        # Update font for all child widgets
        for widget in self.findChildren(QtWidgets.QWidget):
            # Skip widgets that have their own specific font handling
            if widget not in [self.vibe_label]:
                # For most widgets, we'll set the font directly
                widget.setFont(font)

        # Special handling for certain widget types to ensure proper sizing
        for button in self.findChildren(QtWidgets.QPushButton):
            button_font = QtGui.QFont(font)
            button_font.setPointSize(font.pointSize())
            button.setFont(button_font)

        for label in self.findChildren(QtWidgets.QLabel):
            label_font = QtGui.QFont(font)
            label_font.setPointSize(font.pointSize())
            label.setFont(label_font)

        for combo in self.findChildren(QtWidgets.QComboBox):
            combo_font = QtGui.QFont(font)
            combo_font.setPointSize(font.pointSize())
            combo.setFont(combo_font)

        for checkbox in self.findChildren(QtWidgets.QCheckBox):
            checkbox_font = QtGui.QFont(font)
            checkbox_font.setPointSize(font.pointSize())
            checkbox.setFont(checkbox_font)

        for tree in self.findChildren(QtWidgets.QTreeWidget):
            tree_font = QtGui.QFont(font)
            tree_font.setPointSize(font.pointSize())
            tree.setFont(tree_font)

        for header in self.findChildren(QtWidgets.QHeaderView):
            header_font = QtGui.QFont(font)
            header_font.setPointSize(font.pointSize())
            header.setFont(header_font)

        for textbox in self.findChildren(QtWidgets.QPlainTextEdit):
            textbox_font = QtGui.QFont(font)
            textbox_font.setPointSize(font.pointSize())
            textbox.setFont(textbox_font)

        for slider in self.findChildren(QtWidgets.QSlider):
            slider_font = QtGui.QFont(font)
            slider_font.setPointSize(font.pointSize())
            # Note: Sliders don't typically display text, but setting for consistency
            slider.setFont(slider_font)

        for groupbox in self.findChildren(QtWidgets.QGroupBox):
            groupbox_font = QtGui.QFont(font)
            groupbox_font.setPointSize(font.pointSize())
            groupbox.setFont(groupbox_font)

    def _update_dynamic_fonts(self):
        """Update fonts for widgets that use dynamic sizing."""
        # Update preset explanation labels
        for child in self.findChildren(QtWidgets.QLabel):
            if getattr(child, "objectName", lambda: "")() == "preset_explanation":
                child.setStyleSheet(
                    f"font-size: {10 + self.font_size_multiplier}px; color: {'#fb9b0b' if self.is_dark_mode else '#444444'};"
                )

        # Update text label (check if it contains status message or default AI models text)
        if self.text_label.text():
            # Check if it's a status message (contains "Copied" or "error") or the default AI models text
            if "Copied" in self.text_label.text() or "error" in self.text_label.text() or "Warning" in self.text_label.text():
                # Get current color from existing style for status messages
                current_color = "#00c3ff" if self.is_dark_mode else "#0078d4"
                if "ff9900" in self.text_label.styleSheet():
                    current_color = "#ff9900" if self.is_dark_mode else "#cc7a00"
                elif "ff666" in self.text_label.styleSheet():
                    current_color = "#ff6666" if self.is_dark_mode else "#cc0000"

                self.text_label.setStyleSheet(
                    f"font-size: {20 + self.font_size_multiplier}px; color: {current_color}; font-weight: bold;"
                )
            else:
                # It's the default AI models text - keep the subtle styling
                self.text_label.setStyleSheet(
                    f"font-size: {11 + self.font_size_multiplier}px; color: {'#888888' if self.is_dark_mode else '#666666'}; font-style: italic;"
                )

        # Update info label
        if hasattr(self, 'info_label') and self.info_label:
            current_font_size = 9 + self.font_size_multiplier
            # Preserve existing styling but update font size
            current_style = self.info_label.styleSheet()
            if "font-size" in current_style:
                # Replace existing font-size with new one
                import re
                updated_style = re.sub(
                    r"font-size:\s*[^;]+;",
                    f"font-size: {current_font_size}px;",
                    current_style
                )
                self.info_label.setStyleSheet(updated_style)
            else:
                # Add font-size to existing style
                self.info_label.setStyleSheet(
                    f"{current_style} font-size: {current_font_size}px;"
                )

        # Update token label
        if hasattr(self, 'token_label') and self.token_label:
            current_font_size = 9 + self.font_size_multiplier
            self.token_label.setStyleSheet(
                f"font-size: {current_font_size}px;"
            )

        # Update all other labels that might have custom styling
        for label in self.findChildren(QtWidgets.QLabel):
            # Skip labels that are already handled
            if label in [self.vibe_label, self.text_label, self.info_label, self.token_label]:
                continue

            # Check if label has custom styling with font-size
            current_style = label.styleSheet()
            if current_style and "font-size" in current_style:
                current_font_size = 9 + self.font_size_multiplier
                import re
                updated_style = re.sub(
                    r"font-size:\s*[^;]+;",
                    f"font-size: {current_font_size}px;",
                    current_style
                )
                label.setStyleSheet(updated_style)

        # Update menu bar
        if self.menuBar():
            self.menuBar().setFont(QtGui.QFont(self.default_font))

        # Update all menu items
        for action in self.menuBar().actions():
            action.setFont(QtGui.QFont(self.default_font))

        # Update all menu items in submenus
        for menu in self.findChildren(QtWidgets.QMenu):
            menu.setFont(QtGui.QFont(self.default_font))
            for action in menu.actions():
                action.setFont(QtGui.QFont(self.default_font))

        # Update slider value label
        if hasattr(self, 'font_size_value_label') and self.font_size_value_label:
            current_font_size = 9 + self.font_size_multiplier
            self.font_size_value_label.setStyleSheet(
                f"font-size: {current_font_size}px;"
            )

    def _save_font_size_setting(self):
        """Save the font size multiplier setting to QSettings."""
        try:
            settings = QtCore.QSettings("aicodeprep-gui", "Appearance")
            settings.setValue("font_size_multiplier",
                              self.font_size_multiplier)
        except Exception as e:
            logging.error(f"Failed to save font size setting: {e}")

    def _load_font_size_setting(self):
        """Load the font size multiplier setting from QSettings."""
        try:
            settings = QtCore.QSettings("aicodeprep-gui", "Appearance")
            if settings.contains("font_size_multiplier"):
                saved_value = settings.value("font_size_multiplier", type=int)
                self.font_size_multiplier = saved_value
                # Set the combo box to the saved value
                current_index = self.font_size_combo.findData(saved_value)
                if current_index >= 0:
                    self.font_size_combo.setCurrentIndex(current_index)
                # Update fonts with the loaded value
                self.update_font_size(current_index)
        except Exception as e:
            logging.error(f"Failed to load font size setting: {e}")

    # Helper function needs to be a method if it uses self.default_font.
    # It was originally incorrectly defined inside __init__.

    def apply_gradient_to_central(self):
        """Apply a palette-based linear gradient to the central widget."""
        if not hasattr(self, "central_widget") or self.central_widget is None:
            return
        try:
            grad = QtGui.QLinearGradient(0, 0, 1, 1)
            grad.setCoordinateMode(QtGui.QGradient.ObjectBoundingMode)
            if getattr(self, "is_dark_mode", False):
                grad.setColorAt(0.00, QtGui.QColor("#4b455b"))
                grad.setColorAt(0.45, QtGui.QColor("#111111"))
                grad.setColorAt(1.00, QtGui.QColor("#333333"))
            else:
                grad.setColorAt(0.00, QtGui.QColor("#bbbbbb"))
                grad.setColorAt(0.35, QtGui.QColor("#eeeeee"))
                grad.setColorAt(0.70, QtGui.QColor("#999999"))
                grad.setColorAt(1.00, QtGui.QColor("#9ea4b0"))
            brush = QtGui.QBrush(grad)
            pal = self.central_widget.palette()
            pal.setBrush(QtGui.QPalette.Window, brush)
            self.central_widget.setAutoFillBackground(True)
            self.central_widget.setPalette(pal)
        except Exception as e:
            logging.error(f"apply_gradient_to_central failed: {e}")

    def _create_disabled_feature_row(self, text: str, tooltip: str) -> QtWidgets.QHBoxLayout:
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        checkbox = QtWidgets.QCheckBox(text)
        checkbox.setEnabled(False)
        layout.addWidget(checkbox)

        help_icon = QtWidgets.QLabel(
            "<b style='color:#0078D4; font-size:14px; cursor:help;'>?</b>")
        help_icon.setToolTip(tooltip)
        help_icon.setAlignment(QtCore.Qt.AlignVCenter)
        layout.addWidget(help_icon)

        layout.addStretch()
        return layout

    # Delegate methods to managers:
    def load_prefs_if_exists(self):
        return self.preferences_manager.load_prefs_if_exists()

    def save_prefs(self):
        return self.preferences_manager.save_prefs()

    def toggle_dark_mode(self, state):
        """Toggle dark/light mode and update all relevant UI elements."""
        try:
            self.is_dark_mode = bool(state)

            # Apply palette
            if self.is_dark_mode:
                apply_dark_palette(self.app)
            else:
                apply_light_palette(self.app)

            # Apply UI styles
            font_stack = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans", "Noto Sans Arabic", Arial, sans-serif'
            self.setStyleSheet(f"font-family: {font_stack};")

            base_style = """
                QTreeView, QTreeWidget {
                    outline: 2; /* Remove focus rectangle */
                }
            """
            checkbox_style = get_checkbox_style_dark(
            ) if self.is_dark_mode else get_checkbox_style_light()
            self.tree_widget.setStyleSheet(base_style + checkbox_style)

            # Update vibe label style
            if self.is_dark_mode:
                self.vibe_label.setStyleSheet(
                    "background: #000000; "
                    "padding: 10px; border-radius: 8px;"
                )
            else:
                self.vibe_label.setStyleSheet(
                    "background: #d3d3d3; "
                    "padding: 10px; border-radius: 8px;"
                )

            # Update preview window theme
            if hasattr(self, 'preview_window') and self.preview_window:
                try:
                    self.preview_window.set_dark_mode(self.is_dark_mode)
                except Exception as e:
                    logging.error(f"Preview window theme update failed: {e}")

            # Update other UI elements
            for child in self.findChildren(QtWidgets.QLabel):
                if getattr(child, "objectName", lambda: "")() == "preset_explanation":
                    child.setStyleSheet(
                        f"font-size: {10 + self.font_size_multiplier}px; color: {'#bbbbbb' if self.is_dark_mode else '#444444'};"
                    )

            if self.text_label.text():
                self.text_label.setStyleSheet(
                    f"font-size: {20 + self.font_size_multiplier}px; color: {'#00c3ff' if self.is_dark_mode else '#0078d4'}; font-weight: bold;"
                )

            self._update_groupbox_style(self.options_group_box)
            self._update_groupbox_style(self.premium_group_box)

            # Reapply gradient to central widget after theme change
            self.apply_gradient_to_central()

            # Save dark mode setting
            try:
                settings = QtCore.QSettings("aicodeprep-gui", "Appearance")
                settings.setValue("dark_mode_enabled", self.is_dark_mode)
            except Exception as e:
                logging.error(f"Failed to save dark mode setting: {e}")

        except Exception as e:
            logging.error(f"toggle_dark_mode failed: {e}")

    def toggle_logo_visibility(self):
        """Toggle the visibility of the logo banner (watermark stays in tree background)."""
        try:
            self.logo_visible = not self.logo_visible
            self.banner_wrap.setVisible(self.logo_visible)

            # Update button icon
            if self.logo_visible:
                self.logo_toggle_btn.setText("⏶")  # Up arrow (hide)
                self.logo_toggle_btn.setToolTip(self.tr("Hide Logo Banner"))
            else:
                self.logo_toggle_btn.setText("⏷")  # Down arrow (show)
                self.logo_toggle_btn.setToolTip(self.tr("Show Logo Banner"))
        except Exception as e:
            logging.error(f"toggle_logo_visibility failed: {e}")

    def update_logo_size(self):
        """Update logo size based on window width."""
        try:
            if not self.logo_visible or not hasattr(self, 'vibe_label'):
                return

            window_width = self.width()

            # Calculate responsive height: scale down logo when window is narrow
            if window_width < 600:
                logo_height = 60  # Small but readable
            elif window_width < 800:
                logo_height = 80  # Medium-small
            elif window_width < 1000:
                logo_height = 90  # Medium
            else:
                logo_height = 100  # Full size

            # Scale the pixmap to fit while maintaining aspect ratio
            scaled_pixmap = self.logo_pixmap.scaledToHeight(
                logo_height,
                QtCore.Qt.SmoothTransformation
            )
            self.vibe_label.setPixmap(scaled_pixmap)
            self.vibe_label.setMaximumHeight(logo_height)

        except Exception as e:
            logging.error(f"update_logo_size failed: {e}")

    def on_item_expanded(self, item):
        return self.tree_manager.on_item_expanded(item)

    def handle_item_changed(self, item, column):
        return self.tree_manager.handle_item_changed(item, column)

    def get_selected_files(self):
        return self.tree_manager.get_selected_files()

    def select_all(self):
        return self.tree_manager.select_all()

    def deselect_all(self):
        return self.tree_manager.deselect_all()

    def open_links_dialog(self):
        return self.dialog_manager.open_links_dialog()

    def open_about_dialog(self):
        return self.dialog_manager.open_about_dialog()

    def open_complain_dialog(self):
        return self.dialog_manager.open_complain_dialog()

    def add_new_preset_dialog(self):
        return self.dialog_manager.add_new_preset_dialog()

    def delete_preset_dialog(self):
        return self.dialog_manager.delete_preset_dialog()

    def _send_metric_event(self, event_type, token_count=None):
        return self.metrics_manager._send_metric_event(event_type, token_count)

    def open_settings_folder(self):
        return self.window_helpers.open_settings_folder()

    def open_language_dialog(self):
        """Open the language selection dialog."""
        from .components.language_dialog import LanguageSelectionDialog
        dialog = LanguageSelectionDialog(self)
        dialog.exec()

    def dragEnterEvent(self, event):
        return self.window_helpers.dragEnterEvent(event)

    def dropEvent(self, event):
        return self.window_helpers.dropEvent(event)

    def changeEvent(self, event):
        """Handle runtime language changes without requiring restart."""
        try:
            if event.type() == QtCore.QEvent.LanguageChange:
                self._retranslate_ui()
        except Exception:
            pass
        return super(FileSelectionGUI, self).changeEvent(event)

    def _retranslate_ui(self):
        """Re-apply translatable UI strings for live language switching."""
        self.setWindowTitle(self.tr("aicodeprep-gui - File Selection"))

        # Tray menu
        if hasattr(self, "tray_show_act"):
            self.tray_show_act.setText(self.tr("Show"))
        if hasattr(self, "tray_quit_act"):
            self.tray_quit_act.setText(self.tr("Quit"))

        # Menus + actions
        if hasattr(self, "file_menu"):
            self.file_menu.setTitle(self.tr("&File"))
        if hasattr(self, "quit_act"):
            self.quit_act.setText(self.tr("&Quit"))

        if hasattr(self, "edit_menu"):
            self.edit_menu.setTitle(self.tr("&Edit"))
        if hasattr(self, "new_preset_act"):
            self.new_preset_act.setText(self.tr("&New Preset…"))
        if hasattr(self, "open_settings_folder_act"):
            self.open_settings_folder_act.setText(
                self.tr("Open Settings Folder…"))
        if hasattr(self, "language_act"):
            self.language_act.setText(self.tr("&Language / Idioma / 语言…"))

        if hasattr(self, "flow_menu"):
            self.flow_menu.setTitle(self.tr("&Flow"))
        if hasattr(self, "flow_import_act"):
            self.flow_import_act.setText(self.tr("Import Flow JSON…"))
        if hasattr(self, "flow_export_act"):
            self.flow_export_act.setText(self.tr("Export Flow JSON…"))
        if hasattr(self, "flow_reset_act"):
            self.flow_reset_act.setText(self.tr("Reset to Default Flow"))

        if hasattr(self, "help_menu"):
            self.help_menu.setTitle(self.tr("&Help"))
        if hasattr(self, "links_act"):
            self.links_act.setText(self.tr("Help / Links and Guides"))
        if hasattr(self, "about_act"):
            self.about_act.setText(self.tr("&About"))
        if hasattr(self, "complain_act"):
            self.complain_act.setText(self.tr("Send Ideas, bugs, thoughts!"))
        if hasattr(self, "activate_pro_act"):
            self.activate_pro_act.setText(self.tr("Activate Pro…"))

        if hasattr(self, "debug_menu"):
            self.debug_menu.setTitle(self.tr("&Debug"))
        if hasattr(self, "screenshot_act"):
            self.screenshot_act.setText(self.tr("Take Screenshot"))
        if hasattr(self, "lang_info_act"):
            self.lang_info_act.setText(self.tr("Current Language Info"))
        if hasattr(self, "a11y_check_act"):
            self.a11y_check_act.setText(self.tr("Accessibility Check"))

        # Key labels/buttons
        if hasattr(self, "output_label"):
            self.output_label.setText(self.tr("&Output format:"))
        if hasattr(self, "dark_mode_box"):
            self.dark_mode_box.setText(self.tr("Dark mode"))
        if hasattr(self, "token_label"):
            # Preserve the current numeric value if present
            current = self.token_label.text()
            if ":" in current:
                suffix = current.split(":", 1)[1].strip()
                self.token_label.setText(
                    self.tr("Estimated tokens: 0").replace("0", suffix))
            else:
                self.token_label.setText(self.tr("Estimated tokens: 0"))
        if hasattr(self, "info_label"):
            self.info_label.setText(self.tr(
                "The selected files will be added to the LLM Context Block along with your prompt, written to fullcode.txt and copied to clipboard, ready to paste into your AI assistant."))
        if hasattr(self, "logo_toggle_btn"):
            # Tooltip depends on current state
            if getattr(self, "logo_visible", False):
                self.logo_toggle_btn.setToolTip(self.tr("Hide Logo Banner"))
            else:
                self.logo_toggle_btn.setToolTip(self.tr("Show Logo Banner"))
        if hasattr(self, "preset_explanation"):
            self.preset_explanation.setText(self.tr(
                "Presets help you save more time and will be saved for later use"))
        if hasattr(self, "prompt_label"):
            self.prompt_label.setText(self.tr(
                "Optional prompt/question for LLM (will be appended to the end):"))
        if hasattr(self, "prompt_textbox"):
            self.prompt_textbox.setPlaceholderText(
                self.tr("Type your question or prompt here (optional)…"))
        if hasattr(self, "clear_prompt_btn"):
            self.clear_prompt_btn.setText(self.tr("Clear"))
            self.clear_prompt_btn.setToolTip(self.tr("Clear the prompt box"))

        # Buttons
        if hasattr(self, "process_button"):
            self.process_button.setText(self.tr("GENERATE CONTEXT!"))
        if hasattr(self, "select_all_button"):
            self.select_all_button.setText(self.tr("Select All"))
        if hasattr(self, "deselect_all_button"):
            self.deselect_all_button.setText(self.tr("Deselect All"))
        if hasattr(self, "load_prefs_button"):
            self.load_prefs_button.setText(self.tr("Load preferences"))
        if hasattr(self, "scan_button"):
            self.scan_button.setText(self.tr("Quit"))

        # Options group
        if hasattr(self, "options_group_box"):
            self.options_group_box.setTitle(self.tr("Options"))
        if hasattr(self, "remember_checkbox"):
            self.remember_checkbox.setText(
                self.tr("Remember checked files for this folder, window size information"))
        if hasattr(self, "font_size_label"):
            self.font_size_label.setText(self.tr("Font Size:"))

        # Pro Features
        if hasattr(self, "pro_features_label"):
            self.pro_features_label.setText(self.tr("Pro Features"))
        if hasattr(self, "preview_toggle"):
            self.preview_toggle.setText(self.tr("Enable file preview window"))
        if hasattr(self, "syntax_highlight_toggle"):
            self.syntax_highlight_toggle.setText(
                self.tr("Enable syntax highlighting in preview"))
        if hasattr(self, "flow_studio_toggle"):
            self.flow_studio_toggle.setText(self.tr(
                "Enable Flow Studio (currently testing alpha version - might be glitchy!)"))
        if hasattr(self, "font_weight_label"):
            self.font_weight_label.setText(self.tr("Font Weight:"))
        if hasattr(self, "prompt_top_checkbox"):
            self.prompt_top_checkbox.setText(self.tr(
                "Add prompt/question to top - Adding to top AND bottom often gets better responses from AI models"))
        if hasattr(self, "prompt_bottom_checkbox"):
            self.prompt_bottom_checkbox.setText(self.tr(
                "Add prompt/question to bottom - Adding to top AND bottom often gets better responses from AI models"))
        if hasattr(self, "pro_level_toggle"):
            self.pro_level_toggle.setText(self.tr(
                "Enable Context Compression Modes - does not work yet, still experimenting!"))

    def showEvent(self, event):
        return self.window_helpers.showEvent(event)

    def closeEvent(self, event):
        try:
            # Cancel any pending network requests before shutdown
            if hasattr(self, 'network_manager'):
                self.network_manager.clearAccessCache()

            # ... rest of your existing closeEvent code ...

            # Don't send metrics during shutdown to avoid HTTP/2 errors
            if self.action != 'process':
                self.action = 'quit'
                # self._send_metric_event("quit")  # Disabled to prevent HTTP/2 errors

            super(FileSelectionGUI, self).closeEvent(event)
        except Exception as e:
            logging.error(f"Error during closeEvent: {e}")
            super(FileSelectionGUI, self).closeEvent(event)

    # --- Pro Level column management ---
    def install_pro_level_column(self):
        # If already installed, just show the column
        if hasattr(self, "level_delegate") and self.level_delegate:
            self.tree_widget.setColumnHidden(1, False)
            self.pro_level_column_enabled = True
            return

        # Create delegate via pro getter
        result = pro.get_level_delegate(
            self.tree_widget, is_dark_mode=self.is_dark_mode)
        if not result:
            logging.error(
                "Pro Level delegate not available; cannot install Level column.")
            return

        delegate, level_role = result
        self.level_delegate = delegate
        self.level_role = level_role

        # Set column resize modes (headers already set during initialization)
        header = self.tree_widget.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        header.resizeSection(1, 140)  # Fixed width for skeleton level column

        # Attach delegate to column 1 of the tree widget
        self.tree_widget.setItemDelegateForColumn(1, self.level_delegate)

        # Initialize all existing items with Level data
        self._initialize_level_data_for_existing_items()

        # Show the column and set flag
        self.tree_widget.setColumnHidden(1, False)
        self.pro_level_column_enabled = True

        # Sync Level column to current checkbox states
        if hasattr(self, "tree_manager"):
            try:
                self.tree_manager.sync_levels_to_checks()
            except Exception as e:
                logging.error(
                    f"Failed to sync levels to checks after enabling Level column: {e}")

    def uninstall_pro_level_column(self):
        # Hide the Level column instead of removing it
        if hasattr(self, "level_delegate") and self.level_delegate:
            self.tree_widget.setColumnHidden(1, True)
            self.pro_level_column_enabled = False

            # Force a UI refresh to ensure the column disappears immediately
            self.tree_widget.repaint()
            self.tree_widget.viewport().update()

    def _initialize_level_data_for_existing_items(self):
        """Initialize Level data for all existing tree items."""
        if not hasattr(self, 'level_role') or not self.level_delegate:
            return

        # Block signals to avoid unintended itemChanged cascades while initializing
        self.tree_widget.blockSignals(True)
        try:
            iterator = QtWidgets.QTreeWidgetItemIterator(self.tree_widget)
            while iterator.value():
                item = iterator.value()
                # Set default level (0 = "None") if not already set
                if item.data(1, self.level_role) is None:
                    item.setData(1, self.level_role, 0)
                    # Set display text
                    labels = getattr(self.level_delegate, "LEVEL_LABELS", None)
                    if labels:
                        item.setData(1, QtCore.Qt.DisplayRole, labels[0])
                # Make sure the item is editable in column 1
                flags = item.flags()
                item.setFlags(flags | QtCore.Qt.ItemIsEditable)
                iterator += 1
        finally:
            self.tree_widget.blockSignals(False)

    def toggle_pro_level_column(self, enabled: bool):
        if enabled and pro.enabled:
            self.install_pro_level_column()
        else:
            self.uninstall_pro_level_column()

    def is_pro_level_column_enabled(self):
        """Returns True if the pro level column is currently enabled and visible."""
        return getattr(self, 'pro_level_column_enabled', False)

    def _generate_arrow_pixmaps(self):
        """Generates arrow icons and saves them to the temporary directory."""
        if not self.temp_dir.isValid():
            return

        colors = {
            "light_fg": "#333333",
            "dark_fg": "#DDDDDD"
        }

        # Light theme arrows
        pix_right_light = create_arrow_pixmap(
            'right', color=colors["light_fg"])
        path_right_light = os.path.join(
            self.temp_dir.path(), "arrow_right_light.png")
        pix_right_light.save(path_right_light, "PNG")

        pix_down_light = create_arrow_pixmap('down', color=colors["light_fg"])
        path_down_light = os.path.join(
            self.temp_dir.path(), "arrow_down_light.png")
        pix_down_light.save(path_down_light, "PNG")

        # Dark theme arrows
        pix_right_dark = create_arrow_pixmap('right', color=colors["dark_fg"])
        path_right_dark = os.path.join(
            self.temp_dir.path(), "arrow_right_dark.png")
        pix_right_dark.save(path_right_dark, "PNG")

        pix_down_dark = create_arrow_pixmap('down', color=colors["dark_fg"])
        path_down_dark = os.path.join(
            self.temp_dir.path(), "arrow_down_dark.png")
        pix_down_dark.save(path_down_dark, "PNG")

        self.arrow_pixmap_paths = {
            "light": {"down": path_down_light, "right": path_right_light},
            "dark": {"down": path_down_dark, "right": path_right_dark},
        }

    def _update_groupbox_style(self, groupbox: QtWidgets.QGroupBox):
        """Applies the custom QGroupBox style based on the current theme."""
        if not groupbox or not self.temp_dir.isValid() or not self.arrow_pixmap_paths:
            return

        theme = "dark" if self.is_dark_mode else "light"
        paths = self.arrow_pixmap_paths.get(theme)
        if not paths:
            return  # Don't apply style if paths aren't generated

        style = get_groupbox_style(
            paths['down'], paths['right'], self.is_dark_mode)
        groupbox.setStyleSheet(style)

    def _start_update_check(self):
        """Starts the simple, non-blocking update check."""
        self.update_thread = QtCore.QThread()
        self.update_worker = UpdateCheckWorker()
        self.update_worker.moveToThread(self.update_thread)

        self.update_thread.started.connect(self.update_worker.run)
        self.update_worker.finished.connect(self.on_update_check_finished)

        # Clean up thread and worker after finishing
        self.update_worker.finished.connect(self.update_thread.quit)
        self.update_worker.finished.connect(self.update_worker.deleteLater)
        self.update_thread.finished.connect(self.update_thread.deleteLater)

        self.update_thread.start()

    def on_update_check_finished(self, message: str):
        """Slot to handle the result of the update check."""
        if not hasattr(self, "update_label"):
            return
        if message:
            self.update_label.setText(message)
            self.update_label.setVisible(True)
        else:
            self.update_label.setVisible(False)

    def process_selected(self):
        self._send_metric_event(
            "generate_start", token_count=self.total_tokens)
        self.action = 'process'
        selected_files = self.get_selected_files()
        chosen_fmt = self.format_combo.currentData()
        prompt = self.prompt_textbox.toPlainText().strip()

        if process_files(
            selected_files,
            "fullcode.txt",
            fmt=chosen_fmt,
            prompt=prompt,
            prompt_to_top=self.prompt_top_checkbox.isChecked(),
            prompt_to_bottom=self.prompt_bottom_checkbox.isChecked()
        ) > 0:
            output_path = os.path.join(os.getcwd(), "fullcode.txt")
            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check content size and warn if very large
            content_size_mb = len(content) / (1024 * 1024)
            if content_size_mb > 10:  # Warn for content larger than 10MB
                logging.warning(f"Large content size: {content_size_mb:.2f}MB")
                self.text_label.setText(
                    f"Large content ({content_size_mb:.1f}MB) may exceed clipboard limits. Saved to fullcode.txt.")

            # Enhanced clipboard operation with error handling
            try:
                clipboard = QtWidgets.QApplication.clipboard()
                clipboard.setText(content)
                # Verify the clipboard operation succeeded
                if clipboard.text() != content:
                    logging.warning("Clipboard verification failed")
                    self.text_label.setText(
                        "Warning: Clipboard copy may have failed. Content saved to fullcode.txt")
                    self.text_label.setStyleSheet(
                        f"font-size: {20 + self.font_size_multiplier}px; color: {'#ff9900' if self.is_dark_mode else '#cc7a00'}; font-weight: bold;"
                    )
                else:
                    logging.info(f"Copied {len(content)} chars to clipboard.")
                    self.text_label.setText(
                        "Copied to clipboard and fullcode.txt")
                    self.text_label.setStyleSheet(
                        f"font-size: {20 + self.font_size_multiplier}px; color: {'#00c3ff' if self.is_dark_mode else '#0078d4'}; font-weight: bold;"
                    )
            except Exception as e:
                logging.error(f"Failed to copy to clipboard: {e}")
                self.text_label.setText(
                    f"Clipboard error: {str(e)}. Content saved to fullcode.txt")
                self.text_label.setStyleSheet(
                    f"font-size: {20 + self.font_size_multiplier}px; color: {'#ff6666' if self.is_dark_mode else '#cc0000'}; font-weight: bold;"
                )

            self.save_prefs()

            # Increment generate count and check if we should show share dialog
            self.generate_count += 1
            settings = QtCore.QSettings("aicodeprep-gui", "UserIdentity")
            settings.setValue("generate_count", self.generate_count)

            # Show share dialog every 6th generate (skip for pro users) but no longer close the app
            if self.generate_count > 0 and self.generate_count % 6 == 0 and not pro.enabled:
                QtCore.QTimer.singleShot(500, self.show_share_dialog)

    def show_share_dialog(self):
        """Shows the share dialog and keeps the main window open."""
        self.dialog_manager.open_share_dialog()
        # The self.close() call has been removed from this method.

    def quit_without_processing(self):
        self.action = 'quit'
        self.close()

    def update_token_counter(self):
        total_tokens = 0
        for file_path in self.get_selected_files():
            if file_path not in self.file_token_counts:
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                    self.file_token_counts[file_path] = len(text) // 4
                except Exception:
                    self.file_token_counts[file_path] = 0
            total_tokens += self.file_token_counts[file_path]
        self.total_tokens = total_tokens
        self.token_label.setText(f"Estimated tokens: {total_tokens:,}")

    def _save_format_choice(self, idx):
        """Save the current format choice to preferences."""
        return self.ui_settings_manager._save_format_choice(idx)

    def load_from_prefs_button_clicked(self):
        """Load preferences when button is clicked."""
        return self.preferences_manager.load_from_prefs_button_clicked()

    def _save_prompt_options(self):
        """Save global prompt/question placement options to QSettings."""
        return self.ui_settings_manager._save_prompt_options()

    def _load_prompt_options(self):
        """Load global prompt/question placement options from QSettings."""
        return self.ui_settings_manager._load_prompt_options()

    def _save_panel_visibility(self):
        """Save collapsible panel visibility states to QSettings."""
        return self.ui_settings_manager._save_panel_visibility()

    def _load_panel_visibility(self):
        """Load collapsible panel visibility states from QSettings."""
        return self.ui_settings_manager._load_panel_visibility()

    def _expand_folders_for_paths(self, checked_paths):
        """Auto-expand folders that contain files from the given paths."""
        return self.tree_manager._expand_folders_for_paths(checked_paths)

    def _load_preview_window_state(self):
        """Load the saved preview window toggle state from preferences."""
        if hasattr(self, 'preview_toggle') and self.preferences_manager.pro_features_from_prefs:
            preview_enabled = self.preferences_manager.pro_features_from_prefs.get(
                'preview_window_enabled', False)
            # Set the checkbox state without triggering signals to avoid recursion
            self.preview_toggle.blockSignals(True)
            self.preview_toggle.setChecked(preview_enabled)
            self.preview_toggle.blockSignals(False)

            # Apply the state to the preview window
            if preview_enabled:
                self.toggle_preview_window(True)

            logging.info(
                f"Loaded preview window state from preferences: {preview_enabled}")

    def _load_syntax_highlight_state(self):
        """Load the saved syntax highlighting toggle state from preferences."""
        if hasattr(self, 'syntax_highlight_toggle') and self.preferences_manager.pro_features_from_prefs:
            syntax_highlight_enabled = self.preferences_manager.pro_features_from_prefs.get(
                'syntax_highlight_enabled', True)  # Default to True for pro users
            # Set the checkbox state without triggering signals to avoid recursion
            self.syntax_highlight_toggle.blockSignals(True)
            self.syntax_highlight_toggle.setChecked(syntax_highlight_enabled)
            self.syntax_highlight_toggle.blockSignals(False)

            logging.info(
                f"Loaded syntax highlighting state from preferences: {syntax_highlight_enabled}")

    # def _populate_font_combo(self):
    #     """Populate the font combo box with available fonts."""
    #     # Add the available fonts from the fonts/ folder
    #     font_files = [
    #         "JetBrains Mono",
    #         "Lekton",
    #         "Space Mono"
    #     ]

    #     # Add fonts to combo box
    #     for font_name in font_files:
    #         self.font_combo.addItem(font_name)

    #     # Set default selection to Space Mono
    #     self.font_combo.setCurrentText("Space Mono")

    # def _on_font_changed(self, font_name):
    #     """Handle font selection change."""
    #     if hasattr(self, 'preview_window') and self.preview_window:
    #         # Update the preview window font
    #         font = QtGui.QFont(font_name, self.default_font.pointSize())
    #         font.setWeight(QtGui.QFont.Weight(self.font_weight_slider.value()))
    #         # Ensure monospace style hint for preview fonts
    #         if font_name in ["Space Mono", "JetBrains Mono", "Lekton"]:
    #             font.setStyleHint(QtGui.QFont.Monospace)
    #         self.preview_window.text_edit.setFont(font)
    #         # Re-highlight text to apply new font
    #         self.preview_window.text_edit._highlight_text()

    def _on_font_weight_changed(self, value):
        """Handle font weight slider change."""
        # Update the value label
        self.font_weight_value_label.setText(str(value))

        if hasattr(self, 'preview_window') and self.preview_window:
            # Update the preview window font with new weight
            current_font = self.preview_window.text_edit.font()
            current_font.setWeight(QtGui.QFont.Weight(value))
            self.preview_window.text_edit.setFont(current_font)
            # Re-highlight text to apply new font weight
            self.preview_window.text_edit._highlight_text()

    def toggle_preview_window(self, enabled):
        """Toggle the preview window visibility."""
        if hasattr(self, 'preview_window') and self.preview_window:
            if enabled:
                self.preview_window.show()
                # Connect tree selection signal
                self.tree_widget.itemSelectionChanged.connect(
                    self.update_file_preview)
                # Show initial preview if something is selected
                self.update_file_preview()
            else:
                self.preview_window.hide()
                # Disconnect tree selection signal
                try:
                    self.tree_widget.itemSelectionChanged.disconnect(
                        self.update_file_preview)
                except TypeError:
                    pass  # Signal was never connected

    def toggle_syntax_highlighting(self, enabled):
        """Toggle syntax highlighting in the preview window."""
        if hasattr(self, 'preview_window') and self.preview_window:
            # Store the syntax highlighting state in the preview window
            self.preview_window.set_syntax_highlighting_enabled(enabled)
            # Refresh the preview if a file is currently being displayed
            self.update_file_preview()

    def toggle_flow_studio(self, enabled):
        """Show/hide the Flow Studio dock. In Free mode, the dock is read-only."""
        try:
            if enabled:
                if not hasattr(self, "flow_dock") or self.flow_dock is None:
                    self.flow_dock = pro.get_flow_dock()
                if self.flow_dock:
                    # Add to right dock area if not already added
                    if self.flow_dock.parent() is None:
                        self.addDockWidget(
                            QtCore.Qt.RightDockWidgetArea, self.flow_dock)
                    self.flow_dock.show()
                else:
                    logging.error("Flow Studio dock is None after creation.")
                    QtWidgets.QMessageBox.warning(
                        self,
                        "Flow Studio",
                        "Flow Studio could not be initialized. See logs for details.",
                    )
            else:
                if hasattr(self, "flow_dock") and self.flow_dock:
                    self.flow_dock.hide()
        except Exception as e:
            logging.error(f"toggle_flow_studio failed: {e}")

    # ---- Flow menu helpers (Phase 2) ----
    def _ensure_flow_dock(self) -> bool:
        """Create and dock Flow Studio if missing. Returns True on success."""
        try:
            if not hasattr(self, "flow_dock") or self.flow_dock is None:
                self.flow_dock = pro.get_flow_dock()
            if not self.flow_dock:
                logging.error("Flow Studio dock is None after creation.")
                return False
            if self.flow_dock.parent() is None:
                self.addDockWidget(
                    QtCore.Qt.RightDockWidgetArea, self.flow_dock)
            return True
        except Exception as e:
            logging.error(f"_ensure_flow_dock failed: {e}")
            return False

    def _flow_import_action(self):
        """Menu: Import Flow JSON… (Pro only; Free shows info)."""
        try:
            if not self._ensure_flow_dock():
                QtWidgets.QMessageBox.warning(
                    self, "Flow Studio", "Flow Studio could not be initialized.")
                return
            # Delegate to dock handler (has gating + QSettings dir)
            if hasattr(self.flow_dock, "_on_import_clicked"):
                self.flow_dock._on_import_clicked()
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Flow Import", "Import handler not available.")
        except Exception as e:
            logging.error(f"_flow_import_action failed: {e}")
            QtWidgets.QMessageBox.warning(self, "Flow Import", f"Error: {e}")

    def _flow_export_action(self):
        """Menu: Export Flow JSON… (Pro only; Free shows info)."""
        try:
            if not self._ensure_flow_dock():
                QtWidgets.QMessageBox.warning(
                    self, "Flow Studio", "Flow Studio could not be initialized.")
                return
            if hasattr(self.flow_dock, "_on_export_clicked"):
                self.flow_dock._on_export_clicked()
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Flow Export", "Export handler not available.")
        except Exception as e:
            logging.error(f"_flow_export_action failed: {e}")
            QtWidgets.QMessageBox.warning(self, "Flow Export", f"Error: {e}")

    def _flow_reset_action(self):
        """Menu: Reset to Default Flow (Pro only; Free shows info)."""
        try:
            if not self._ensure_flow_dock():
                QtWidgets.QMessageBox.warning(
                    self, "Flow Studio", "Flow Studio could not be initialized.")
                return
            if hasattr(self.flow_dock, "reset_to_default_flow"):
                self.flow_dock.reset_to_default_flow()
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Reset Flow", "Reset handler not available.")
        except Exception as e:
            logging.error(f"_flow_reset_action failed: {e}")
            QtWidgets.QMessageBox.warning(self, "Reset Flow", f"Error: {e}")

    def update_file_preview(self):
        """Update the preview based on current tree selection."""
        if not hasattr(self, 'preview_window') or not self.preview_window or not self.preview_window.isVisible():
            return

        selected_items = self.tree_widget.selectedItems()
        if selected_items:
            item = selected_items[0]
            file_path = item.data(0, QtCore.Qt.UserRole)
            if file_path and os.path.isfile(file_path):
                self.preview_window.preview_file(file_path)
            else:
                self.preview_window.clear_preview()
        else:
            self.preview_window.clear_preview()

    def _is_pro_enabled(self):
        """Check if pro mode is enabled globally."""
        # Check global settings for pro_enabled, license key, and verification
        try:
            settings = QtCore.QSettings("aicodeprep-gui", "ProLicense")
            pro_enabled = settings.value("pro_enabled", False, type=bool)
            if not pro_enabled:
                return False
            license_key = settings.value("license_key", "")
            license_verified = settings.value(
                "license_verified", False, type=bool)
            return bool(pro_enabled and license_key and license_verified)
        except Exception as e:
            logging.error(f"QSettings error in _is_pro_enabled: {e}")
            return False

    # ===== Debug Menu Methods (for i18n/a11y testing) =====

    def _take_debug_screenshot(self):
        """Debug menu: Take a screenshot of the main window."""
        try:
            from aicodeprep_gui.utils.screenshot_helper import capture_window_screenshot
            screenshot_path = capture_window_screenshot(
                self, filename_prefix="debug")
            QtWidgets.QMessageBox.information(
                self,
                "Screenshot Captured",
                f"Screenshot saved to:\n{screenshot_path}"
            )
        except Exception as e:
            logging.error(f"Error taking screenshot: {e}")
            QtWidgets.QMessageBox.warning(
                self,
                "Screenshot Error",
                f"Failed to capture screenshot:\n{str(e)}"
            )

    def _show_language_info(self):
        """Debug menu: Show current language information."""
        try:
            from PySide6.QtCore import QLocale

            app = QtWidgets.QApplication.instance()
            system_locale = QLocale.system()

            # Get translation manager if available
            current_ui_lang = "English (default)"
            if hasattr(app, 'translation_manager'):
                tm = app.translation_manager
                current_code = tm.get_current_language()
                # Find the language name
                for code, name in tm.get_available_languages():
                    if code == current_code:
                        current_ui_lang = f"{name} ({code})"
                        break

            info = f"""Current Language Information:

System Locale: {system_locale.name()}
Language: {system_locale.languageToString(system_locale.language())}
Country: {system_locale.countryToString(system_locale.country())}

UI Language: {current_ui_lang}

Note: Use Preferences → Language to change UI language
"""
            QtWidgets.QMessageBox.information(
                self,
                "Language Information",
                info
            )
        except Exception as e:
            logging.error(f"Error showing language info: {e}")
            QtWidgets.QMessageBox.warning(
                self,
                "Language Info Error",
                f"Failed to retrieve language info:\n{str(e)}"
            )

    def _run_accessibility_check(self):
        """Debug menu: Run accessibility compliance check."""
        try:
            from aicodeprep_gui.utils.screenshot_helper import get_text_color_contrast

            # Collect contrast info from various widgets
            results = []
            widgets_to_check = [
                ("Window Background", self),
                ("Tree Widget", self.tree_widget),
                ("Token Label", self.token_label),
            ]

            for name, widget in widgets_to_check:
                try:
                    contrast_info = get_text_color_contrast(widget)
                    status = "✓ PASS" if contrast_info["wcag_aa_normal"] else "✗ FAIL"
                    results.append(
                        f"{name}: {status} (Ratio: {contrast_info['contrast_ratio']:.2f}:1)"
                    )
                except Exception as e:
                    results.append(f"{name}: Error - {str(e)}")

            info = "Accessibility Check Results (WCAG AA):\n\n" + \
                "\n".join(results)
            info += "\n\nNote: Full accessibility features coming in Phase 2"

            QtWidgets.QMessageBox.information(
                self,
                "Accessibility Check",
                info
            )
        except Exception as e:
            logging.error(f"Error running accessibility check: {e}")
            QtWidgets.QMessageBox.warning(
                self,
                "Accessibility Check Error",
                f"Failed to run accessibility check:\n{str(e)}"
            )
