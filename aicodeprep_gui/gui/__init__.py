from .main_window import FileSelectionGUI
from .handlers.update_events import UpdateCheckWorker

import PySide6.QtWidgets as QtWidgets


def show_file_selection_gui(files, project_root=None, initial_tree_fully_loaded=True):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    gui = FileSelectionGUI(
        files,
        project_root=project_root,
        initial_tree_fully_loaded=initial_tree_fully_loaded,
    )
    gui.show()
    app.exec()
    return gui.action, gui.get_selected_files()


__all__ = ['FileSelectionGUI', 'show_file_selection_gui', 'UpdateCheckWorker']
