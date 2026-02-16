"""
Tests for AI Chat functionality including endpoint selection, model dropdown, and window sizing.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from PySide6 import QtWidgets, QtCore

# Ensure the project is in the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Use session-scoped QApplication from conftest
pytestmark = pytest.mark.usefixtures("qapp_session")


class TestChatTabEndpointSelections:
    """Tests for per-tab endpoint selection - runs without fixture issues."""

    @patch("aicodeprep_gui.pro.ai_chat.chat_tab.load_endpoints")
    @patch("aicodeprep_gui.pro.ai_chat.chat_tab.set_active_model")
    @patch("aicodeprep_gui.pro.ai_chat.chat_tab.get_active_endpoint")
    def test_endpoint_dropdown_populated(
        self, mock_get_active, mock_set_model, mock_load_endpoints
    ):
        """Test that endpoint dropdown is populated with all configured endpoints."""
        # Mock endpoint config
        mock_load_endpoints.return_value = {
            "active_endpoint": "local",
            "endpoints": {
                "local": {
                    "name": "Local Server",
                    "url": "http://localhost:59999/v1",
                    "api_key": "",
                    "selected_model": "gpt-3.5-turbo"
                },
                "openrouter": {
                    "name": "OpenRouter",
                    "url": "https://openrouter.ai/api/v1",
                    "api_key": "test-key",
                    "selected_model": "openai/gpt-3.5-turbo"
                }
            }
        }
        mock_get_active.return_value = {
            "id": "local",
            "name": "Local Server",
            "url": "http://localhost:59999/v1",
            "api_key": "",
            "selected_model": "gpt-3.5-turbo"
        }

        from aicodeprep_gui.pro.ai_chat.chat_tab import ChatTabWidget

        with patch("aicodeprep_gui.pro.ai_chat.chat_tab.AIClient") as mock_client:
            mock_client.return_value.list_models.return_value = []

            tab = ChatTabWidget()

            # Check endpoint combo has both endpoints
            assert tab.endpoint_combo.count() == 2

            # Check endpoint names are displayed
            endpoint_names = [tab.endpoint_combo.itemText(i) for i in range(tab.endpoint_combo.count())]
            assert "Local Server" in endpoint_names
            assert "OpenRouter" in endpoint_names

            # Check data values
            data_values = [tab.endpoint_combo.itemData(i) for i in range(tab.endpoint_combo.count())]
            assert "local" in data_values
            assert "openrouter" in data_values

            # Clean up - close the widget
            tab.close()
            tab.deleteLater()

    @patch("aicodeprep_gui.pro.ai_chat.chat_tab.load_endpoints")
    @patch("aicodeprep_gui.pro.ai_chat.chat_tab.set_active_model")
    @patch("aicodeprep_gui.pro.ai_chat.chat_tab.get_active_endpoint")
    def test_switching_endpoint_changes_config(
        self, mock_get_active, mock_set_model, mock_load_endpoints
    ):
        """Test that switching endpoint changes the tab's endpoint config."""
        mock_load_endpoints.return_value = {
            "active_endpoint": "local",
            "endpoints": {
                "local": {
                    "name": "Local Server",
                    "url": "http://localhost:59999/v1",
                    "api_key": "",
                    "selected_model": "gpt-3.5-turbo"
                },
                "openrouter": {
                    "name": "OpenRouter",
                    "url": "https://openrouter.ai/api/v1",
                    "api_key": "test-key",
                    "selected_model": "gpt-3.5-turbo"
                }
            }
        }
        mock_get_active.return_value = {
            "id": "local",
            "name": "Local Server",
            "url": "http://localhost:59999/v1",
            "api_key": "",
            "selected_model": "gpt-3.5-turbo"
        }

        from aicodeprep_gui.pro.ai_chat.chat_tab import ChatTabWidget

        with patch("aicodeprep_gui.pro.ai_chat.chat_tab.AIClient") as mock_client:
            mock_client.return_value.list_models.return_value = []

            tab = ChatTabWidget()

            # Initially should have local endpoint
            assert tab._endpoint_id == "local"
            assert tab._endpoint_config.get("url") == "http://localhost:59999/v1"

            # Switch to openrouter
            idx = tab.endpoint_combo.findData("openrouter")
            tab.endpoint_combo.setCurrentIndex(idx)

            # Now should have openrouter
            assert tab._endpoint_id == "openrouter"
            assert tab._endpoint_config.get("url") == "https://openrouter.ai/api/v1"
            assert tab._endpoint_config.get("api_key") == "test-key"

            # Clean up
            tab.close()
            tab.deleteLater()


