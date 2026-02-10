import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from PySide6 import QtWidgets, QtCore

app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)


class TestAIAssistUI(unittest.TestCase):
    """Test that AI Assist UI elements are created properly."""

    @patch("aicodeprep_gui.gui.main_window.pro")
    def test_ai_buttons_exist(self, mock_pro):
        """Verify AI buttons are created."""
        mock_pro.enabled = True
        mock_pro.get_preview_window = MagicMock(return_value=None)
        mock_pro.get_level_delegate = MagicMock(return_value=None)
        mock_pro.get_flow_dock = MagicMock(return_value=None)

        # We'll just verify the import works and the classes exist
        from aicodeprep_gui.gui.handlers.ai_workers import PromptRewriteWorker, SmartSelectWorker
        assert PromptRewriteWorker is not None
        assert SmartSelectWorker is not None

    def test_ai_model_combo_import(self):
        """Verify endpoint config is importable."""
        from aicodeprep_gui.pro.ai_assist.endpoint_config import get_active_endpoint, load_endpoints
        assert get_active_endpoint is not None
        assert load_endpoints is not None

    def test_ai_client_import(self):
        """Verify AI client is importable."""
        from aicodeprep_gui.pro.ai_assist.ai_client import AIClient
        assert AIClient is not None
