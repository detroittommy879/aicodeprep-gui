from .main_window import FileSelectionGUI
from .handlers.update_events import UpdateCheckWorker

import PySide6.QtWidgets as QtWidgets

def show_file_selection_gui(files):
    from .main_window import FileSelectionGUI
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    gui = FileSelectionGUI(files)
    gui.show()
    app.exec()
    return gui.action, gui.get_selected_files()

__all__ = ['FileSelectionGUI', 'show_file_selection_gui', 'UpdateCheckWorker']
