"""Premium plugin loader."""
import os
import sys
from PySide6 import QtCore


def _check_pro_enabled():
    """Check if pro mode is enabled via CLI flag or global settings."""
    # Command line flag takes precedence
    if '--pro' in sys.argv:
        return True

    # Check global settings for license key and pro status
    try:
        settings = QtCore.QSettings("aicodeprep-gui", "ProLicense")
        pro_enabled = settings.value("pro_enabled", False, type=bool)
        if not pro_enabled:
            return False
        license_key = settings.value("license_key", "")
        license_verified = settings.value("license_verified", False, type=bool)
        return bool(pro_enabled and license_key and license_verified)
    except Exception as e:
        import logging
        logging.error(f"QSettings error in _check_pro_enabled: {e}")
        return False


# Check if pro mode is enabled
enabled = _check_pro_enabled()

# Preview window instance
_preview_window = None


def get_preview_window():
    """Get the global preview window instance."""
    global _preview_window
    if enabled and _preview_window is None:
        from .preview_window import FilePreviewDock
        _preview_window = FilePreviewDock()
    return _preview_window


def get_level_delegate(parent, is_dark_mode: bool = False):
    """
    Return (delegate_instance, LEVEL_ROLE) if pro is enabled; otherwise None.

    The delegate renders a multi-state 'Level' indicator in column 1.
    """
    if not enabled:
        return None
    try:
        from .multi_state_level_delegate import ComboBoxLevelDelegate, LEVEL_ROLE
        return ComboBoxLevelDelegate(parent, is_dark_mode=is_dark_mode), LEVEL_ROLE
    except Exception as e:
        # Descriptive error for later debugging per .clinerules
        import logging
        logging.error(f"Failed to load Pro Level delegate: {e}")
        return None
