import sys
import os
import shutil
from pathlib import Path

# Import Qt Components
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QTabWidget, QSplitter, QMenuBar, QToolBar, QFileDialog,
    QMessageBox, QLabel, QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit, QSizePolicy,
    QDialog, QDialogButtonBox, QFormLayout, QStyleFactory, QStatusBar, QGroupBox,
    QRadioButton, QCheckBox, QToolButton, QCommandLinkButton, QDateTimeEdit,
    QSlider, QScrollBar, QDial, QProgressBar, QGridLayout, QMenu, QInputDialog,
    QListWidget, QListWidgetItem
)
from PySide6.QtGui import QAction, QKeySequence, QTextCursor, QShortcut, QTextDocument
from PySide6.QtCore import Qt, Slot, QSize, QSettings, QFile, QTextStream, QDateTime, QTimer, QObject

# --- Constants ---
APP_NAME = "Cool GUI Example"
APP_VERSION = "1.0"
SETTINGS_ORG = "ExampleOrg"
SETTINGS_APP = "CoolGUIExample"
DEFAULT_WINDOW_SIZE = QSize(1200, 800)
DEFAULT_FONT_SIZE = 11
RESOURCES_DIR = Path("resources")
DEFAULT_THEME_PATH = RESOURCES_DIR / "default_theme.qss"
STYLE_THEMES = ['windows11', 'windowsvista', 'Windows', 'Fusion']
STYLE_SELECTED_THEME = STYLE_THEMES[3]  # Fusion style
COLOR_SCHEMES = ['Auto', 'Light', 'Dark']
DEFAULT_COLOR_SCHEME = COLOR_SCHEMES[0]  # Auto by default

