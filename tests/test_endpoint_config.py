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
        assert data["endpoints"]["local"]["name"] == "Local / Custom Endpoint"
        assert data["endpoints"]["local"]["url"] == ""
        assert data["endpoints"]["local"]["api_key"] == ""
        assert data["endpoints"]["local"]["selected_model"] == ""

        # Verify file was created
        endpoints_file = get_endpoints_file()
        assert endpoints_file.exists()

        with open(endpoints_file, "r") as f:
            file_data = toml.load(f)
            assert file_data == data

    @patch("aicodeprep_gui.pro.ai_assist.endpoint_config.get_config_dir")
    def test_empty_local_endpoint_hydrates_from_custom_provider(self, mock_config_dir, tmp_path):
        mock_config_dir.return_value = tmp_path

        endpoints_file = tmp_path / "ai-endpoints.toml"
        endpoints_file.write_text(
            toml.dumps({
                "active_endpoint": "local",
                "endpoints": {
                    "local": {
                        "name": "Local / Custom Endpoint",
                        "url": "",
                        "api_key": "",
                        "selected_model": "",
                    }
                }
            }),
            encoding="utf-8",
        )

        api_keys_file = tmp_path / "api-keys.toml"
        api_keys_file.write_text(
            toml.dumps({
                "custom": {
                    "name": "Working Custom Endpoint",
                    "base_url": "https://real.example/v1",
                    "api_key": "real-key",
                }
            }),
            encoding="utf-8",
        )

        data = load_endpoints()

        assert data["endpoints"]["local"]["name"] == "Working Custom Endpoint"
        assert data["endpoints"]["local"]["url"] == "https://real.example/v1"
        assert data["endpoints"]["local"]["api_key"] == "real-key"
        assert data["endpoints"]["local"]["selected_model"] == ""

    @patch("aicodeprep_gui.pro.ai_assist.endpoint_config.get_config_dir")
    def test_local_endpoint_save_updates_shared_custom_provider(self, mock_config_dir, tmp_path):
        mock_config_dir.return_value = tmp_path

        data = {
            "active_endpoint": "local",
            "endpoints": {
                "local": {
                    "name": "Shared Endpoint",
                    "url": "https://shared.example/v1",
                    "api_key": "shared-key",
                    "selected_model": "shared-model",
                }
            }
        }

        save_endpoints(data)

        api_keys_file = tmp_path / "api-keys.toml"
        api_keys_data = toml.load(api_keys_file)
        assert api_keys_data["custom"]["name"] == "Shared Endpoint"
        assert api_keys_data["custom"]["base_url"] == "https://shared.example/v1"
        assert api_keys_data["custom"]["api_key"] == "shared-key"
        assert api_keys_data["custom"]["selected_model"] == "shared-model"

    @patch("aicodeprep_gui.pro.ai_assist.endpoint_config.get_config_dir")
    def test_active_non_local_endpoint_save_does_not_pollute_custom_provider(self, mock_config_dir, tmp_path):
        """Non-local active endpoints must NOT overwrite api-keys.toml [custom].
        Only the local endpoint is mirrored to [custom] so that the sync logic
        on the next load_endpoints() call does not overwrite local with stale data
        from a different named endpoint."""
        mock_config_dir.return_value = tmp_path

        data = {
            "active_endpoint": "extra",
            "endpoints": {
                "local": {
                    "name": "Local / Custom Endpoint",
                    "url": "",
                    "api_key": "",
                    "selected_model": "",
                },
                "extra": {
                    "name": "Extra Endpoint",
                    "url": "https://extra.example/v1",
                    "api_key": "extra-key",
                    "selected_model": "extra-model",
                },
            },
        }

        save_endpoints(data)

        api_keys_file = tmp_path / "api-keys.toml"
        api_keys_data = toml.load(api_keys_file)
        # Local endpoint is empty, so [custom] should reflect that (blank)
        assert api_keys_data["custom"]["base_url"] == ""
        assert api_keys_data["custom"]["api_key"] == ""

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

        assert loaded_data["active_endpoint"] == custom_data["active_endpoint"]
        assert loaded_data["endpoints"]["custom"] == custom_data["endpoints"]["custom"]
        # Should be ensured by load_endpoints
        assert "local" in loaded_data["endpoints"]

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
