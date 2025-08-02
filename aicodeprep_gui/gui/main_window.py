# All imports from the original gui.py
import os
import sys
import platform
import logging
import uuid
import json
from datetime import datetime, date
from PySide6 import QtWidgets, QtCore, QtGui, QtNetwork
from aicodeprep_gui import __version__
from aicodeprep_gui import update_checker
from PySide6.QtCore import QTemporaryDir
from importlib import resources
from aicodeprep_gui.apptheme import (
    system_pref_is_dark,  # Keep for initial theme detection if needed
    create_arrow_pixmap, get_groupbox_style  # Keep for QGroupBox styling
)
from .theming import ThemeManager  # New import
from typing import List, Tuple
from aicodeprep_gui import smart_logic
from aicodeprep_gui.file_processor import process_files
from aicodeprep_gui import __version__
from aicodeprep_gui import pro

# New modular imports
from .components.layouts import FlowLayout
from .components.dialogs import DialogManager, VoteDialog
from .components.tree_widget import FileTreeManager
from .components.preset_buttons import PresetButtonManager
from .settings.presets import global_preset_manager
from .settings.preferences import PreferencesManager
from .settings.ui_settings import UISettingsManager
from .handlers.update_events import UpdateCheckWorker
from .utils.metrics import MetricsManager
from .utils.helpers import WindowHelpers