# --- Main Application Window ---


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings(SETTINGS_ORG, SETTINGS_APP)
        self.current_search_term = ""
        self.replace_dialog = None  # For ReplaceDialog instance

        # Create resources directory if it doesn't exist
        if not RESOURCES_DIR.exists():
            RESOURCES_DIR.mkdir(parents=True)

        # Create empty default theme file if it doesn't exist
        if not DEFAULT_THEME_PATH.exists():
            with open(DEFAULT_THEME_PATH, 'w', encoding='utf-8') as file:
                file.write('')  # Write empty content

        self._init_ui()
        self._load_settings()
        self._apply_current_theme()
        self.app = QApplication.instance()

    def _init_ui(self):
        """Creates the user interface elements."""
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setGeometry(100, 100, DEFAULT_WINDOW_SIZE.width(),
                         DEFAULT_WINDOW_SIZE.height())

        # --- Central Widget & Main Layout ---
        central_widget = QWidget()  # QWidget central widget
        self.setCentralWidget(central_widget)
        # QVBoxLayout for main layout
        main_layout = QVBoxLayout(central_widget)

        # --- Menu Bar ---
        menu_bar = self.menuBar()  # QMenuBar for menu bar

        # File Menu
        file_menu = menu_bar.addMenu("&File")  # QMenu for file menu

        exit_action = QAction("E&xit", self)  # QAction for exit
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menu_bar.addMenu("&Edit")  # QMenu for edit menu
        select_all_action = QAction(
            "Select &All", self)  # QAction for select all
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(self._handle_select_all)
        edit_menu.addAction(select_all_action)

        edit_menu.addSeparator()

        find_action = QAction("&Find...", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self._handle_find)
        edit_menu.addAction(find_action)

        find_next_action = QAction("Find &Next", self)
        find_next_action.setShortcut(QKeySequence.StandardKey.FindNext)
        find_next_action.triggered.connect(self._handle_find_next)
        edit_menu.addAction(find_next_action)

        replace_action = QAction("&Replace...", self)
        replace_action.setShortcut(QKeySequence.StandardKey.Replace)
        replace_action.triggered.connect(self._handle_replace_dialog)
        edit_menu.addAction(replace_action)

        # View Menu
        view_menu = menu_bar.addMenu("&View")  # QMenu for view menu

        # Color Scheme Submenu
        color_scheme_menu = view_menu.addMenu(
            "&Color Scheme")  # QMenu for color scheme submenu

        # Add color scheme options
        self.color_scheme_actions = []

        # Auto color scheme action
        # QAction for auto color scheme
        auto_scheme_action = QAction("Auto", self)
        auto_scheme_action.setCheckable(True)
        auto_scheme_action.setData(0)  # Index for Auto in Qt.ColorScheme
        auto_scheme_action.triggered.connect(self._on_color_scheme_selected)
        color_scheme_menu.addAction(auto_scheme_action)
        self.color_scheme_actions.append(auto_scheme_action)

        # Light color scheme action
        # QAction for light color scheme
        light_scheme_action = QAction("Light", self)
        light_scheme_action.setCheckable(True)
        light_scheme_action.setData(1)  # Index for Light in Qt.ColorScheme
        light_scheme_action.triggered.connect(self._on_color_scheme_selected)
        color_scheme_menu.addAction(light_scheme_action)
        self.color_scheme_actions.append(light_scheme_action)

        # Dark color scheme action
        # QAction for dark color scheme
        dark_scheme_action = QAction("Dark", self)
        dark_scheme_action.setCheckable(True)
        dark_scheme_action.setData(2)  # Index for Dark in Qt.ColorScheme
        dark_scheme_action.triggered.connect(self._on_color_scheme_selected)
        color_scheme_menu.addAction(dark_scheme_action)
        self.color_scheme_actions.append(dark_scheme_action)

        # Theme Submenu
        theme_menu = view_menu.addMenu("&Theme")  # QMenu for theme submenu

        # Add theme options
        self.theme_actions = []

        # Load Custom QSS action
        # QAction for loading custom QSS
        load_qss_action = QAction("Load Custom QSS...", self)
        load_qss_action.triggered.connect(self._load_custom_qss)
        theme_menu.addAction(load_qss_action)

        # Add separator
        theme_menu.addSeparator()

        # Default Fusion Style action
        # QAction for default Fusion style
        default_fusion_action = QAction("Default Fusion Style", self)
        default_fusion_action.triggered.connect(
            self._apply_default_fusion_style)
        theme_menu.addAction(default_fusion_action)

        # --- Main Horizontal Splitter (Top/Bottom Panes) ---
        # QSplitter for main horizontal split
        main_splitter_h = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(main_splitter_h, 1)  # Make splitter stretch

        # --- Example Widgets Section ---
        example_widgets_layout = QHBoxLayout()
        main_layout.addLayout(example_widgets_layout)

        # Create Buttons Group Box
        buttons_group_box = self._create_buttons_group_box()
        example_widgets_layout.addWidget(buttons_group_box)

        # Create Input Widgets Group Box
        input_widgets_group_box = self._create_input_widgets_group_box()
        example_widgets_layout.addWidget(input_widgets_group_box)

        # Create Progress Bar
        self.progress_bar = self._create_progress_bar()
        main_layout.addWidget(self.progress_bar)

        # --- Top Pane (Display Area) ---
        top_pane_widget = QWidget()  # QWidget for top pane
        top_pane_layout = QHBoxLayout(
            top_pane_widget)  # QHBoxLayout for top pane
        top_pane_layout.setContentsMargins(0, 0, 0, 0)
        # QSplitter for vertical display split
        display_splitter_v = QSplitter(Qt.Orientation.Horizontal)
        top_pane_layout.addWidget(display_splitter_v)
        main_splitter_h.addWidget(top_pane_widget)

        # --- Left Display (Story) ---
        left_display_widget = QWidget()  # QWidget for left display
        left_display_layout = QVBoxLayout(
            left_display_widget)  # QVBoxLayout for left display
        story_label = QLabel("Content Display:")  # QLabel for story label
        left_display_layout.addWidget(story_label)
        self.story_display = QTextEdit()  # QTextEdit for story display
        self.story_display.setReadOnly(True)
        self.story_display.setPlaceholderText("Content will be displayed here")
        left_display_layout.addWidget(self.story_display)
        display_splitter_v.addWidget(left_display_widget)
        self.story_display.textChanged.connect(
            self._update_counts)  # Connect signal

        # --- Right Display (Monitor Tabs) ---
        right_display_widget = QWidget()  # QWidget for right display
        right_display_layout = QVBoxLayout(
            right_display_widget)  # QVBoxLayout for right display
        self.monitor_tabs = QTabWidget()  # QTabWidget for monitor tabs
        right_display_layout.addWidget(self.monitor_tabs)
        display_splitter_v.addWidget(right_display_widget)

        # Info Tab
        info_tab = QWidget()  # QWidget for info tab
        info_layout = QVBoxLayout(info_tab)  # QVBoxLayout for info tab
        self.info_display = QTextEdit()  # QTextEdit for info display
        self.info_display.setReadOnly(True)
        self.info_display.setPlaceholderText(
            "Information will be displayed here")
        info_layout.addWidget(self.info_display)
        self.monitor_tabs.addTab(info_tab, "Info")

        # Settings Tab
        settings_tab = QWidget()  # QWidget for settings tab
        # QVBoxLayout for settings tab
        settings_layout = QVBoxLayout(settings_tab)
        self.settings_display = QTextEdit()  # QTextEdit for settings display
        self.settings_display.setReadOnly(True)
        self.settings_display.setPlaceholderText(
            "Settings information will be displayed here")
        settings_layout.addWidget(self.settings_display)
        self.monitor_tabs.addTab(settings_tab, "Settings")

        # Outline Tab
        outline_tab = QWidget()  # QWidget for outline tab
        # QVBoxLayout for outline tab
        outline_layout = QVBoxLayout(outline_tab)
        self.outline_display = QTextEdit()  # QTextEdit for outline display
        self.outline_display.setPlaceholderText(
            "Enter your story outline here...")
        outline_layout.addWidget(self.outline_display)
        self.monitor_tabs.addTab(outline_tab, "Outline")

        # Chat Preview Tab
        chat_preview_tab = QWidget()
        chat_preview_layout = QVBoxLayout(chat_preview_tab)
        self.chat_preview_display = QTextEdit()
        self.chat_preview_display.setReadOnly(True)
        self.chat_preview_display.setPlaceholderText(
            "Chatlog will appear here...")
        chat_preview_layout.addWidget(self.chat_preview_display)

        chat_input_bar_layout = QHBoxLayout()
        self.chat_input_line = QLineEdit()
        self.chat_input_line.setPlaceholderText("Type message...")
        chat_input_bar_layout.addWidget(self.chat_input_line)
        send_chat_button = QPushButton("Send")
        send_chat_button.clicked.connect(self._handle_send_chat_message)
        chat_input_bar_layout.addWidget(send_chat_button)
        chat_preview_layout.addLayout(chat_input_bar_layout)
        self.monitor_tabs.addTab(chat_preview_tab, "Chat Preview")

        # Canon Tab
        canon_tab_widget = QWidget()
        canon_layout = QVBoxLayout(canon_tab_widget)
        self.canon_display = QTextEdit()
        self.canon_display.setPlaceholderText(
            "Enter canon details, established facts, and continuity notes here...")
        canon_layout.addWidget(self.canon_display)
        self.monitor_tabs.addTab(canon_tab_widget, "Canon")

        # World Setting Tab
        world_setting_tab_widget = QWidget()
        world_setting_layout = QVBoxLayout(world_setting_tab_widget)
        self.world_setting_display = QTextEdit()
        self.world_setting_display.setPlaceholderText(
            "Describe the world, its rules, locations, and overall atmosphere...")
        world_setting_layout.addWidget(self.world_setting_display)
        self.monitor_tabs.addTab(world_setting_tab_widget, "World Setting")

        # Character Profiles Tab
        character_profiles_tab_widget = QWidget()
        character_profiles_layout = QVBoxLayout(character_profiles_tab_widget)
        self.character_profiles_display = QTextEdit()
        self.character_profiles_display.setPlaceholderText(
            "Manage character sheets, backstories, relationships, and arcs...")
        character_profiles_layout.addWidget(self.character_profiles_display)
        self.monitor_tabs.addTab(
            character_profiles_tab_widget, "Character Profiles")

        # Checklist Tab
        checklist_tab_widget = QWidget()
        checklist_layout = QVBoxLayout(checklist_tab_widget)
        self.checklist_widget = QListWidget()
        self.checklist_widget.setSelectionMode(
            QListWidget.SelectionMode.ExtendedSelection)  # Allow multi-select
        checklist_layout.addWidget(self.checklist_widget)

        checklist_input_layout = QHBoxLayout()
        self.checklist_input_line = QLineEdit()
        self.checklist_input_line.setPlaceholderText("Enter new task...")
        checklist_input_layout.addWidget(self.checklist_input_line)
        add_task_button = QPushButton("Add Task")
        add_task_button.clicked.connect(self._handle_add_checklist_item)
        checklist_input_layout.addWidget(add_task_button)
        checklist_layout.addLayout(checklist_input_layout)

        remove_task_button = QPushButton("Remove Selected Tasks")
        remove_task_button.clicked.connect(self._handle_remove_checklist_item)
        checklist_layout.addWidget(remove_task_button)
        self.monitor_tabs.addTab(checklist_tab_widget, "Checklist")

        # --- Bottom Pane (Input Area Tabs) ---
        bottom_pane_widget = QWidget()  # QWidget for bottom pane
        bottom_pane_layout = QVBoxLayout(
            bottom_pane_widget)  # QVBoxLayout for bottom pane
        bottom_pane_layout.setContentsMargins(
            0, 5, 0, 0)  # Add some top margin
        self.input_tabs = QTabWidget()  # QTabWidget for input tabs
        bottom_pane_layout.addWidget(self.input_tabs)
        main_splitter_h.addWidget(bottom_pane_widget)

        # Narrative Input Tab
        main_input_tab = QWidget()  # QWidget for main input tab
        # QVBoxLayout for main input tab
        main_input_layout = QVBoxLayout(main_input_tab)
        self.main_input = QTextEdit()  # QTextEdit for main input
        self.main_input.setPlaceholderText("Enter your narrative text here...")
        main_input_layout.addWidget(self.main_input)
        main_input_buttons_layout = QHBoxLayout()  # QHBoxLayout for main input buttons
        send_button_main = QPushButton("Send")  # QPushButton for send
        send_button_main.clicked.connect(self._handle_send)
        main_input_buttons_layout.addWidget(send_button_main)
        main_input_layout.addLayout(main_input_buttons_layout)
        self.input_tabs.addTab(main_input_tab, "Narrative Input")

        # System Prompt Input Tab
        secondary_input_tab = QWidget()  # QWidget for secondary input tab
        # QVBoxLayout for secondary input tab
        secondary_input_layout = QVBoxLayout(secondary_input_tab)
        self.secondary_input = QTextEdit()  # QTextEdit for secondary input
        self.secondary_input.setPlaceholderText(
            "Define system prompt or instructions here...")
        secondary_input_layout.addWidget(self.secondary_input)
        # QHBoxLayout for secondary input buttons
        secondary_input_buttons_layout = QHBoxLayout()
        send_button_secondary = QPushButton("Send")  # QPushButton for send
        send_button_secondary.clicked.connect(self._handle_send)
        secondary_input_buttons_layout.addWidget(send_button_secondary)
        secondary_input_layout.addLayout(secondary_input_buttons_layout)
        self.input_tabs.addTab(secondary_input_tab, "System Prompt Input")

        # --- Initial Splitter Sizes ---
        main_splitter_h.setSizes(
            [int(self.height() * 0.65), int(self.height() * 0.35)])
        display_splitter_v.setSizes(
            [int(self.width() * 0.6), int(self.width() * 0.4)])

        # --- Bottom Toolbar ---
        toolbar = QToolBar("Main Toolbar")  # QToolBar for toolbar
        toolbar.setIconSize(QSize(16, 16))  # Smaller icons if used
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, toolbar)

        # Style Selector (ComboBox)
        toolbar.addWidget(QLabel(" Style: "))  # QLabel for style
        self.style_selector = QComboBox()  # QComboBox for style selection
        self.style_selector.addItems(STYLE_THEMES)
        self.style_selector.setCurrentText(
            STYLE_SELECTED_THEME)  # Select Fusion by default
        self.style_selector.setMinimumWidth(150)
        self.style_selector.currentTextChanged.connect(self._on_style_changed)
        toolbar.addWidget(self.style_selector)

        # Temperature (DoubleSpinBox)
        toolbar.addWidget(QLabel(" Temp: "))  # QLabel for temperature
        self.temp_spinbox = QDoubleSpinBox()  # QDoubleSpinBox for temperature
        self.temp_spinbox.setRange(0.0, 2.0)
        self.temp_spinbox.setSingleStep(0.1)
        self.temp_spinbox.setValue(0.7)  # Default temp
        toolbar.addWidget(self.temp_spinbox)

        # Max Tokens (SpinBox)
        toolbar.addWidget(QLabel(" Max Tokens: "))  # QLabel for max tokens
        self.max_tokens_spinbox = QSpinBox()  # QSpinBox for max tokens
        self.max_tokens_spinbox.setRange(50, 8192)
        self.max_tokens_spinbox.setSingleStep(10)
        self.max_tokens_spinbox.setValue(1024)  # Default max tokens
        toolbar.addWidget(self.max_tokens_spinbox)

        toolbar.addSeparator()

        # XML Tag Input (LineEdit)
        toolbar.addWidget(QLabel(" Tag: "))  # QLabel for XML tag
        self.xml_tag_input = QLineEdit()  # QLineEdit for XML tag input
        self.xml_tag_input.setPlaceholderText("e.g., <instruction>")
        self.xml_tag_input.setFixedWidth(120)
        toolbar.addWidget(self.xml_tag_input)

        toolbar.addSeparator()

        # Font Size (SpinBox)
        toolbar.addWidget(QLabel(" Font Size: "))  # QLabel for font size
        self.font_size_spinbox = QSpinBox()  # QSpinBox for font size
        self.font_size_spinbox.setRange(8, 24)
        self.font_size_spinbox.setValue(DEFAULT_FONT_SIZE)
        self.font_size_spinbox.valueChanged.connect(self._update_font_size)
        toolbar.addWidget(self.font_size_spinbox)

        # Theme Toggle Button (QPushButton with checkable property)
        # QPushButton for theme toggle
        self.theme_button = QPushButton("Dark Mode")
        self.theme_button.setCheckable(True)
        self.theme_button.toggled.connect(self._toggle_color_scheme)
        toolbar.addWidget(self.theme_button)

        toolbar.addSeparator()

        # System Prompt Selector (ComboBox)
        toolbar.addWidget(QLabel(" Sys Prompt: "))  # QLabel for system prompt
        # QComboBox for system prompt selection
        self.system_prompt_selector = QComboBox()
        self.system_prompt_selector.addItems(
            ["Default", "Creative", "Technical"])
        self.system_prompt_selector.setMinimumWidth(150)
        toolbar.addWidget(self.system_prompt_selector)

        # Send Button (Main Action) (QPushButton)
        self.send_button = QPushButton("Send")  # QPushButton for send
        self.send_button.setToolTip("Send input based on active tab")
        self.send_button.clicked.connect(self._handle_send)
        toolbar.addWidget(self.send_button)

        # --- Status Bar ---
        self.status_bar = QStatusBar()  # QStatusBar for status bar
        self.setStatusBar(self.status_bar)

        self.line_count_label = QLabel("Lines: 0")
        self.word_count_label = QLabel("Words: 0")
        self.status_bar.addPermanentWidget(self.line_count_label)
        self.status_bar.addPermanentWidget(self.word_count_label)

        self.status_bar.showMessage("Ready")

        # Add sample content to demonstrate the UI
        self._add_sample_content()
        self._update_counts()  # Initial calculation for sample content

        # Print available styles
        print(f"Available styles: {QStyleFactory.keys()}")

    @Slot()
    def _update_counts(self):
        """Updates the word and line counts in the status bar."""
        text = self.story_display.toPlainText()
        word_count = len(text.split()) if text else 0
        # blockCount gives paragraph count; for visual lines, it's more complex if wrapping is on.
        # For simple newline counting:
        # line_count = text.count('\n') + 1 if text else 0
        # Using blockCount is more conventional for QTextEdit lines.
        line_count = self.story_display.document().blockCount()

        self.word_count_label.setText(f"Words: {word_count}")
        self.line_count_label.setText(f"Lines: {line_count}")

    def _add_sample_content(self):
        """Adds sample content to the display area."""
        sample_text = """# Cool GUI Example

This is a demonstration of a cool GUI implementation using PySide6.

## Features:
- Color Scheme selection (Auto, Light, Dark) via View > Color Scheme menu
- Toggle between light and dark modes with the Dark Mode button
- Load custom QSS themes (experimental feature)
- Style selection via the Style dropdown
- Default Fusion style option in View > Theme menu
- Adjustable font size
- Tab-based input area
- Splitter for resizable panels
- Various example widgets (buttons, input fields, progress bar)

## How to Use:
1. Try the Auto/Light/Dark options in the View > Color Scheme menu
2. Toggle between Light/Dark modes using the button in the toolbar
3. Try different Qt styles from the Style dropdown in the toolbar
4. Experiment with custom themes via View > Theme > Load Custom QSS (experimental)
5. Select "Default Fusion Style" from the View > Theme menu to reset
6. Experiment with the example widgets below

Note: The Auto/Light/Dark color schemes are the recommended way to handle theming. Custom QSS themes are experimental and may not work perfectly with all styles.
"""
        self.story_display.setMarkdown(sample_text)

        info_text = """# Information Panel

This panel displays information about the application.

## Widget Classes Used:
- QMainWindow: Main application window
- QWidget: Container widgets
- QVBoxLayout/QHBoxLayout: Layout managers
- QSplitter: Resizable panel dividers
- QTabWidget: Tab containers
- QTextEdit: Text editing/display areas
- QPushButton: Action buttons
- QLabel: Text labels
- QSpinBox: Numeric input for font size
- QToolBar: Toolbar container
- QStatusBar: Status information
- QAction: Menu actions
- QGroupBox: Grouped widget container
- QRadioButton: Exclusive selection button
- QCheckBox: Checkable option button
- QToolButton: Compact button with menu support
- QCommandLinkButton: Vista-style link button
- QDateTimeEdit: Date and time editor
- QSlider: Sliding value selector
- QScrollBar: Scrolling control
- QDial: Rotary value control
- QProgressBar: Progress indicator
"""
        self.info_display.setMarkdown(info_text)

        settings_text = """# Theme and Style Settings

## Color Schemes (Recommended)
The application supports system color schemes via the View > Color Scheme menu:
- Auto: Uses the system default (light or dark based on OS settings)
- Light: Forces light mode
- Dark: Forces dark mode

The Dark Mode toggle button in the toolbar provides a quick way to switch between Light and Dark modes.

## Custom Themes (Experimental)
The application supports custom themes via QSS (Qt Style Sheets) as an experimental feature.
You can load custom QSS files via View > Theme > Load Custom QSS.
The theme files are stored in the 'resources' directory with names based on what you provide.

Note: Custom QSS themes may conflict with the system color schemes and might not work perfectly with all styles.

## Styles
You can select different Qt styles from the Style dropdown in the toolbar.
The application uses the Fusion style by default, which provides a consistent look across platforms.

## Default Fusion Style
Select "Default Fusion Style" from the View > Theme menu to reset to the default Fusion style with Auto color scheme.
This is useful if you want to clear any custom themes and return to the default appearance.
"""
        self.settings_display.setMarkdown(settings_text)

        outline_sample_text = """# Story Outline

Use this space to structure your story.

- Chapter 1
  - Scene 1
  - Scene 2
- Chapter 2
  - Scene 1
"""
        self.outline_display.setMarkdown(
            outline_sample_text)  # Add sample text to outline
        self.chat_preview_display.append(
            "Chatbot: Hello! How can I help you today?\n")
        self.canon_display.setText(
            "# Story Canon\n\n*   Major Event 1: The Great Upheaval changed the course of history.\n*   Key Fact A: Magic is fading from the world.\n")
        self.world_setting_display.setText(
            "# World Setting Overview\n\n## Geography\nThe land of Eldoria is marked by towering mountains to the north and vast, sprawling plains to the south.\n\n## Culture\nEldorian society is strictly hierarchical, with mages at the top.\n\n## Magic System (if any)\nMagic is drawn from elemental spirits, but their power is waning.\n")
        self.character_profiles_display.setText(
            "# Character Profiles\n\n## Lyra Meadowlight\nName: Lyra Meadowlight\nRole: Protagonist, young mage apprentice\nMotivation: To find a cure for the fading magic.\n\n## Lord Kaelen\nName: Lord Kaelen\nRole: Antagonist, power-hungry sorcerer\nMotivation: To hoard the remaining magic for himself.\n")

        # Sample checklist items
        sample_tasks = ["Draft Chapter 1", "Develop Character X's backstory",
                        "Outline Act II plot points", "Worldbuild: Faction A details"]
        for task_text in sample_tasks:
            item = QListWidgetItem(task_text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.checklist_widget.addItem(item)
        if self.checklist_widget.count() > 0:  # Check the first item as an example
            self.checklist_widget.item(0).setCheckState(Qt.CheckState.Checked)

    @Slot()
    def _handle_add_checklist_item(self):
        """Adds an item to the checklist widget."""
        text = self.checklist_input_line.text().strip()
        if text:
            item = QListWidgetItem(text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.checklist_widget.addItem(item)
            self.checklist_input_line.clear()

    @Slot()
    def _handle_remove_checklist_item(self):
        """Removes selected items from the checklist widget."""
        selected_items = self.checklist_widget.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.checklist_widget.takeItem(self.checklist_widget.row(item))

    @Slot()
    def _handle_send_chat_message(self):
        """Handles sending a message from the chat input line."""
        text = self.chat_input_line.text().strip()
        if text:
            self.chat_preview_display.append(f"User: {text}\n")
            self.chat_input_line.clear()
            # Simulate bot response
            QTimer.singleShot(500, lambda: self.chat_preview_display.append(
                f"Bot: Acknowledged: '{text}'\n"))

    @Slot()
    def _handle_select_all(self):
        """Handles the Select All action from the Edit menu."""
        focused_widget = app.focusWidget()
        if isinstance(focused_widget, QTextEdit):
            focused_widget.selectAll()

    @Slot()
    def _handle_find(self):
        """Handles the Find action from the Edit menu."""
        search_term, ok = QInputDialog.getText(
            self, "Find Text", "Enter text to find:")
        if ok and search_term:
            self.current_search_term = search_term
            self._find_text_in_story_display(
                self.current_search_term, find_next=False)
        elif ok and not search_term:  # User entered blank search
            QMessageBox.information(
                self, "Find Text", "Search term cannot be empty.")

    @Slot()
    def _handle_find_next(self):
        """Handles the Find Next action from the Edit menu."""
        if not self.current_search_term:
            # If no current search term, invoke _handle_find to get one
            self._handle_find()
        else:
            # Use the new find method that supports options; assume default options for simple Find Next
            self.find_text_in_story_display_with_options(
                self.current_search_term, find_next=True)

    def find_text_in_story_display_with_options(self, search_term, find_next=False, case_sensitive=False, whole_words=False):
        """
        Finds text in self.story_display with options for case sensitivity and whole words.
        Returns True if found, False otherwise.
        """
        if not search_term:
            return False

        # PySide6 uses QTextDocument.FindFlags()
        find_flags = QTextDocument.FindFlag(0)
        if case_sensitive:
            find_flags |= QTextDocument.FindFlag.FindCaseSensitively
        if whole_words:
            find_flags |= QTextDocument.FindFlag.FindWholeWords

        if not find_next:
            cursor = self.story_display.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.story_display.setTextCursor(cursor)

        # Use the flags in the find operation
        # QTextEdit.find() in PySide6 takes flags directly.
        found = self.story_display.find(search_term, find_flags)

        if found:
            self.story_display.ensureCursorVisible()
            return True
        else:
            if find_next:  # Only show wrap-around for "Find Next" type operations
                reply = QMessageBox.question(self, "Find Text",
                                             f"'{search_term}' not found. Search from beginning?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    cursor = self.story_display.textCursor()
                    cursor.movePosition(QTextCursor.MoveOperation.Start)
                    self.story_display.setTextCursor(cursor)
                    if self.story_display.find(search_term, find_flags):
                        self.story_display.ensureCursorVisible()
                        return True
                    else:
                        QMessageBox.information(
                            self, "Find Text", f"'{search_term}' not found in document.")
                        return False
            else:  # This was an initial "Find" or "Find" from dialog
                QMessageBox.information(
                    self, "Find Text", f"'{search_term}' not found in document.")
            return False

    # Renamed the old _find_text_in_story_display to avoid conflicts if it was directly used by find_next
    # For simple find (Ctrl+F), we can call the new method with default flags.
    def _find_text_in_story_display(self, search_term, find_next=False):
        """Legacy simple find, now calls the new method with default options."""
        return self.find_text_in_story_display_with_options(search_term, find_next=find_next, case_sensitive=False, whole_words=False)

    @Slot()
    def _handle_replace_dialog(self):
        """Handles the Replace action from the Edit menu."""
        if self.replace_dialog is None:
            self.replace_dialog = ReplaceDialog(
                self)  # Pass MainWindow instance

        # Pre-fill find text from current search term or last used in dialog
        last_find_text = self.settings.value(
            "replaceDialog/findText", self.current_search_term)
        self.replace_dialog.find_edit.setText(last_find_text)  # type: ignore

        last_replace_text = self.settings.value(
            "replaceDialog/replaceText", "")
        self.replace_dialog.replace_edit.setText(
            last_replace_text)  # type: ignore

        case_checked = self.settings.value(
            "replaceDialog/caseSensitive", False, type=bool)
        self.replace_dialog.case_checkbox.setChecked(
            case_checked)  # type: ignore

        words_checked = self.settings.value(
            "replaceDialog/wholeWords", False, type=bool)
        self.replace_dialog.words_checkbox.setChecked(
            words_checked)  # type: ignore

        # Using exec() for modal dialog. Use show() for non-modal.
        if self.replace_dialog.exec():  # exec() returns QDialog.DialogCode.Accepted if Ok/Accept
            # Store settings if dialog was accepted (though actions are immediate)
            self.settings.setValue(
                "replaceDialog/findText", self.replace_dialog.find_edit.text())
            self.settings.setValue(
                "replaceDialog/replaceText", self.replace_dialog.replace_edit.text())
            self.settings.setValue(
                "replaceDialog/caseSensitive", self.replace_dialog.case_checkbox.isChecked())
            self.settings.setValue(
                "replaceDialog/wholeWords", self.replace_dialog.words_checkbox.isChecked())
        # else:
            # Dialog was cancelled or closed, settings are not saved from here, but during interaction.

    @Slot()
    def _handle_send(self):
        """Handles the send button click."""
        active_tab = self.input_tabs.currentWidget()
        if active_tab == self.input_tabs.widget(0):  # Narrative Input tab
            input_text = self.main_input.toPlainText()
            if input_text:
                self.story_display.append(
                    f"\n\n**Narrative Input:**\n{input_text}")
                self.main_input.clear()
                self.status_bar.showMessage("Narrative input sent", 3000)
        # System Prompt Input tab
        elif active_tab == self.input_tabs.widget(1):
            input_text = self.secondary_input.toPlainText()
            if input_text:
                self.story_display.append(
                    f"\n\n**System Prompt Input:**\n{input_text}")
                self.secondary_input.clear()
                self.status_bar.showMessage("System prompt input sent", 3000)

    @Slot(int)
    def _update_font_size(self, size: int):
        """Applies the selected font size to relevant text areas."""
        font = self.font()  # Get default app font
        font.setPointSize(size)

        widgets_to_update = [
            self.story_display,      # QTextEdit for main content display
            self.info_display,       # QTextEdit for info tab
            self.settings_display,   # QTextEdit for settings tab
            self.outline_display,    # QTextEdit for outline tab
            self.chat_preview_display,  # QTextEdit for chat preview
            self.canon_display,      # QTextEdit for Canon
            self.world_setting_display,  # QTextEdit for World Setting
            self.character_profiles_display,  # QTextEdit for Character Profiles
            self.checklist_widget,   # QListWidget for Checklist
            self.main_input,         # QTextEdit for main input
            self.secondary_input,    # QTextEdit for secondary input
            self.chat_input_line,    # QLineEdit for chat input
            self.checklist_input_line  # QLineEdit for checklist input
        ]

        for widget in widgets_to_update:
            widget.setFont(font)

        self.settings.setValue("fontSize", size)  # Save setting

    @Slot(bool)
    def _toggle_color_scheme(self, checked: bool):
        """Toggles between light and dark color schemes."""
        # app = QApplication.instance()

        # First set style for consistent look
        app.setStyle(QStyleFactory.create(STYLE_SELECTED_THEME))

        # Make sure the style selector shows the current style
        self.style_selector.setCurrentText(STYLE_SELECTED_THEME)

        # Clear any custom theme by emptying default_theme.qss
        with open(DEFAULT_THEME_PATH, 'w', encoding='utf-8') as file:
            file.write('')  # Write empty content

        # Reset stylesheet
        app.setStyleSheet('')

        if checked:  # Dark mode
            # Apply dark color scheme
            app.styleHints().setColorScheme(Qt.ColorScheme.Dark)
            scheme_index = 2  # Dark

            # Update settings and UI
            self.settings.setValue("colorScheme", scheme_index)
            self.theme_button.setText("Light Mode")
        else:  # Light mode
            # Apply light color scheme
            app.styleHints().setColorScheme(Qt.ColorScheme.Light)
            scheme_index = 1  # Light

            # Update settings and UI
            self.settings.setValue("colorScheme", scheme_index)
            self.theme_button.setText("Dark Mode")

        # Update color scheme action checkboxes
        for action in self.color_scheme_actions:
            action.setChecked(action.data() == scheme_index)

        # Uncheck theme actions since we're using color scheme
        for action in self.theme_actions:
            action.setChecked(False)

        # Update status bar
        scheme_name = COLOR_SCHEMES[scheme_index]
        self.status_bar.showMessage(
            f"{scheme_name} color scheme applied", 3000)

    def _apply_theme_from_file(self, theme_path: Path):
        """Applies a theme from a QSS file."""
        if not theme_path.exists():
            QMessageBox.warning(self, "Theme Error",
                                f"Theme file not found: {theme_path}")
            return False

        try:
            # Read the QSS file content
            with open(theme_path, 'r', encoding='utf-8') as file:
                qss = file.read()

            # Reset to style first
            # app = QApplication.instance()
            app.setStyle(QStyleFactory.create(STYLE_SELECTED_THEME))

            # Apply the stylesheet to the application instance
            app.setStyleSheet(qss)
            return True
        except Exception as e:
            QMessageBox.warning(self, "Theme Error",
                                f"Error applying theme: {str(e)}")
            return False

    @Slot(bool)
    def _on_theme_selected(self, checked: bool):
        """Handles theme selection from the menu."""
        action = self.sender()
        if not isinstance(action, QAction) or not checked:
            return

        theme_type = action.data()
        if theme_type:
            # Uncheck all other theme actions
            for other_action in self.theme_actions:
                if other_action != action:
                    other_action.setChecked(False)

            # Uncheck color scheme actions since we're using a custom theme
            for action in self.color_scheme_actions:
                action.setChecked(False)

            # Apply the selected theme directly
            # app = QApplication.instance()

            # First set style for consistent look
            app.setStyle(QStyleFactory.create(STYLE_SELECTED_THEME))

            # Apply the theme based on type
            if theme_type == "dark":
                # Apply dark theme via color scheme
                app.styleHints().setColorScheme(Qt.ColorScheme.Dark)
                self.theme_button.setText("Light Mode")
                self.theme_button.setChecked(True)
                self.settings.setValue("colorScheme", 2)  # Dark
            else:  # light theme
                # Apply light theme via color scheme
                app.styleHints().setColorScheme(Qt.ColorScheme.Light)
                self.theme_button.setText("Dark Mode")
                self.theme_button.setChecked(False)
                self.settings.setValue("colorScheme", 1)  # Light

    @Slot(str)
    def _on_style_changed(self, style_name: str):
        """Handles style selection from the dropdown."""
        try:
            # Apply the selected style
            # app = QApplication.instance()
            app.setStyle(QStyleFactory.create(style_name))

            # Update the global style theme
            global STYLE_SELECTED_THEME
            STYLE_SELECTED_THEME = style_name

            # Get current color scheme
            color_scheme = self.settings.value(
                "colorScheme", 0, type=int)  # 0 = Auto by default

            # Reapply the color scheme to ensure it works with the new style
            app.styleHints().setColorScheme(Qt.ColorScheme(color_scheme))

            self.status_bar.showMessage(f"{style_name} style applied", 3000)

        except Exception as e:
            QMessageBox.warning(self, "Style Error",
                                f"Error applying {style_name} style: {str(e)}")

    @Slot()
    def _apply_default_fusion_style(self):
        """Applies the default Fusion style without any QSS customization."""
        try:
            # Clear any custom theme setting
            self.settings.setValue("customTheme", "")

            # Reset to Fusion style without any stylesheet
            # app = QApplication.instance()
            app.setStyle(QStyleFactory.create(STYLE_SELECTED_THEME))
            app.setStyleSheet('')  # Clear any stylesheet

            # Update UI to reflect we're using default style
            self.status_bar.showMessage("Default Fusion style applied", 3000)

            # Uncheck theme actions since we're not using any custom theme
            for action in self.theme_actions:
                action.setChecked(False)

            # Make sure the style selector shows the current style
            self.style_selector.setCurrentText(STYLE_SELECTED_THEME)

            # Set Auto color scheme
            self._on_color_scheme_selected(True, force_index=0)

        except Exception as e:
            QMessageBox.warning(self, "Style Error",
                                f"Error applying default style: {str(e)}")

    @Slot(bool)
    def _on_color_scheme_selected(self, checked: bool, force_index=None):
        """Handles color scheme selection from the menu."""
        if not checked and force_index is None:
            return

        # Get the selected scheme index
        if force_index is not None:
            scheme_index = force_index
        else:
            action = self.sender()
            if not isinstance(action, QAction):
                return
            scheme_index = action.data()

        # Uncheck all other color scheme actions
        for action in self.color_scheme_actions:
            action.setChecked(action.data() == scheme_index)

        # Apply the selected color scheme
        # app = QApplication.instance()
        app.styleHints().setColorScheme(Qt.ColorScheme(scheme_index))

        # Reset stylesheet but keep the style
        app.setStyleSheet('')

        # Clear any custom theme setting
        self.settings.setValue("customTheme", "")

        # Update settings
        self.settings.setValue("colorScheme", scheme_index)

        # Update UI
        scheme_name = COLOR_SCHEMES[scheme_index]
        self.status_bar.showMessage(
            f"{scheme_name} color scheme applied", 3000)

        # Uncheck theme actions since we're using color scheme
        for action in self.theme_actions:
            action.setChecked(False)

        # Update theme button state based on color scheme
        if scheme_index == 2:  # Dark
            self.theme_button.setChecked(True)
            self.theme_button.setText("Light Mode")
        else:  # Light or Auto
            self.theme_button.setChecked(False)
            self.theme_button.setText("Dark Mode")

    @Slot()
    def _load_custom_qss(self):
        """Opens a file dialog to load a custom QSS file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Custom QSS Theme",
            str(RESOURCES_DIR),
            "QSS Files (*.qss);;All Files (*)"
        )

        if not file_path:
            return

        # Ask for a theme name
        theme_name, ok = QInputDialog.getText(
            self,
            "Theme Name",
            "Enter a name for this theme (e.g., 'Blue Accent'):"
        )

        if not ok or not theme_name:
            theme_name = "custom"

        # Create a sanitized filename
        safe_name = "".join(
            c if c.isalnum() or c in "_- " else "_" for c in theme_name).lower()
        safe_name = safe_name.replace(" ", "_")

        # Create the new theme file path
        new_theme_path = RESOURCES_DIR / f"{safe_name}_theme.qss"

        try:
            # Copy the selected QSS file to the new theme file
            shutil.copy(file_path, new_theme_path)

            # Also copy to default_theme.qss
            shutil.copy(file_path, DEFAULT_THEME_PATH)

            # Apply the theme
            success = self._apply_theme_from_file(new_theme_path)

            if success:
                # Store the custom theme name in settings
                self.settings.setValue("customTheme", safe_name)

                # Uncheck color scheme actions
                for action in self.color_scheme_actions:
                    action.setChecked(False)

                # Update UI
                self.status_bar.showMessage(
                    f"Custom theme '{theme_name}' applied", 3000)

                # Add to theme menu if it doesn't exist
                theme_exists = False
                for action in self.theme_actions:
                    if action.text() == theme_name:
                        action.setChecked(True)
                        theme_exists = True
                        break

                if not theme_exists:
                    # Create a new action for this theme
                    new_theme_action = QAction(theme_name, self)
                    new_theme_action.setCheckable(True)
                    new_theme_action.setData(safe_name)
                    new_theme_action.setChecked(True)
                    new_theme_action.triggered.connect(
                        self._on_custom_theme_selected)

                    # Add it to the theme menu before the separators
                    menu = self.theme_actions[0].parentWidget()
                    if menu:
                        menu.insertAction(
                            self.theme_actions[-1], new_theme_action)
                        self.theme_actions.append(new_theme_action)
        except Exception as e:
            QMessageBox.warning(self, "Theme Error",
                                f"Error loading custom theme: {str(e)}")

    @Slot(bool)
    def _on_custom_theme_selected(self, checked: bool):
        """Handles custom theme selection from the menu."""
        if not checked:
            return

        action = self.sender()
        if not isinstance(action, QAction):
            return

        theme_id = action.data()
        theme_path = RESOURCES_DIR / f"{theme_id}_theme.qss"

        if theme_path.exists():
            # Store the custom theme name in settings
            self.settings.setValue("customTheme", theme_id)

            # Apply the theme directly from the theme file
            self._apply_theme_from_file(theme_path)

            # Uncheck other theme actions
            for other_action in self.theme_actions:
                if other_action != action:
                    other_action.setChecked(False)

            # Uncheck color scheme actions
            for scheme_action in self.color_scheme_actions:
                scheme_action.setChecked(False)

            # Update UI
            self.status_bar.showMessage(
                f"Theme '{action.text()}' applied", 3000)
        else:
            QMessageBox.warning(self, "Theme Error",
                                f"Theme file not found: {theme_path}")
            action.setChecked(False)
            # Clear the custom theme setting
            self.settings.setValue("customTheme", "")

    def _create_buttons_group_box(self):
        """Creates a group box with various button types."""
        group_box = QGroupBox("Buttons")  # QGroupBox for buttons
        group_box.setObjectName("buttonsGroupBox")

        # Create buttons
        default_push_button = QPushButton(
            "Default Push Button")  # QPushButton for default
        default_push_button.setDefault(True)

        toggle_push_button = QPushButton(
            "Toggle Push Button")  # QPushButton for toggle
        toggle_push_button.setCheckable(True)
        toggle_push_button.setChecked(True)

        flat_push_button = QPushButton(
            "Flat Push Button")  # QPushButton for flat
        flat_push_button.setFlat(True)

        tool_button = QToolButton()  # QToolButton
        tool_button.setText("Tool Button")

        menu_tool_button = QToolButton()  # QToolButton for menu
        menu_tool_button.setText("Menu Button")
        tool_menu = QMenu(menu_tool_button)  # QMenu for tool button
        menu_tool_button.setPopupMode(
            QToolButton.ToolButtonPopupMode.InstantPopup)
        tool_menu.addAction("Option")
        tool_menu.addSeparator()
        action = tool_menu.addAction("Checkable Option")
        action.setCheckable(True)
        menu_tool_button.setMenu(tool_menu)

        tool_layout = QHBoxLayout()  # QHBoxLayout for tool buttons
        tool_layout.addWidget(tool_button)
        tool_layout.addWidget(menu_tool_button)

        command_link_button = QCommandLinkButton(
            "Command Link Button")  # QCommandLinkButton
        command_link_button.setDescription("Description")

        # Create radio buttons and checkbox
        radio_button1 = QRadioButton("Radio button 1")  # QRadioButton
        radio_button2 = QRadioButton("Radio button 2")  # QRadioButton
        radio_button3 = QRadioButton("Radio button 3")  # QRadioButton
        radio_button1.setChecked(True)

        check_box = QCheckBox("Tri-state check box")  # QCheckBox
        check_box.setTristate(True)
        check_box.setCheckState(Qt.CheckState.PartiallyChecked)

        # Layout for buttons
        button_layout = QVBoxLayout()  # QVBoxLayout for buttons
        button_layout.addWidget(default_push_button)
        button_layout.addWidget(toggle_push_button)
        button_layout.addWidget(flat_push_button)
        button_layout.addLayout(tool_layout)
        button_layout.addWidget(command_link_button)
        button_layout.addStretch(1)

        # Layout for checkable widgets
        checkable_layout = QVBoxLayout()  # QVBoxLayout for checkable widgets
        checkable_layout.addWidget(radio_button1)
        checkable_layout.addWidget(radio_button2)
        checkable_layout.addWidget(radio_button3)
        checkable_layout.addWidget(check_box)
        checkable_layout.addStretch(1)

        # Main layout
        main_layout = QHBoxLayout(group_box)  # QHBoxLayout for main layout
        main_layout.addLayout(button_layout)
        main_layout.addLayout(checkable_layout)
        main_layout.addStretch()

        return group_box

    def _create_input_widgets_group_box(self):
        """Creates a group box with various input widgets."""
        group_box = QGroupBox(
            "Simple Input Widgets")  # QGroupBox for input widgets
        group_box.setObjectName("inputWidgetsGroupBox")
        group_box.setCheckable(True)
        group_box.setChecked(True)

        # Create input widgets
        line_edit = QLineEdit("s3cRe7")  # QLineEdit
        line_edit.setClearButtonEnabled(True)
        line_edit.setEchoMode(QLineEdit.EchoMode.Password)

        spin_box = QSpinBox()  # QSpinBox
        spin_box.setValue(50)

        date_time_edit = QDateTimeEdit()  # QDateTimeEdit
        date_time_edit.setDateTime(QDateTime.currentDateTime())

        slider = QSlider()  # QSlider
        slider.setOrientation(Qt.Orientation.Horizontal)
        slider.setValue(40)

        scroll_bar = QScrollBar()  # QScrollBar
        scroll_bar.setOrientation(Qt.Orientation.Horizontal)
        scroll_bar.setValue(60)

        dial = QDial()  # QDial
        dial.setValue(30)
        dial.setNotchesVisible(True)

        # Layout
        layout = QGridLayout(group_box)  # QGridLayout for layout
        layout.addWidget(line_edit, 0, 0, 1, 2)
        layout.addWidget(spin_box, 1, 0, 1, 2)
        layout.addWidget(date_time_edit, 2, 0, 1, 2)
        layout.addWidget(slider, 3, 0)
        layout.addWidget(scroll_bar, 4, 0)
        layout.addWidget(dial, 3, 1, 2, 1)
        layout.setRowStretch(5, 1)

        return group_box

    def _create_progress_bar(self):
        """Creates a progress bar with a timer."""
        progress_bar = QProgressBar()  # QProgressBar
        progress_bar.setObjectName("progressBar")
        progress_bar.setRange(0, 10000)
        progress_bar.setValue(0)

        # Create timer to advance the progress bar
        timer = QTimer(self)  # QTimer
        timer.timeout.connect(self._advance_progress_bar)
        timer.start(100)

        return progress_bar

    @Slot()
    def _advance_progress_bar(self):
        """Advances the progress bar value."""
        current_value = self.progress_bar.value()
        max_value = self.progress_bar.maximum()
        self.progress_bar.setValue(
            current_value + (max_value - current_value) // 100)

    def _apply_current_theme(self):
        """Applies the current theme based on settings."""
        color_scheme = self.settings.value(
            "colorScheme", 0, type=int)  # 0 = Auto by default

        # Make sure the style selector shows the current style
        self.style_selector.setCurrentText(STYLE_SELECTED_THEME)

        # Apply color scheme
        # app = QApplication.instance()
        app.styleHints().setColorScheme(Qt.ColorScheme(color_scheme))

        # Clear any stylesheet by default
        app.setStyleSheet('')

        # Ensure default_theme.qss exists but is empty
        if not RESOURCES_DIR.exists():
            RESOURCES_DIR.mkdir(parents=True)

        with open(DEFAULT_THEME_PATH, 'w', encoding='utf-8') as file:
            file.write('')  # Write empty content

        # Update color scheme actions
        for action in self.color_scheme_actions:
            action.setChecked(action.data() == color_scheme)

        # Update theme button state based on color scheme
        if color_scheme == 2:  # Dark
            self.theme_button.setChecked(True)
            self.theme_button.setText("Light Mode")
        else:  # Light or Auto
            self.theme_button.setChecked(False)
            self.theme_button.setText("Dark Mode")

        # Check if we have a custom theme file to apply
        custom_theme = self.settings.value("customTheme", "", type=str)
        if custom_theme:
            theme_path = RESOURCES_DIR / f"{custom_theme}_theme.qss"
            if theme_path.exists():
                # Apply the custom theme
                self._apply_theme_from_file(theme_path)

                # Update theme actions
                for action in self.theme_actions:
                    action.setChecked(action.data() == custom_theme)

    def _load_settings(self):
        """Loads UI settings like theme and font size."""
        font_size = self.settings.value(
            "fontSize", DEFAULT_FONT_SIZE, type=int)
        if not isinstance(font_size, int):
            return
        self.font_size_spinbox.setValue(font_size)
        self._update_font_size(font_size)

    def closeEvent(self, event):
        """Handle window close event."""
        self.settings.setValue("geometry", self.saveGeometry())
        # Ensure replace dialog is closed if open and non-modal
        if self.replace_dialog and not self.replace_dialog.isModal():
            self.replace_dialog.close()
        event.accept()

# --- Replace Dialog Class ---


class ReplaceDialog(QDialog):
    def __init__(self, parent_main_window: MainWindow):
        super().__init__(parent_main_window)  # Set MainWindow as parent
        self.main_window = parent_main_window
        self.setWindowTitle("Find and Replace")

        # Widgets
        self.find_edit = QLineEdit()
        self.replace_edit = QLineEdit()
        self.case_checkbox = QCheckBox("Case sensitive")
        self.words_checkbox = QCheckBox("Whole words")

        self.find_next_button = QPushButton("Find Next")
        self.replace_button = QPushButton("Replace")
        self.replace_all_button = QPushButton("Replace All")
        self.cancel_button = QPushButton("Cancel")

        # Layout
        form_layout = QFormLayout()
        form_layout.addRow("Find what:", self.find_edit)
        form_layout.addRow("Replace with:", self.replace_edit)

        options_layout = QHBoxLayout()
        options_layout.addWidget(self.case_checkbox)
        options_layout.addWidget(self.words_checkbox)
        options_layout.addStretch()

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()  # Push buttons to the right
        buttons_layout.addWidget(self.find_next_button)
        buttons_layout.addWidget(self.replace_button)
        buttons_layout.addWidget(self.replace_all_button)
        buttons_layout.addWidget(self.cancel_button)

        main_dialog_layout = QVBoxLayout(self)
        main_dialog_layout.addLayout(form_layout)
        main_dialog_layout.addLayout(options_layout)
        main_dialog_layout.addLayout(buttons_layout)

        # Connections
        self.cancel_button.clicked.connect(
            self.reject)  # QDialog.reject() for cancel
        self.find_next_button.clicked.connect(self._on_find_next)
        self.replace_button.clicked.connect(self._on_replace)
        self.replace_all_button.clicked.connect(self._on_replace_all)

        # Set initial focus
        self.find_edit.setFocus()

    def _get_find_options(self):
        """Helper to get find text and options."""
        term = self.find_edit.text()
        case_sensitive = self.case_checkbox.isChecked()
        whole_words = self.words_checkbox.isChecked()
        return term, case_sensitive, whole_words

    @Slot()
    def _on_find_next(self):
        term, case_sensitive, whole_words = self._get_find_options()
        if not term:
            QMessageBox.information(
                self, "Find Next", "Please enter a search term.")
            return
        # Call MainWindow's find method
        self.main_window.find_text_in_story_display_with_options(
            term,
            find_next=True,
            case_sensitive=case_sensitive,
            whole_words=whole_words
        )
        # Store for next time dialog is opened (during this session)
        self.main_window.current_search_term = term

    @Slot()
    def _on_replace(self):
        find_term, case_sensitive, whole_words = self._get_find_options()
        replace_term = self.replace_edit.text()

        if not find_term:
            QMessageBox.information(
                self, "Replace", "Please enter a search term.")
            return

        story_display = self.main_window.story_display
        cursor = story_display.textCursor()

        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            # Check if the selected text matches the find_term with current options
            # This is an approximation. A perfect check would involve re-evaluating
            # "whole words" if that option is checked.
            # For now, string comparison with case sensitivity is the main check.

            current_selection_matches_find_term = False
            if case_sensitive:
                if selected_text == find_term:
                    current_selection_matches_find_term = True
            else:  # Case insensitive comparison
                if selected_text.lower() == find_term.lower():
                    current_selection_matches_find_term = True

            # More accurate check for whole words would be complex here without re-finding.
            # We assume if "whole words" is checked, the selection made by "Find Next" is a whole word.
            # So, if current_selection_matches_find_term is True, we proceed.

            if current_selection_matches_find_term:
                cursor.insertText(replace_term)  # Replace the selected text
                # After replacing, automatically find the next occurrence
                self.main_window.find_text_in_story_display_with_options(
                    find_term,
                    find_next=True,
                    case_sensitive=case_sensitive,
                    whole_words=whole_words
                )
                self.main_window.current_search_term = find_term  # Update main window's term
            else:
                # Selection doesn't match, or user selected something else.
                # Just do a "Find Next" to re-orient the user.
                self._on_find_next()
        else:
            # No selection, so just perform a "Find Next".
            # The user can then click "Replace" if this selection is what they want.
            self._on_find_next()

    @Slot()
    def _on_replace_all(self):
        find_term, case_sensitive, whole_words = self._get_find_options()
        replace_term = self.replace_edit.text()

        if not find_term:
            QMessageBox.information(
                self, "Replace All", "Please enter a search term.")
            return

        story_display = self.main_window.story_display
        cursor = story_display.textCursor()
        # Start from the beginning
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        story_display.setTextCursor(cursor)

        find_flags = QTextDocument.FindFlag(0)
        if case_sensitive:
            find_flags |= QTextDocument.FindFlag.FindCaseSensitively
        if whole_words:
            find_flags |= QTextDocument.FindFlag.FindWholeWords

        replacements_count = 0
        # find() selects the found text and moves cursor
        while story_display.find(find_term, find_flags):
            story_display.textCursor().insertText(replace_term)  # Replace current selection
            replacements_count += 1

        if replacements_count > 0:
            QMessageBox.information(
                self, "Replace All", f"Made {replacements_count} replacement(s).")
            # Store terms
            self.main_window.settings.setValue(
                "replaceDialog/findText", find_term)
            self.main_window.settings.setValue(
                "replaceDialog/replaceText", replace_term)
            self.main_window.settings.setValue(
                "replaceDialog/caseSensitive", case_sensitive)
            self.main_window.settings.setValue(
                "replaceDialog/wholeWords", whole_words)
        else:
            QMessageBox.information(
                self, "Replace All", f"'{find_term}' not found.")

    # Override accept to save settings if dialog is closed via "Enter" on a button etc.
    def accept(self):
        self.main_window.settings.setValue(
            "replaceDialog/findText", self.find_edit.text())
        self.main_window.settings.setValue(
            "replaceDialog/replaceText", self.replace_edit.text())
        self.main_window.settings.setValue(
            "replaceDialog/caseSensitive", self.case_checkbox.isChecked())
        self.main_window.settings.setValue(
            "replaceDialog/wholeWords", self.words_checkbox.isChecked())
        super().accept()

    def reject(self):  # Override reject to save settings as well (user might close dialog)
        self.main_window.settings.setValue(
            "replaceDialog/findText", self.find_edit.text())
        self.main_window.settings.setValue(
            "replaceDialog/replaceText", self.replace_edit.text())
        self.main_window.settings.setValue(
            "replaceDialog/caseSensitive", self.case_checkbox.isChecked())
        self.main_window.settings.setValue(
            "replaceDialog/wholeWords", self.words_checkbox.isChecked())
        super().reject()


# --- Main Execution ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName(SETTINGS_APP)
    app.setOrganizationName(SETTINGS_ORG)

    # Force style for more consistent look across platforms initially
    app.setStyle(QStyleFactory.create(STYLE_SELECTED_THEME))

    # Set color scheme to Auto by default
    # Auto/Unknown = system default
    app.styleHints().setColorScheme(Qt.ColorScheme.Unknown)

    # Create and show the main window
    window = MainWindow()

    # Restore window geometry
    geometry = window.settings.value("geometry")
    if geometry:
        window.restoreGeometry(geometry)
    else:
        window.resize(DEFAULT_WINDOW_SIZE)

    window.show()

    sys.exit(app.exec())
