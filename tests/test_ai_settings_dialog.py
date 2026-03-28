import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from PySide6 import QtWidgets, QtCore
import toml
from pathlib import Path

# Ensure app exists
app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)


class TestAISettingsDialog(unittest.TestCase):

    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.load_endpoints")
    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.get_all_endpoint_ids")
    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.get_active_endpoint")
    def test_ai_settings_dialog_opens(self, mock_active, mock_ids, mock_load):
        """Dialog can be instantiated and shows endpoint list."""
        mock_load.return_value = {
            "active_endpoint": "local",
            "endpoints": {
                "local": {
                    "name": "zoobies coding plan",
                    "url": "https://extra.wuu73.org/aimodels/v1",
                    "api_key": "",
                    "selected_model": ""
                }
            }
        }
        mock_ids.return_value = ["local"]
        mock_active.return_value = {
            "id": "local", "name": "zoobies coding plan", "url": "...", "api_key": ""}

        from aicodeprep_gui.gui.components.ai_settings_dialog import AIEndpointSettingsDialog
        dialog = AIEndpointSettingsDialog()
        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.endpoint_list.count(), 1)
        dialog.close()

    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.load_endpoints")
    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.get_all_endpoint_ids")
    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.add_endpoint")
    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.get_active_endpoint")
    def test_ai_settings_add_endpoint(self, mock_active, mock_add, mock_ids, mock_load):
        """Can add a new endpoint."""
        mock_load.return_value = {
            "active_endpoint": "local",
            "endpoints": {
                "local": {"name": "Local", "url": "https://extra.wuu73.org/aimodels/v1", "api_key": "", "selected_model": ""}
            }
        }
        mock_ids.return_value = ["local"]
        mock_active.return_value = {"id": "local", "name": "Local"}

        from aicodeprep_gui.gui.components.ai_settings_dialog import AIEndpointSettingsDialog
        dialog = AIEndpointSettingsDialog()

        # Verify method exists
        self.assertTrue(hasattr(dialog, '_on_add_endpoint'))
        dialog.close()

    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.load_endpoints")
    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.get_all_endpoint_ids")
    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.get_active_endpoint")
    def test_ai_settings_has_required_widgets(self, mock_active, mock_ids, mock_load):
        """Dialog has all required widgets."""
        mock_load.return_value = {
            "active_endpoint": "local",
            "endpoints": {
                "local": {"name": "Local", "url": "https://extra.wuu73.org/aimodels/v1", "api_key": "", "selected_model": ""}
            }
        }
        mock_ids.return_value = ["local"]
        mock_active.return_value = {"id": "local"}

        from aicodeprep_gui.gui.components.ai_settings_dialog import AIEndpointSettingsDialog
        dialog = AIEndpointSettingsDialog()

        self.assertTrue(hasattr(dialog, 'endpoint_list'))
        self.assertTrue(hasattr(dialog, 'name_edit'))
        self.assertTrue(hasattr(dialog, 'url_edit'))
        self.assertTrue(hasattr(dialog, 'key_edit'))
        self.assertTrue(hasattr(dialog, 'test_btn'))
        self.assertTrue(hasattr(dialog, 'status_label'))
        self.assertTrue(hasattr(dialog, 'models_combo'))
        self.assertTrue(hasattr(dialog, 'refresh_btn'))
        dialog.close()

    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.AIClient")
    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.load_endpoints")
    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.get_all_endpoint_ids")
    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.get_active_endpoint")
    def test_refresh_models(self, mock_active, mock_ids, mock_load, mock_client_cls):
        """Test refreshing models populates the combo."""
        mock_load.return_value = {
            "active_endpoint": "local",
            "endpoints": {
                "local": {"name": "Local", "url": "https://extra.wuu73.org/aimodels/v1", "api_key": "", "selected_model": ""}
            }
        }
        mock_ids.return_value = ["local"]
        mock_active.return_value = {"id": "local"}

        # Mock client behavior
        mock_client = mock_client_cls.return_value
        mock_client.list_models.return_value = [
            {"id": "gpt-4"}, {"id": "claude-3"}]

        from aicodeprep_gui.gui.components.ai_settings_dialog import AIEndpointSettingsDialog
        dialog = AIEndpointSettingsDialog()

        # Call refresh
        # We need to ensure right side is populated for "local"
        # Select the item
        dialog.endpoint_list.setCurrentRow(0)

        dialog._on_refresh_models()

        mock_client.list_models.assert_called()
        self.assertEqual(dialog.models_combo.count(), 2)
        self.assertEqual(dialog.models_combo.itemText(0), "gpt-4")
        dialog.close()

    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.save_endpoints")
    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.load_endpoints")
    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.get_all_endpoint_ids")
    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.get_active_endpoint")
    def test_edit_url_persists_on_save(self, mock_active, mock_ids, mock_load, mock_save):
        """Regression: editing the URL field must be saved to config_data and disk."""
        mock_load.return_value = {
            "active_endpoint": "local",
            "endpoints": {
                "local": {
                    "name": "zoobies coding plan",
                    "url": "https://extra.wuu73.org/aimodels/v1",
                    "api_key": "",
                    "selected_model": ""
                }
            }
        }
        mock_ids.return_value = ["local"]
        mock_active.return_value = {"id": "local"}

        from aicodeprep_gui.gui.components.ai_settings_dialog import AIEndpointSettingsDialog
        dialog = AIEndpointSettingsDialog()

        # After init, current_endpoint_id must be set (this was the root cause)
        self.assertIsNotNone(dialog.current_endpoint_id,
                             "current_endpoint_id must be set after _refresh_list")
        self.assertEqual(dialog.current_endpoint_id, "local")

        # Verify form shows the original URL
        self.assertEqual(dialog.url_edit.text(),
                         "https://extra.wuu73.org/aimodels/v1")

        # Simulate user editing the URL (textEdited signal is emitted by clear+type)
        dialog.url_edit.clear()
        # textEdited is NOT emitted by setText/clear, so simulate the signal
        dialog.url_edit.setText("http://localhost:12345/v1")
        # Manually fire the signal since setText doesn't emit textEdited
        dialog._marked_changed()

        # Verify the in-memory config was updated
        self.assertEqual(
            dialog.config_data["endpoints"]["local"]["url"],
            "http://localhost:12345/v1"
        )

        # Now simulate clicking Save & Close
        dialog._on_save()

        # Verify save_endpoints was called with the updated URL
        mock_save.assert_called_once()
        saved_data = mock_save.call_args[0][0]
        self.assertEqual(
            saved_data["endpoints"]["local"]["url"],
            "http://localhost:12345/v1",
            "URL change must persist through save"
        )
        dialog.close()

    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.save_endpoints")
    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.load_endpoints")
    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.get_all_endpoint_ids")
    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.get_active_endpoint")
    def test_edit_port_not_reverted_by_test_connection(self, mock_active, mock_ids, mock_load, mock_save):
        """Regression: editing URL then clicking Test Connection must NOT revert the edit."""
        mock_load.return_value = {
            "active_endpoint": "local",
            "endpoints": {
                "local": {
                    "name": "zoobies coding plan",
                    "url": "https://extra.wuu73.org/aimodels/v1",
                    "api_key": "",
                    "selected_model": ""
                }
            }
        }
        mock_ids.return_value = ["local"]
        mock_active.return_value = {"id": "local"}

        from aicodeprep_gui.gui.components.ai_settings_dialog import AIEndpointSettingsDialog
        dialog = AIEndpointSettingsDialog()

        # Edit URL
        dialog.url_edit.setText("http://localhost:7777/v1")
        dialog._marked_changed()  # simulate textEdited signal

        # Verify edit is in memory
        self.assertEqual(
            dialog.config_data["endpoints"]["local"]["url"],
            "http://localhost:7777/v1"
        )

        # Simulate test connection (will fail since no server, but should not revert URL)
        with patch("aicodeprep_gui.gui.components.ai_settings_dialog.AIClient") as mock_client_cls:
            mock_client_cls.return_value.list_models.side_effect = Exception(
                "no server")
            dialog._on_test_connection()

        # URL in form and config must still be the edited value
        self.assertEqual(dialog.url_edit.text(), "http://localhost:7777/v1",
                         "URL in form must not revert after Test Connection")
        self.assertEqual(
            dialog.config_data["endpoints"]["local"]["url"],
            "http://localhost:7777/v1",
            "URL in config_data must not revert after Test Connection"
        )
        dialog.close()

    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.load_endpoints")
    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.get_all_endpoint_ids")
    @patch("aicodeprep_gui.gui.components.ai_settings_dialog.get_active_endpoint")
    def test_name_edit_updates_endpoint_list_label(self, mock_active, mock_ids, mock_load):
        mock_load.return_value = {
            "active_endpoint": "local",
            "endpoints": {
                "local": {
                    "name": "Original Name",
                    "url": "https://example.com/v1",
                    "api_key": "",
                    "selected_model": ""
                }
            }
        }
        mock_ids.return_value = ["local"]
        mock_active.return_value = {"id": "local"}

        from aicodeprep_gui.gui.components.ai_settings_dialog import AIEndpointSettingsDialog
        dialog = AIEndpointSettingsDialog()

        dialog.endpoint_list.setCurrentRow(0)
        dialog.name_edit.setText("Updated Name")
        dialog._marked_changed()

        self.assertEqual(dialog.endpoint_list.item(0).text(), "► Updated Name")
        dialog.close()

    @patch("aicodeprep_gui.pro.ai_assist.endpoint_config.get_config_dir")
    def test_save_persists_real_files_when_cached_endpoint_id_is_stale(self, mock_config_dir):
        temp_dir = Path(tempfile.mkdtemp(prefix="aicp-endpoints-test-"))
        self.addCleanup(lambda: __import__(
            "shutil").rmtree(temp_dir, ignore_errors=True))
        mock_config_dir.return_value = temp_dir

        from aicodeprep_gui.gui.components.ai_settings_dialog import AIEndpointSettingsDialog

        dialog = AIEndpointSettingsDialog()
        dialog.endpoint_list.setCurrentRow(0)

        dialog.url_edit.setText("http://localhost:4321/v1")
        dialog.key_edit.setText("real-test-key")
        dialog.models_combo.setEditText("test-model")

        # Simulate the stale cached id case seen in the live regression.
        dialog.current_endpoint_id = None
        dialog._on_save()

        with open(temp_dir / "ai-endpoints.toml", "r", encoding="utf-8") as handle:
            endpoints_data = toml.load(handle)
        with open(temp_dir / "api-keys.toml", "r", encoding="utf-8") as handle:
            api_keys_data = toml.load(handle)

        self.assertEqual(
            endpoints_data["endpoints"]["local"]["url"],
            "http://localhost:4321/v1",
        )
        self.assertEqual(
            endpoints_data["endpoints"]["local"]["api_key"],
            "real-test-key",
        )
        self.assertEqual(
            endpoints_data["endpoints"]["local"]["selected_model"],
            "test-model",
        )
        self.assertEqual(
            api_keys_data["custom"]["base_url"],
            "http://localhost:4321/v1",
        )
        self.assertEqual(
            api_keys_data["custom"]["api_key"],
            "real-test-key",
        )
        self.assertEqual(
            api_keys_data["custom"]["selected_model"],
            "test-model",
        )
        dialog.close()