class FileSelectionGUI(QtWidgets.QMainWindow):
    def __init__(self, files):
        super().__init__()
        self.dialog_manager = DialogManager(self)
        self.preferences_manager = PreferencesManager(self)
        self.ui_settings_manager = UISettingsManager(self)
        self.tree_manager = FileTreeManager(self)
        self.preset_manager = PresetButtonManager(self)
        self.metrics_manager = MetricsManager(self)
        self.window_helpers = WindowHelpers(self)

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
            from PySide6.QtWidgets import QSystemTrayIcon, QMenu
            from PySide6.QtGui import QAction
            tray = QSystemTrayIcon(app_icon, parent=self)
            menu = QMenu()
            show_act = QAction("Show", self)
            quit_act = QAction("Quit", self)
            show_act.triggered.connect(self.show)
            quit_act.triggered.connect(self.quit_without_processing)
            menu.addAction(show_act)
            menu.addSeparator()
            menu.addAction(quit_act)
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

        # Show share dialog every 4th open
        if self.app_open_count > 0 and self.app_open_count % 4 == 0:
            # We use a timer to show the dialog slightly after the main window appears,
            # which feels less intrusive.
            QtCore.QTimer.singleShot(
                1500, self.dialog_manager.open_share_dialog)

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
        self.setWindowTitle("aicodeprep-gui - File Selection")
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
        font_stack = '"Segoe UI", "Ubuntu", "Helvetica Neue", Arial, sans-serif'
        default_font_size = int(default_font_size * scale_factor)
        self.default_font = QtGui.QFont("Segoe UI", default_font_size)
        self.setFont(self.default_font)
        self.setStyleSheet(f"font-family: {font_stack};")
        style = self.style()
        self.folder_icon = style.standardIcon(QtWidgets.QStyle.SP_DirIcon)
        self.file_icon = style.standardIcon(QtWidgets.QStyle.SP_FileIcon)

        if self.preferences_manager.window_size_from_prefs:
            w, h = self.preferences_manager.window_size_from_prefs
            self.setGeometry(100, 100, w, h)
        else:
            self.setGeometry(100, 100, int(600 * scale_factor),
                             int(400 * scale_factor))

        # Initialize ThemeManager
        self.theme_manager = ThemeManager(self.app)
        self.is_dark_mode = self.theme_manager.active_theme_name.lower(
        ) == "dark"  # Keep for compatibility with other parts for now
        # The initial theme will be applied by the ThemeManager itself.
        # We need to connect its theme_changed signal to update UI elements like QGroupBox styles.
        self.theme_manager.theme_changed.connect(self.on_theme_changed)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(20, 10, 20, 10)

        mb = self.menuBar()
        file_menu = mb.addMenu("&File")

        # Add OS-specific installer menu items
        if platform.system() == "Windows":
            from .components.installer_dialogs import RegistryManagerDialog

            def open_registry_manager():
                dialog = RegistryManagerDialog(self)
                dialog.exec()
            install_menu_act = QtGui.QAction(
                "Install Right-Click Menu...", self)
            install_menu_act.triggered.connect(open_registry_manager)
            file_menu.addAction(install_menu_act)
            file_menu.addSeparator()

        elif platform.system() == "Darwin":
            from .components.installer_dialogs import MacInstallerDialog

            def open_mac_installer():
                dialog = MacInstallerDialog(self)
                dialog.exec()
            install_menu_act = QtGui.QAction(
                "Install Finder Quick Action...", self)
            install_menu_act.triggered.connect(open_mac_installer)
            file_menu.addAction(install_menu_act)
            file_menu.addSeparator()

        elif platform.system() == "Linux":
            from .components.installer_dialogs import LinuxInstallerDialog

            def open_linux_installer():
                dialog = LinuxInstallerDialog(self)
                dialog.exec()
            install_menu_act = QtGui.QAction(
                "Install File Manager Action...", self)
            install_menu_act.triggered.connect(open_linux_installer)
            file_menu.addAction(install_menu_act)
            file_menu.addSeparator()

        quit_act = QtGui.QAction("&Quit", self)
        quit_act.triggered.connect(self.quit_without_processing)
        file_menu.addAction(quit_act)

        edit_menu = mb.addMenu("&Edit")
        new_preset_act = QtGui.QAction("&New Preset…", self)
        new_preset_act.triggered.connect(self.add_new_preset_dialog)
        edit_menu.addAction(new_preset_act)

        open_settings_folder_act = QtGui.QAction("Open Settings Folder…", self)
        open_settings_folder_act.triggered.connect(self.open_settings_folder)
        edit_menu.addAction(open_settings_folder_act)

        view_menu = mb.addMenu("&View")
        themes_menu = view_menu.addMenu("&Themes")

        available_themes = self.theme_manager.get_available_themes()
        for name, is_pro_theme in available_themes:
            action = QtGui.QAction(name, self)
            action.setCheckable(True)
            if is_pro_theme and not pro.enabled:
                action.setEnabled(False)
            action.triggered.connect(
                lambda checked, n=name: self.on_theme_selected(n))
            themes_menu.addAction(action)
            # Set the initial checked state
            if name == self.theme_manager.active_theme_name:
                action.setChecked(True)

        if pro.enabled:
            themes_menu.addSeparator()
            add_theme_action = QtGui.QAction("Add Custom Theme...", self)
            add_theme_action.triggered.connect(
                self.dialog_manager.open_add_theme_dialog)
            themes_menu.addAction(add_theme_action)

        help_menu = mb.addMenu("&Help")
        links_act = QtGui.QAction("Help / Links and Guides", self)
        links_act.triggered.connect(self.open_links_dialog)
        help_menu.addAction(links_act)
        help_menu.addSeparator()

        about_act = QtGui.QAction("&About", self)
        about_act.triggered.connect(self.open_about_dialog)
        help_menu.addAction(about_act)

        complain_act = QtGui.QAction("Send Ideas, bugs, thoughts!", self)
        complain_act.triggered.connect(self.open_complain_dialog)
        help_menu.addAction(complain_act)

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

        output_label = QtWidgets.QLabel("&Output format:")
        output_label.setBuddy(self.format_combo)

        self.theme_combo = QtWidgets.QComboBox()
        # Populate theme combo box
        available_themes = self.theme_manager.get_available_themes()
        for name, is_pro_theme in available_themes:
            self.theme_combo.addItem(name)
            if is_pro_theme and not pro.enabled:
                idx = self.theme_combo.findText(name)
                if idx != -1:
                    # A more robust way to disable an item:
                    self.theme_combo.model().item(idx).setEnabled(False)

        current_theme_name = self.theme_manager.active_theme_name
        idx = self.theme_combo.findText(current_theme_name)
        if idx != -1:
            self.theme_combo.setCurrentIndex(idx)
        self.theme_combo.textActivated.connect(self.on_theme_selected)

        self.token_label = QtWidgets.QLabel("Estimated tokens: 0")
        main_layout.addWidget(self.token_label)
        main_layout.addSpacing(8)

        self.vibe_label = QtWidgets.QLabel("AI Code Prep GUI")
        # Set object name for theming
        self.vibe_label.setObjectName("vibe_label")
        vibe_font = QtGui.QFont(self.default_font)
        vibe_font.setBold(True)
        vibe_font.setPointSize(self.default_font.pointSize() + 8)
        self.vibe_label.setFont(vibe_font)
        self.vibe_label.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        # The stylesheet is now set by the theme manager via QSS overrides
        self.vibe_label.setFixedHeight(44)

        banner_wrap = QtWidgets.QWidget()
        banner_layout = QtWidgets.QHBoxLayout(banner_wrap)
        banner_layout.setContentsMargins(14, 0, 14, 0)
        banner_layout.addWidget(self.vibe_label)
        main_layout.addWidget(banner_wrap)
        main_layout.addSpacing(8)

        self.info_label = QtWidgets.QLabel("The selected files will be added to the LLM Context Block along with your prompt, written to fullcode.txt and copied to clipboard, ready to paste into <a href='https://www.kimi.com/chat'>Kimi K2</a>, <a href='https://aistudio.google.com/'>Gemini</a>, <a href='https://chat.deepseek.com/'>Deepseek</a>, <a href='https://openrouter.ai/'>Openrouter</a>, <a href='https://chatgpt.com/'>ChatGPT</a>, <a href='https://claude.ai'>Claude</a>")
        self.info_label.setWordWrap(True)
        self.info_label.setOpenExternalLinks(True)
        self.info_label.setAlignment(QtCore.Qt.AlignHCenter)
        main_layout.addWidget(self.info_label)

        self.text_label = QtWidgets.QLabel("")
        self.text_label.setWordWrap(True)
        main_layout.addWidget(self.text_label)

        # Initialize some required attributes
        self.selected_files = []
        self.file_token_counts = {}
        self.total_tokens = 0

        # Preset buttons setup
        prompt_header_label = QtWidgets.QLabel("Prompt Preset Buttons:")
        main_layout.addWidget(prompt_header_label)

        presets_wrapper = QtWidgets.QHBoxLayout()
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFixedHeight(52)

        scroll_widget = QtWidgets.QWidget()
        self.preset_strip = QtWidgets.QHBoxLayout(scroll_widget)
        self.preset_strip.setContentsMargins(0, 0, 0, 0)

        add_preset_btn = QtWidgets.QPushButton("✚")
        add_preset_btn.setFixedSize(24, 24)
        add_preset_btn.setToolTip("New Preset…")
        add_preset_btn.clicked.connect(self.add_new_preset_dialog)
        self.preset_strip.addWidget(add_preset_btn)

        delete_preset_btn = QtWidgets.QPushButton("🗑️")
        delete_preset_btn.setFixedSize(24, 24)
        delete_preset_btn.setToolTip("Delete a preset…")
        delete_preset_btn.clicked.connect(self.delete_preset_dialog)
        self.preset_strip.addWidget(delete_preset_btn)

        self.preset_strip.addStretch()

        scroll_area.setWidget(scroll_widget)
        presets_wrapper.addWidget(scroll_area)
        main_layout.addLayout(presets_wrapper)

        # Add explanation text below presets
        preset_explanation = QtWidgets.QLabel(
            "Presets help you save more time and will be saved for later use")
        preset_explanation.setObjectName("preset_explanation")
        preset_explanation.setStyleSheet(
            f"font-size: 10px; color: {'#bbbbbb' if self.is_dark_mode else '#444444'};"
        )
        main_layout.addWidget(preset_explanation)

        main_layout.addSpacing(8)

        # Tree widget and prompt setup
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setHeaderLabels(["File/Folder"])
        self.tree_widget.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        # Styling is now handled by the ThemeManager
        # The initial theme will be applied, which includes QTreeWidget styles.
        pass

        self.splitter.addWidget(self.tree_widget)

        # --- NEW ---
        # Apply the initial tree widget theme right after it's created
        self._apply_tree_widget_theme()

        prompt_widget = QtWidgets.QWidget()
        prompt_layout = QtWidgets.QVBoxLayout(prompt_widget)
        prompt_layout.setContentsMargins(0, 0, 0, 0)
        prompt_layout.addWidget(QtWidgets.QLabel(
            "Optional prompt/question for LLM (will be appended to the end):"))
        prompt_layout.addSpacing(8)

        self.prompt_textbox = QtWidgets.QPlainTextEdit()
        self.prompt_textbox.setPlaceholderText(
            "Type your question or prompt here (optional)…")
        prompt_layout.addWidget(self.prompt_textbox)

        self.clear_prompt_btn = QtWidgets.QPushButton("Clear")
        self.clear_prompt_btn.setToolTip("Clear the prompt box")
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
                path_so_far = os.path.join(
                    path_so_far, part) if path_so_far else part
                if path_so_far in self.path_to_item:
                    parent_node = self.path_to_item[path_so_far]
                else:
                    new_parent = QtWidgets.QTreeWidgetItem(parent_node, [part])
                    new_parent.setIcon(0, self.folder_icon)
                    new_parent.setFlags(new_parent.flags()
                                        | QtCore.Qt.ItemIsUserCheckable)
                    new_parent.setCheckState(0, QtCore.Qt.Unchecked)
                    self.path_to_item[path_so_far] = new_parent
                    parent_node = new_parent

            item_text = parts[-1]
            item = QtWidgets.QTreeWidgetItem(parent_node, [item_text])
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
            "Remember checked files for this folder, window size information")
        self.remember_checkbox.setChecked(True)

        self.prompt_top_checkbox = QtWidgets.QCheckBox(
            "Add prompt/question to top")
        self.prompt_bottom_checkbox = QtWidgets.QCheckBox(
            "Add prompt/question to bottom")

        # Load global prompt option settings
        self._load_prompt_options()

        # Save settings when toggled
        self.prompt_top_checkbox.stateChanged.connect(
            self._save_prompt_options)
        self.prompt_bottom_checkbox.stateChanged.connect(
            self._save_prompt_options)

        # Options group
        options_group_box = QtWidgets.QGroupBox("Options")
        options_group_box.setCheckable(True)
        self.options_group_box = options_group_box

        options_container = QtWidgets.QWidget()
        options_content_layout = QtWidgets.QVBoxLayout(options_container)
        options_content_layout.setContentsMargins(0, 5, 0, 5)

        options_top_row = QtWidgets.QHBoxLayout()
        options_top_row.addWidget(output_label)
        options_top_row.addWidget(self.format_combo)
        options_top_row.addWidget(self.theme_combo)  # Add theme_combo here
        options_top_row.addStretch()
        options_content_layout.addLayout(options_top_row)

        # Remember checkbox with help icon
        remember_help = QtWidgets.QLabel(
            "<b style='color:#0078D4; font-size:14px; cursor:help;'>?</b>")
        remember_help.setToolTip(
            "Saves which files are included in the context for this folder, so you don't have to keep doing it over and over")
        remember_help.setAlignment(QtCore.Qt.AlignVCenter)
        remember_layout = QtWidgets.QHBoxLayout()
        remember_layout.setContentsMargins(0, 0, 0, 0)
        remember_layout.addWidget(self.remember_checkbox)
        remember_layout.addWidget(remember_help)
        remember_layout.addStretch()
        options_content_layout.addLayout(remember_layout)

        # Prompt top checkbox with help icon
        prompt_top_help = QtWidgets.QLabel(
            "<b style='color:#0078D4; font-size:14px; cursor:help;'>?</b>")
        prompt_top_help.setToolTip(
            "Research shows that asking your question before AND after the code context, can improve quality and ability of the AI responses! Highly recommended to check both of these")
        prompt_top_help.setAlignment(QtCore.Qt.AlignVCenter)
        prompt_top_layout = QtWidgets.QHBoxLayout()
        prompt_top_layout.setContentsMargins(0, 0, 0, 0)
        prompt_top_layout.addWidget(self.prompt_top_checkbox)
        prompt_top_layout.addWidget(prompt_top_help)
        prompt_top_layout.addStretch()
        options_content_layout.addLayout(prompt_top_layout)

        # Prompt bottom checkbox with help icon
        prompt_bottom_help = QtWidgets.QLabel(
            "<b style='color:#0078D4; font-size:14px; cursor:help;'>?</b>")
        prompt_bottom_help.setToolTip(
            "Research shows that asking your question before AND after the code context, can improve quality and ability of the AI responses! Highly recommended to check both of these")
        prompt_bottom_help.setAlignment(QtCore.Qt.AlignVCenter)
        prompt_bottom_layout = QtWidgets.QHBoxLayout()
        prompt_bottom_layout.setContentsMargins(0, 0, 0, 0)
        prompt_bottom_layout.addWidget(self.prompt_bottom_checkbox)
        prompt_bottom_layout.addWidget(prompt_bottom_help)
        prompt_bottom_layout.addStretch()
        options_content_layout.addLayout(prompt_bottom_layout)

        group_box_main_layout = QtWidgets.QVBoxLayout(options_group_box)
        group_box_main_layout.setContentsMargins(10, 5, 10, 10)
        group_box_main_layout.addWidget(options_container)

        options_group_box.toggled.connect(options_container.setVisible)
        options_group_box.toggled.connect(self._save_panel_visibility)
        self._update_groupbox_style(self.options_group_box)
        main_layout.addWidget(self.options_group_box)

        # --- New Pro Features Group ---
        premium_group_box = QtWidgets.QGroupBox("Pro Features")
        premium_group_box.setCheckable(True)
        self.premium_group_box = premium_group_box

        premium_container = QtWidgets.QWidget()

        premium_content_layout = QtWidgets.QVBoxLayout(premium_container)
        premium_content_layout.setContentsMargins(0, 5, 0, 5)

        # Helper function to create a disabled feature row
        def create_feature_row(text: str, tooltip: str) -> QtWidgets.QHBoxLayout:
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

        # No placeholder features - only real pro features below

        # Add Preview Window toggle to premium features (always visible)
        self.preview_toggle = QtWidgets.QCheckBox(
            "Enable file preview window")
        # Tooltip will be set conditionally below
        preview_help = QtWidgets.QLabel(
            "<b style='color:#0078D4; font-size:14px; cursor:help;'>?</b>")
        preview_help.setToolTip(
            "Shows a docked window on the right that previews file contents when you select them in the tree")
        preview_help.setAlignment(QtCore.Qt.AlignVCenter)

        preview_layout = QtWidgets.QHBoxLayout()
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.addWidget(self.preview_toggle)
        preview_layout.addWidget(preview_help)
        preview_layout.addStretch()

        premium_content_layout.addLayout(preview_layout)

        if pro.enabled:
            self.preview_toggle.setEnabled(True)
            self.preview_toggle.setToolTip(
                "Show docked preview of selected files")
            # Initialize preview window
            self.preview_window = pro.get_preview_window()
            if self.preview_window:
                self.addDockWidget(
                    QtCore.Qt.RightDockWidgetArea, self.preview_window)
                self.preview_toggle.toggled.connect(self.toggle_preview_window)
        else:
            self.preview_toggle.setEnabled(False)
            self.preview_toggle.setToolTip(
                "Enable file preview window (Pro Feature)")

        # The main layout for the QGroupBox itself. It will contain the collapsible widget.
        premium_group_box_main_layout = QtWidgets.QVBoxLayout(
            premium_group_box)
        premium_group_box_main_layout.setContentsMargins(10, 5, 10, 10)
        premium_group_box_main_layout.addWidget(premium_container)
        premium_group_box.toggled.connect(premium_container.setVisible)
        premium_group_box.toggled.connect(self._save_panel_visibility)

        # Apply style and add to main layout
        self._update_groupbox_style(self.premium_group_box)
        main_layout.addWidget(self.premium_group_box)

        # --- Load saved panel visibility states ---
        self._load_panel_visibility()

        # Button layouts
        button_layout1 = QtWidgets.QHBoxLayout()
        button_layout2 = QtWidgets.QHBoxLayout()

        button_layout1.addStretch()
        process_button = QtWidgets.QPushButton("GENERATE CONTEXT!")
        process_button.clicked.connect(self.process_selected)
        button_layout1.addWidget(process_button)

        select_all_button = QtWidgets.QPushButton("Select All")
        select_all_button.clicked.connect(self.select_all)
        button_layout1.addWidget(select_all_button)

        deselect_all_button = QtWidgets.QPushButton("Deselect All")
        deselect_all_button.clicked.connect(self.deselect_all)
        button_layout1.addWidget(deselect_all_button)

        button_layout2.addStretch()
        load_prefs_button = QtWidgets.QPushButton("Load preferences")
        load_prefs_button.clicked.connect(self.load_from_prefs_button_clicked)
        button_layout2.addWidget(load_prefs_button)

        quit_button = QtWidgets.QPushButton("Quit")
        quit_button.clicked.connect(self.quit_without_processing)
        button_layout2.addWidget(quit_button)

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

    # Delegate methods to managers:
    def load_prefs_if_exists(self):
        return self.preferences_manager.load_prefs_if_exists()

    def save_prefs(self):
        return self.preferences_manager.save_prefs()

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

    def dragEnterEvent(self, event):
        return self.window_helpers.dragEnterEvent(event)

    def dropEvent(self, event):
        return self.window_helpers.dropEvent(event)

    def showEvent(self, event):
        return self.window_helpers.showEvent(event)

    def closeEvent(self, event):
        return self.window_helpers.closeEvent(event)

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

    def _apply_tree_widget_theme(self):
        """
        Generates and applies a COMPLETE and THEME-AWARE stylesheet directly
        to the tree widget. This ensures both correct styling and reliable checkbox images.
        """
        if not hasattr(self, 'theme_manager'):
            return

        active_theme_data = self.theme_manager.themes[self.theme_manager.active_theme_name]
        colors = active_theme_data.get("colors", {})
        bg_color = QtGui.QColor(colors.get('window_bg', '#FFFFFF'))
        is_dark = bg_color.lightnessF() < 0.5

        unchecked_filename = "checkbox_unchecked_dark.png" if is_dark else "checkbox_unchecked.png"
        checked_filename = "checkbox_checked_dark.png" if is_dark else "checkbox_checked.png"

        unchecked_url, checked_url = "", ""
        try:
            res_base = resources.files('aicodeprep_gui.images')
            with resources.as_file(res_base.joinpath(unchecked_filename)) as p:
                unchecked_url = f'"{str(p).replace(os.sep, "/")}"'
            with resources.as_file(res_base.joinpath(checked_filename)) as p:
                checked_url = f'"{str(p).replace(os.sep, "/")}"'
        except Exception as e:
            logging.error(
                f"Could not load checkbox images for tree widget: {e}")
            return

        # This is now a COMPLETE stylesheet for the tree widget and its header
        tree_widget_stylesheet = f"""
            /* Base tree styling */
            QTreeWidget {{
                background-color: {colors.get('base_bg')};
                color: {colors.get('text_color')};
                alternate-background-color: {colors.get('alternate_base_bg')};
                border: 1px solid {colors.get('border_color')};
                outline: 0; /* Hide focus rectangle */
            }}
            
            /* Header styling */
            QHeaderView::section {{
                background-color: {colors.get('window_bg')};
                color: {colors.get('text_color')};
                padding: 5px;
                border: 1px solid {colors.get('border_color')};
                border-bottom: 2px solid {colors.get('accent_color_1')};
            }}

            /* Selection and Hover states */
            QTreeWidget::item:selected {{
                background-color: {colors.get('highlight_bg')};
                color: {colors.get('highlight_text')};
                border: 1px solid {colors.get('accent_color_2')};
            }}
            QTreeWidget::item:hover:!selected {{
                background-color: {colors.get('alternate_base_bg')};
            }}

            /* The working checkbox indicators */
            QTreeWidget::indicator {{
                width: 16px;
                height: 16px;
                border: none;
                background: transparent;
            }}
            QTreeWidget::indicator:unchecked {{
                image: url({unchecked_url});
            }}
            QTreeWidget::indicator:checked {{
                image: url({checked_url});
            }}
            QTreeWidget::indicator:partially-checked {{
                background-color: {colors.get('disabled_text_color')};
                border: 1px solid {colors.get('border_color')};
                border-radius: 2px;
            }}
        """

        self.tree_widget.setStyleSheet(tree_widget_stylesheet)

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
            QtWidgets.QApplication.clipboard().setText(content)
            logging.info(f"Copied {len(content)} chars to clipboard.")
            self.text_label.setStyleSheet(
                f"font-size: 20px; color: {'#00c3ff' if self.is_dark_mode else '#0078d4'}; font-weight: bold;"
            )
            self.text_label.setText("Copied to clipboard and fullcode.txt")
            self.save_prefs()
            QtCore.QTimer.singleShot(1500, self.close)
        else:
            self.close()

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

    def on_theme_selected(self, theme_name: str):
        """Handles theme selection from combo box or menu."""
        if theme_name and theme_name in self.theme_manager.themes:
            theme_data = self.theme_manager.themes[theme_name]
            is_pro_theme = theme_data.get("meta", {}).get("pro", False)
            if is_pro_theme and not pro.enabled:
                logging.warning(
                    f"Attempted to select Pro theme '{theme_name}' without Pro mode enabled.")
                # Revert to the current active theme in the combo box
                current_idx = self.theme_combo.findText(
                    self.theme_manager.active_theme_name)
                if current_idx != -1:
                    self.theme_combo.setCurrentIndex(current_idx)
                # Optionally, show a message to the user
                self.dialog_manager.show_info_message(
                    "Pro Feature", f"The '{theme_name}' theme is a Pro feature. Please enable Pro mode to use it.")
                return

            self.theme_manager.apply_theme(theme_name)
            # Update the checked state in the View menu
            mb = self.menuBar()
            view_menu = mb.findChild(QtWidgets.QMenu, "&View")
            if view_menu:
                themes_menu = view_menu.findChild(QtWidgets.QMenu, "&Themes")
                if themes_menu:
                    for action in themes_menu.actions():
                        if action.text() == theme_name:
                            action.setChecked(True)
                        else:
                            action.setChecked(False)
        else:
            logging.error(f"Theme '{theme_name}' not found.")

    def on_theme_changed(self, stylesheet: str, theme_data: dict):
        """Called when the ThemeManager applies a new theme."""
        colors = theme_data.get("colors", {})

        # Determine darkness from theme data for robust logic
        bg_color = QtGui.QColor(colors.get("window_bg", "#FFFFFF"))
        self.is_dark_mode = bg_color.lightnessF() < 0.5

        # The main stylesheet is already applied by the ThemeManager.
        # Only update UI elements that have dynamic styles.

        # Re-apply styles to QGroupBoxes as they use dynamic pixmap paths
        self._update_groupbox_style(self.options_group_box)
        self._update_groupbox_style(self.premium_group_box)

        # --- NEW ---
        # After the main theme is applied, re-apply our specific
        # tree widget styles to ensure the checkboxes are correct.
        self._apply_tree_widget_theme()

        # Update other specific, dynamic, or overridden elements
        qss_overrides = theme_data.get("qss_overrides", {})

        # Safely apply the vibe_label override
        vibe_override = qss_overrides.get("FileSelectionGUI #vibe_label")
        if vibe_override:
            try:
                # Safely format the override string, it might contain color placeholders
                self.vibe_label.setStyleSheet(vibe_override.format(**colors))
            except (KeyError, IndexError) as e:
                logging.warning(
                    f"Could not format vibe_label override: {e}. Applying as is.")
                self.vibe_label.setStyleSheet(vibe_override)

        # Update preset explanation text color from theme
        if hasattr(self, "preset_explanation"):
            disabled_color = colors.get("disabled_text_color", "#808080")
            self.preset_explanation.setStyleSheet(
                f"font-size: 10px; color: {disabled_color};")

        # Update the success message color
        success_color = colors.get("accent_color_1", "#0078d4")
        self.text_label.setStyleSheet(
            f"font-size: 20px; color: {success_color}; font-weight: bold;")

    def _populate_theme_controls(self):
        """Refreshes the theme combo box and View menu theme actions."""
        # Refresh combo box
        current_theme_name = self.theme_combo.currentText()
        self.theme_combo.clear()
        available_themes = self.theme_manager.get_available_themes()
        for name, is_pro_theme in available_themes:
            self.theme_combo.addItem(name)
            if is_pro_theme and not pro.enabled:
                idx = self.theme_combo.findText(name)
                if idx != -1:
                    self.theme_combo.model().item(idx).setEnabled(False)

        # Restore selection in combo box
        idx = self.theme_combo.findText(current_theme_name)
        if idx != -1:
            self.theme_combo.setCurrentIndex(idx)
        elif self.theme_manager.active_theme_name in self.theme_manager.themes:
            # Fallback to active theme if current selection is no longer valid
            idx = self.theme_combo.findText(
                self.theme_manager.active_theme_name)
            if idx != -1:
                self.theme_combo.setCurrentIndex(idx)

        # Refresh View menu
        mb = self.menuBar()
        view_menu = mb.findChild(QtWidgets.QMenu, "&View")
        if view_menu:
            themes_menu = view_menu.findChild(QtWidgets.QMenu, "&Themes")
            if themes_menu:
                # Clear existing theme actions, but keep "Add Custom Theme..." if it exists
                actions_to_remove = []
                for action in themes_menu.actions():
                    if action.text() != "Add Custom Theme...":
                        actions_to_remove.append(action)
                for action in actions_to_remove:
                    themes_menu.removeAction(action)

                # Add updated theme actions
                for name, is_pro_theme in available_themes:
                    action = QtGui.QAction(name, self)
                    action.setCheckable(True)
                    if is_pro_theme and not pro.enabled:
                        action.setEnabled(False)
                    action.triggered.connect(
                        lambda checked, n=name: self.on_theme_selected(n))
                    themes_menu.addAction(action)
                    # Set the initial checked state
                    if name == self.theme_manager.active_theme_name:
                        action.setChecked(True)