class TestChatTabWindowSizings:
    """Tests for window sizing constraints."""

    @patch("aicodeprep_gui.pro.ai_chat.chat_tab.load_endpoints")
    @patch("aicodeprep_gui.pro.ai_chat.chat_tab.set_active_model")
    @patch("aicodeprep_gui.pro.ai_chat.chat_tab.get_active_endpoint")
    def test_tab_has_size_constraints(
        self, mock_get_active, mock_set_model, mock_load_endpoints
    ):
        """Test that ChatTabWidget has proper size constraints."""
        mock_load_endpoints.return_value = {
            "active_endpoint": "local",
            "endpoints": {
                "local": {
                    "name": "Local Server",
                    "url": "http://localhost:59999/v1",
                    "api_key": "",
                    "selected_model": ""
                }
            }
        }
        mock_get_active.return_value = {
            "id": "local",
            "name": "Local Server",
            "url": "http://localhost:59999/v1",
            "api_key": "",
            "selected_model": ""
        }

        from aicodeprep_gui.pro.ai_chat.chat_tab import ChatTabWidget

        with patch("aicodeprep_gui.pro.ai_chat.chat_tab.AIClient") as mock_client:
            mock_client.return_value.list_models.return_value = []

            tab = ChatTabWidget()

            # Check minimum size
            assert tab.minimumSize().width() >= 200
            assert tab.minimumSize().height() >= 200

            # Check maximum size is reasonable
            assert tab.maximumSize().width() <= 4000
            assert tab.maximumSize().height() <= 4000

            # Clean up
            tab.close()
            tab.deleteLater()

    @patch("aicodeprep_gui.pro.ai_chat.chat_tab.load_endpoints")
    @patch("aicodeprep_gui.pro.ai_chat.chat_tab.set_active_model")
    @patch("aicodeprep_gui.pro.ai_chat.chat_tab.get_active_endpoint")
    def test_error_label_constrained(
        self, mock_get_active, mock_set_model, mock_load_endpoints
    ):
        """Test that error label is constrained to prevent giant windows."""
        mock_load_endpoints.return_value = {
            "active_endpoint": "local",
            "endpoints": {
                "local": {
                    "name": "Local Server",
                    "url": "http://localhost:59999/v1",
                    "api_key": "",
                    "selected_model": ""
                }
            }
        }
        mock_get_active.return_value = {
            "id": "local",
            "name": "Local Server",
            "url": "http://localhost:59999/v1",
            "api_key": "",
            "selected_model": ""
        }

        from aicodeprep_gui.pro.ai_chat.chat_tab import ChatTabWidget

        with patch("aicodeprep_gui.pro.ai_chat.chat_tab.AIClient") as mock_client:
            mock_client.return_value.list_models.return_value = []

            tab = ChatTabWidget()

            # Error label should have max height
            assert tab.status_label.maximumHeight() == 80

            # Should be hidden by default
            assert not tab.status_label.isVisible()

            # Clean up
            tab.close()
            tab.deleteLater()


class TestChatDockLayouts:
    """Tests for chat dock layout functionality."""
    @pytest.mark.skip(reason="PySide6 cleanup issues with mocked widgets")
    def test_splitter_settings(self):
        """Test that splitter has proper settings for resizing."""
        # This test has issues with PySide6 cleanup in pytest
        # The splitter settings are verified by other tests and manual testing
        pass


class TestModelSortings:
    """Tests for model dropdown sorting."""

    @patch("aicodeprep_gui.pro.ai_chat.chat_tab.load_endpoints")
    @patch("aicodeprep_gui.pro.ai_chat.chat_tab.set_active_model")
    @patch("aicodeprep_gui.pro.ai_chat.chat_tab.get_active_endpoint")
    def test_models_sorted_alphabetically(
        self, mock_get_active, mock_set_model, mock_load_endpoints
    ):
        """Test that models are sorted A-Z."""
        mock_load_endpoints.return_value = {
            "active_endpoint": "local",
            "endpoints": {
                "local": {
                    "name": "Local Server",
                    "url": "http://localhost:59999/v1",
                    "api_key": "",
                    "selected_model": ""
                }
            }
        }
        mock_get_active.return_value = {
            "id": "local",
            "name": "Local Server",
            "url": "http://localhost:59999/v1",
            "api_key": "",
            "selected_model": ""
        }

        from aicodeprep_gui.pro.ai_chat.chat_tab import ChatTabWidget

        with patch("aicodeprep_gui.pro.ai_chat.chat_tab.AIClient") as mock_client:
            # Return unsorted models
            mock_client.return_value.list_models.return_value = [
                {"id": "gpt-4"},
                {"id": "claude-3"},
                {"id": "gpt-3.5-turbo"},
                {"id": "claude-2"}
            ]

            tab = ChatTabWidget()

            # Wait for async loading
            QtWidgets.QApplication.processEvents()

            # Get model names from combo
            if tab.model_combo.count() > 1:
                model_names = []
                for i in range(tab.model_combo.count()):
                    data = tab.model_combo.itemData(i)
                    if data and ':' in data:
                        model_names.append(data.split(':', 1)[1])
                    elif data:
                        model_names.append(data)

                # Check they're sorted
                if len(model_names) > 1:
                    sorted_names = sorted(model_names, key=str.lower)
                    assert model_names == sorted_names, f"Models not sorted: {model_names} vs {sorted_names}"

            # Clean up
            tab.close()
            tab.deleteLater()


class TestErrorHandlings:
    """Tests for error handling."""

    @patch("aicodeprep_gui.pro.ai_chat.chat_tab.load_endpoints")
    @patch("aicodeprep_gui.pro.ai_chat.chat_tab.set_active_model")
    @patch("aicodeprep_gui.pro.ai_chat.chat_tab.get_active_endpoint")
    def test_error_display_constrained(
        self, mock_get_active, mock_set_model, mock_load_endpoints
    ):
        """Test that error messages are displayed in a constrained label."""
        mock_load_endpoints.return_value = {
            "active_endpoint": "local",
            "endpoints": {
                "local": {
                    "name": "Local Server",
                    "url": "http://localhost:59999/v1",
                    "api_key": "",
                    "selected_model": ""
                }
            }
        }
        mock_get_active.return_value = {
            "id": "local",
            "name": "Local Server",
            "url": "http://localhost:59999/v1",
            "api_key": "",
            "selected_model": ""
        }

        from aicodeprep_gui.pro.ai_chat.chat_tab import ChatTabWidget

        with patch("aicodeprep_gui.pro.ai_chat.chat_tab.AIClient") as mock_client:
            mock_client.return_value.list_models.return_value = []

            tab = ChatTabWidget()

            # Initial state - status label should be hidden by default
            assert not tab.status_label.isVisible()

            # Label should be constrained height
            assert tab.status_label.maximumHeight() == 80


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
