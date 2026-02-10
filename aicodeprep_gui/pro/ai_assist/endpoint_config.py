from pathlib import Path
import toml
from aicodeprep_gui.config import get_config_dir

ENDPOINTS_FILENAME = "ai-endpoints.toml"


def get_endpoints_file() -> Path:
    """Return path to ~/.aicodeprep-gui/ai-endpoints.toml"""
    return get_config_dir() / ENDPOINTS_FILENAME


def load_endpoints() -> dict:
    """Load endpoints config from TOML. Creates default if missing.
    Returns dict like:
    {
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
    """
    file_path = get_endpoints_file()
    if not file_path.exists():
        default_data = {
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
        save_endpoints(default_data)
        return default_data

    try:
        with open(file_path, "r") as f:
            return toml.load(f)
    except Exception:
        # Fallback if corrupted
        return {
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


def save_endpoints(data: dict) -> None:
    """Save endpoints config to TOML file."""
    file_path = get_endpoints_file()
    with open(file_path, "w") as f:
        toml.dump(data, f)


def get_active_endpoint() -> dict:
    """Get the currently active endpoint config dict (with name, url, api_key, selected_model).
    Returns the endpoint dict merged with its key as 'id'."""
    data = load_endpoints()
    active_id = data.get("active_endpoint", "local")
    endpoints = data.get("endpoints", {})

    if active_id not in endpoints:
        # Fallback to the first available endpoint if active_id is missing
        if endpoints:
            active_id = list(endpoints.keys())[0]
        else:
            # Should not happen with load_endpoints creating defaults
            return {}

    endpoint_config = endpoints[active_id].copy()
    endpoint_config["id"] = active_id
    return endpoint_config


def set_active_model(endpoint_id: str, model_id: str) -> None:
    """Set the selected model for an endpoint."""
    data = load_endpoints()
    if endpoint_id in data.get("endpoints", {}):
        data["endpoints"][endpoint_id]["selected_model"] = model_id
        save_endpoints(data)


def add_endpoint(endpoint_id: str, name: str, url: str, api_key: str = "") -> None:
    """Add a new endpoint to the config."""
    data = load_endpoints()
    if "endpoints" not in data:
        data["endpoints"] = {}

    data["endpoints"][endpoint_id] = {
        "name": name,
        "url": url,
        "api_key": api_key,
        "selected_model": ""
    }
    save_endpoints(data)


def remove_endpoint(endpoint_id: str) -> bool:
    """Remove an endpoint. Returns False if it's the last one (can't remove all).
    Also updates active_endpoint if the removed one was active."""
    data = load_endpoints()
    endpoints = data.get("endpoints", {})

    if len(endpoints) <= 1:
        return False

    if endpoint_id in endpoints:
        del endpoints[endpoint_id]

        # If we removed the active one, pick a new one
        if data.get("active_endpoint") == endpoint_id:
            data["active_endpoint"] = list(endpoints.keys())[0]

        save_endpoints(data)
        return True

    return False


def get_all_endpoint_ids() -> list:
    """Return list of all endpoint IDs."""
    data = load_endpoints()
    return list(data.get("endpoints", {}).keys())


def set_active_endpoint(endpoint_id: str) -> None:
    """Set which endpoint is active."""
    data = load_endpoints()
    if endpoint_id in data.get("endpoints", {}):
        data["active_endpoint"] = endpoint_id
        save_endpoints(data)
