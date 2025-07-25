from PySide6 import QtCore, QtGui, QtWidgets
import platform
import os
import sys
import ctypes
import json
import logging
from importlib import resources

def system_pref_is_dark() -> bool:
    """Detect if system is using dark mode."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        try:
            import subprocess
            cmd = "defaults read -g AppleInterfaceStyle"
            result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
            return result.stdout.strip() == "Dark"
        except:
            pass
    
    elif system == "Windows":  # Windows 10+
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            reg_keypath = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            key = winreg.OpenKey(registry, reg_keypath)
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        except:
            pass
    
    # Fallback: use palette heuristic
    return QtWidgets.QApplication.palette().color(QtGui.QPalette.Window).lightness() < 128

def apply_dark_palette(app: QtWidgets.QApplication):
    """Apply dark color palette to application."""
    dark = QtGui.QPalette()
    dark.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    dark.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 255, 255))
    dark.setColor(QtGui.QPalette.Base, QtGui.QColor(42, 42, 42))
    dark.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(66, 66, 66))
    dark.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(53, 53, 53))
    dark.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(255, 255, 255))
    dark.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 255, 255))
    dark.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    dark.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(255, 255, 255))
    dark.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    dark.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    dark.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
    
    # Disabled colors
    dark.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtGui.QColor(128, 128, 128))
    dark.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtGui.QColor(128, 128, 128))
    dark.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, QtGui.QColor(128, 128, 128))
    
    app.setPalette(dark)

def apply_light_palette(app: QtWidgets.QApplication):
    """Apply light color palette to application."""
    light = QtGui.QPalette()
    light.setColor(QtGui.QPalette.Window, QtGui.QColor(240, 240, 240))
    light.setColor(QtGui.QPalette.WindowText, QtGui.QColor(0, 0, 0))
    light.setColor(QtGui.QPalette.Base, QtGui.QColor(255, 255, 255))
    light.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(233, 233, 233))
    light.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(255, 255, 255))
    light.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(0, 0, 0))
    light.setColor(QtGui.QPalette.Text, QtGui.QColor(0, 0, 0))
    light.setColor(QtGui.QPalette.Button, QtGui.QColor(240, 240, 240))
    light.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(0, 0, 0))
    light.setColor(QtGui.QPalette.Link, QtGui.QColor(0, 0, 255))
    light.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    light.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
    
    # Disabled colors
    light.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtGui.QColor(120, 120, 120))
    light.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtGui.QColor(120, 120, 120))
    light.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, QtGui.QColor(120, 120, 120))
    
    app.setPalette(light)

def create_checkmark_pixmap(size=16, color="#0078D4"):
    """Create a checkmark pixmap programmatically."""
    pixmap = QtGui.QPixmap(size, size)
    pixmap.fill(QtCore.Qt.transparent)
    
    painter = QtGui.QPainter(pixmap)
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    
    pen = QtGui.QPen(QtGui.QColor(color))
    pen.setWidth(2)
    pen.setCapStyle(QtCore.Qt.RoundCap)
    pen.setJoinStyle(QtCore.Qt.RoundJoin)
    painter.setPen(pen)
    
    # Draw checkmark
    painter.drawLine(4, 8, 7, 11)
    painter.drawLine(7, 11, 12, 4)
    
    painter.end()
    return pixmap

def create_x_mark_pixmap(size=16, color="#0078D4"):
    """Create an X mark pixmap programmatically (alternative to checkmark)."""
    pixmap = QtGui.QPixmap(size, size)
    pixmap.fill(QtCore.Qt.transparent)
    
    painter = QtGui.QPainter(pixmap)
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    
    pen = QtGui.QPen(QtGui.QColor(color))
    pen.setWidth(2)
    pen.setCapStyle(QtCore.Qt.RoundCap)
    painter.setPen(pen)
    
    # Draw X mark
    margin = 3
    painter.drawLine(margin, margin, size-margin, size-margin)
    painter.drawLine(margin, size-margin, size-margin, margin)
    
    painter.end()
    return pixmap

def create_arrow_pixmap(direction: str, size: int = 16, color: str = "#000000") -> QtGui.QPixmap:
    """Creates a triangular arrow pixmap, perfect for collapsible sections."""
    pixmap = QtGui.QPixmap(size, size)
    pixmap.fill(QtCore.Qt.transparent)
    
    painter = QtGui.QPainter(pixmap)
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    
    painter.setPen(QtCore.Qt.NoPen)
    painter.setBrush(QtGui.QColor(color))
    
    if direction == 'down':
        # Down-pointing triangle
        points = [
            QtCore.QPoint(int(size * 0.25), int(size * 0.3)),
            QtCore.QPoint(int(size * 0.75), int(size * 0.3)),
            QtCore.QPoint(int(size * 0.5), int(size * 0.7))
        ]
    else:  # 'right'
        # Right-pointing triangle
        points = [
            QtCore.QPoint(int(size * 0.3), int(size * 0.25)),
            QtCore.QPoint(int(size * 0.7), int(size * 0.5)),
            QtCore.QPoint(int(size * 0.3), int(size * 0.75))
        ]
        
    painter.drawPolygon(QtGui.QPolygon(points))
    painter.end()
    return pixmap

def get_groupbox_style(arrow_down_path: str, arrow_right_path: str, dark: bool) -> str:
    """Generates QSS for a collapsible QGroupBox with custom arrow indicators."""
    border_color = "#555555" if dark else "#AAAAAA"
    title_color = "#FFFFFF" if dark else "#000000"
    
    # Convert Windows paths to what QSS expects (forward slashes)
    if os.name == 'nt':
        arrow_down_url = arrow_down_path.replace('\\', '/')
        arrow_right_url = arrow_right_path.replace('\\', '/')
    else:
        arrow_down_url = arrow_down_path
        arrow_right_url = arrow_right_path

    return f"""
        QGroupBox {{
            border: 1px solid {border_color};
            border-radius: 5px;
            margin-top: 1em; /* Provides space for the title to be drawn on top of the border */
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding-left: 22px; /* Make space for the indicator */
            padding-right: 5px;
            color: {title_color};
        }}
        QGroupBox::indicator {{
            width: 16px;
            height: 16px;
            /* Position the indicator to the left of the title */
            position: absolute;
            top: 0.1em;
            left: 5px;
        }}
        QGroupBox::indicator:unchecked {{
            image: url('{arrow_right_url}');
        }}
        QGroupBox::indicator:checked {{
            image: url('{arrow_down_url}');
        }}
    """

def _checkbox_style_with_images(dark: bool) -> str:
    """Use SVG-based checkboxes - same as _checkbox_style but with descriptive name."""
    return _checkbox_style(dark)

def _checkbox_style(dark: bool) -> str:
    """Return checkbox styling using packaged image files."""
    
    # Use appropriate images for theme
    if dark:
        unchecked_filename = "checkbox_unchecked_dark.png"
        checked_filename = "checkbox_checked_dark.png"
    else:
        unchecked_filename = "checkbox_unchecked.png"
        checked_filename = "checkbox_checked.png"
    
    # --- THIS IS THE NEW, PACKAGE-SAFE WAY TO FIND FILES ---
    try:
        # 'aicodeprep_gui.images' corresponds to the aicodeprep_gui/images folder
        with resources.as_file(resources.files('aicodeprep_gui.images').joinpath(unchecked_filename)) as p:
            unchecked_path = str(p)
        with resources.as_file(resources.files('aicodeprep_gui.images').joinpath(checked_filename)) as p:
            checked_path = str(p)
    except Exception as e:
        # Fallback or error logging if resources can't be found
        logging.error(f"Could not load checkbox images: {e}")
        return "" # Return empty style if images fail to load
    # --- END OF THE NEW SECTION ---

    # The rest of the function is the same as before
    # Convert Windows paths to proper URLs for Qt
    if os.name == 'nt':  # Windows
        unchecked_url = unchecked_path.replace('\\', '/')
        checked_url = checked_path.replace('\\', '/')
    else:
        unchecked_url = unchecked_path
        checked_url = checked_path
    
    hover_border_color = "#00c3ff"
    
    return f"""
    QTreeView::indicator, QTreeWidget::indicator {{
        width: 16px;
        height: 16px;
        border: none;
        background: transparent;
        image: url({unchecked_url});
    }}
    
    QTreeView::indicator:checked, QTreeWidget::indicator:checked {{
        image: url({checked_url});
    }}
    
    QTreeView::indicator:hover, QTreeWidget::indicator:hover {{
        border: 1px solid {hover_border_color};
        border-radius: 2px;
    }}
    
    QTreeView::indicator:checked:hover, QTreeWidget::indicator:checked:hover {{
        border: 1px solid {hover_border_color};
        border-radius: 2px;
        image: url({checked_url});
    }}
    """

def get_checkbox_style_dark()  -> str: 
    return _checkbox_style(True)

def get_checkbox_style_light() -> str: 
    return _checkbox_style(False)
