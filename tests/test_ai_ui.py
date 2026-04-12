import os
import sys
from types import SimpleNamespace
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

    def test_generate_ai_button_sync_follows_ai_chat_toggle(self):
        """The Generate Context to AI button should reflect restored AI chat state."""
        from aicodeprep_gui.gui.main_window import FileSelectionGUI

        generate_ai_button = QtWidgets.QPushButton()
        generate_ai_button.setEnabled(False)

        ai_chat_toggle = QtWidgets.QCheckBox()
        ai_chat_toggle.setEnabled(True)
        ai_chat_toggle.setChecked(True)

        window = SimpleNamespace(
            generate_ai_button=generate_ai_button,
            ai_chat_toggle=ai_chat_toggle,
        )

        FileSelectionGUI._sync_generate_ai_button_state(window)
        self.assertTrue(generate_ai_button.isEnabled())

        ai_chat_toggle.setChecked(False)
        FileSelectionGUI._sync_generate_ai_button_state(window)
        self.assertFalse(generate_ai_button.isEnabled())

    @patch("aicodeprep_gui.gui.main_window.get_remote_access_state")
    def test_remote_notice_popup_excludes_free_for_all_copy(self, mock_get_remote_access_state):
        """The free-for-all remote notice should no longer produce a startup popup."""
        from aicodeprep_gui.gui.main_window import FileSelectionGUI

        mock_get_remote_access_state.return_value = {
            "free_for_all": True,
            "announcement_message": "",
        }

        popup_text, _banner_text = FileSelectionGUI._build_remote_pro_notice_texts(
            SimpleNamespace()
        )

        self.assertEqual(popup_text, "")

    @patch("aicodeprep_gui.gui.main_window.should_show_remote_pro_notice")
    @patch("aicodeprep_gui.gui.main_window.get_remote_access_state")
    def test_remote_notice_popup_shows_only_for_non_pro_users(self, mock_get_remote_access_state, mock_should_show_remote_pro_notice):
        """Free-user-only remote announcement copy should only surface for users who are not currently Pro-enabled."""
        from aicodeprep_gui.gui.main_window import FileSelectionGUI

        mock_get_remote_access_state.return_value = {
            "free_for_all": False,
            "announcement_message": "",
            "free_user_announcement_message": "Limited-time discount",
        }

        mock_should_show_remote_pro_notice.return_value = False
        popup_text, _banner_text = FileSelectionGUI._build_remote_pro_notice_texts(
            SimpleNamespace()
        )
        self.assertEqual(popup_text, "")

        mock_should_show_remote_pro_notice.return_value = True
        popup_text, _banner_text = FileSelectionGUI._build_remote_pro_notice_texts(
            SimpleNamespace()
        )
        self.assertEqual(popup_text, "Limited-time discount")

    @patch("aicodeprep_gui.gui.main_window.should_show_remote_pro_notice")
    @patch("aicodeprep_gui.gui.main_window.get_remote_access_state")
    def test_remote_notice_popup_shows_general_message_to_all_users(self, mock_get_remote_access_state, mock_should_show_remote_pro_notice):
        """General remote announcement copy should still be available for all users."""
        from aicodeprep_gui.gui.main_window import FileSelectionGUI

        mock_get_remote_access_state.return_value = {
            "free_for_all": False,
            "announcement_message": "General announcement",
            "free_user_announcement_message": "",
        }

        mock_should_show_remote_pro_notice.return_value = False
        popup_text, _banner_text = FileSelectionGUI._build_remote_pro_notice_texts(
            SimpleNamespace()
        )
        self.assertEqual(popup_text, "General announcement")
