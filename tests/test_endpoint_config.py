import pytest
from pathlib import Path
from unittest.mock import patch
import toml

from aicodeprep_gui.pro.ai_assist.endpoint_config import (
    load_endpoints,
    save_endpoints,
    get_active_endpoint,
    set_active_model,
    add_endpoint,
    remove_endpoint,
    get_all_endpoint_ids,
    set_active_endpoint,
    get_endpoints_file
)


class TestEndpointConfig:
    @patch("aicodeprep_gui.pro.ai_assist.endpoint_config.get_config_dir")
    def test_endpoint_default_creation(self, mock_config_dir, tmp_path):
        mock_config_dir.return_value = tmp_path

        # Load endpoints when file doesn't exist
        data = load_endpoints()

        # Verify default structure
        assert data["active_endpoint"] == "local"
        assert "local" in data["endpoints"]
        assert data["endpoints"]["local"]["name"] == "Local Server"
        assert data["endpoints"]["local"]["url"] == "http://localhost:59999/v1"
        assert data["endpoints"]["local"]["api_key"] == ""
        assert data["endpoints"]["local"]["selected_model"] == ""

        # Verify file was created
        endpoints_file = get_endpoints_file()
        assert endpoints_file.exists()

        with open(endpoints_file, "r") as f:
            file_data = toml.load(f)
            assert file_data == data

    @patch("aicodeprep_gui.pro.ai_assist.endpoint_config.get_config_dir")
    def test_endpoint_load_save_roundtrip(self, mock_config_dir, tmp_path):
        mock_config_dir.return_value = tmp_path

        custom_data = {
            "active_endpoint": "custom",
            "endpoints": {
                "custom": {
                    "name": "Custom",
                    "url": "http://custom:1234/v1",
                    "api_key": "test-key",
                    "selected_model": "test-model"
                }
            }
        }

        save_endpoints(custom_data)
        loaded_data = load_endpoints()

        assert loaded_data == custom_data

    @patch("aicodeprep_gui.pro.ai_assist.endpoint_config.get_config_dir")
    def test_endpoint_add_remove(self, mock_config_dir, tmp_path):
        mock_config_dir.return_value = tmp_path

        # Start with default
        load_endpoints()

        # Add new endpoint
        add_endpoint("new-one", "New Endpoint", "http://new:8080/v1", "key123")

        ids = get_all_endpoint_ids()
        assert "new-one" in ids
        assert "local" in ids

        data = load_endpoints()
        assert data["endpoints"]["new-one"]["name"] == "New Endpoint"
        assert data["endpoints"]["new-one"]["api_key"] == "key123"

        # Remove it
        success = remove_endpoint("new-one")
        assert success is True

        ids = get_all_endpoint_ids()
        assert "new-one" not in ids
        assert "local" in ids

    @patch("aicodeprep_gui.pro.ai_assist.endpoint_config.get_config_dir")
    def test_endpoint_cannot_remove_last(self, mock_config_dir, tmp_path):
        mock_config_dir.return_value = tmp_path

        # Start with default (only 'local')
        load_endpoints()

        # Try to remove 'local'
        success = remove_endpoint("local")
        assert success is False

        ids = get_all_endpoint_ids()
        assert "local" in ids
        assert len(ids) == 1

    @patch("aicodeprep_gui.pro.ai_assist.endpoint_config.get_config_dir")
    def test_endpoint_set_active_model(self, mock_config_dir, tmp_path):
        mock_config_dir.return_value = tmp_path

        load_endpoints()
        set_active_model("local", "gpt-4")

        data = load_endpoints()
        assert data["endpoints"]["local"]["selected_model"] == "gpt-4"

    @patch("aicodeprep_gui.pro.ai_assist.endpoint_config.get_config_dir")
    def test_endpoint_set_active_endpoint(self, mock_config_dir, tmp_path):
        mock_config_dir.return_value = tmp_path

        load_endpoints()
        add_endpoint("remote", "Remote", "http://remote/v1")

        set_active_endpoint("remote")

        data = load_endpoints()
        assert data["active_endpoint"] == "remote"

    @patch("aicodeprep_gui.pro.ai_assist.endpoint_config.get_config_dir")
    def test_endpoint_get_active(self, mock_config_dir, tmp_path):
        mock_config_dir.return_value = tmp_path

        load_endpoints()
        add_endpoint("remote", "Remote", "http://remote/v1", "remote-key")
        set_active_model("remote", "remote-model")
        set_active_endpoint("remote")

        active = get_active_endpoint()
        assert active["id"] == "remote"
        assert active["name"] == "Remote"
        assert active["url"] == "http://remote/v1"
        assert active["api_key"] == "remote-key"
        assert active["selected_model"] == "remote-model"

    @patch("aicodeprep_gui.pro.ai_assist.endpoint_config.get_config_dir")
    def test_remove_active_updates_active(self, mock_config_dir, tmp_path):
        mock_config_dir.return_value = tmp_path

        load_endpoints()
        add_endpoint("secondary", "Secondary", "http://secondary/v1")
        set_active_endpoint("secondary")

        # Remove the currently active endpoint
        success = remove_endpoint("secondary")
        assert success is True

        data = load_endpoints()
        assert data["active_endpoint"] != "secondary"
        assert data["active_endpoint"] in data["endpoints"]
