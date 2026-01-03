import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt

class RegMenuGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Main layout
        main_layout = QVBoxLayout()
        
        # Context Menu Section
        context_label = QLabel("Context Menu:")
        context_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(context_label)
        
        context_buttons = QHBoxLayout()
        self.add_context_btn = QPushButton("Add to Context Menu")
        self.remove_context_btn = QPushButton("Remove from Context Menu")
        context_buttons.addWidget(self.add_context_btn)
        context_buttons.addWidget(self.remove_context_btn)
        main_layout.addLayout(context_buttons)
        
        # Classic Menu Section
        classic_label = QLabel("Classic Right-Click Menu:")
        classic_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(classic_label)
        
        classic_buttons = QHBoxLayout()
        self.enable_classic_btn = QPushButton("Enable Classic Menu")
        self.disable_classic_btn = QPushButton("Disable Classic Menu")
        classic_buttons.addWidget(self.enable_classic_btn)
        classic_buttons.addWidget(self.disable_classic_btn)
        main_layout.addLayout(classic_buttons)
        
        # Status Section
        self.status_label = QLabel("Status: Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Connect buttons
        self.add_context_btn.clicked.connect(self.add_context)
        self.remove_context_btn.clicked.connect(self.remove_context)
        self.enable_classic_btn.clicked.connect(self.enable_classic)
        self.disable_classic_btn.clicked.connect(self.disable_classic)
        
        # Window settings
        self.setLayout(main_layout)
        self.setWindowTitle("AI Code Prep GUI - Menu Manager")
        self.setFixedSize(400, 250)
        
    def run_command(self, args):
        """Run command in new cmd window that stays open"""
        try:
            # Create command string
            command = f'cmd /k "python aicodeprep_gui_c/regmenu-win.py {args}"'
            subprocess.Popen(command, shell=True)
            self.status_label.setText(f"Status: Executed {args}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to execute command: {str(e)}")
            self.status_label.setText("Status: Error")
        
    def add_context(self):
        self.run_command("--add-context")
        
    def remove_context(self):
        self.run_command("--remove-context")
        
    def enable_classic(self):
        self.run_command("--enable-classic")
        
    def disable_classic(self):
        self.run_command("--disable-classic")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegMenuGUI()
    window.show()
    sys.exit(app.exec_())
