import sys
from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QAction
from .flow.flow_dock import FlowStudioDock


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AICodePrep Flow Editor")
        self.setGeometry(100, 100, 1400, 900)

        # Instantiate FlowStudioDock and set it as the central widget.
        # Set read_only=False to ensure full editing capabilities.
        self.flow_studio = FlowStudioDock(parent=self, read_only=False)
        self.setCentralWidget(self.flow_studio)

        self._setup_menus()
        self.show()

    def _setup_menus(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")

        import_action = QAction("Import Flow...", self)
        import_action.triggered.connect(self.flow_studio._on_import_clicked)
        file_menu.addAction(import_action)

        export_action = QAction("Export Flow...", self)
        export_action.triggered.connect(self.flow_studio._on_export_clicked)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        help_menu = menu_bar.addMenu("&Help")
        help_action = QAction("Flow Studio Guide...", self)
        help_action.triggered.connect(self.flow_studio._show_help)
        help_menu.addAction(help_action)
