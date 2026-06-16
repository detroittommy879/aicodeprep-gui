from pathlib import Path
import logging
import toml
from aicodeprep_gui.config import get_config_dir

ENDPOINTS_FILENAME = "ai-endpoints.toml"
DEFAULT_ENDPOINT_ID = "local"
DEFAULT_ENDPOINT_NAME = "Local / Custom Endpoint"
LEGACY_EXTRA_ENDPOINTS = {
    "http://extra.wuu73.org/aimodels/v1",
    "https://extra.wuu73.org/aimodels/v1",
}

logger = logging.getLogger(__name__)


def _default_endpoints_data() -> dict:
    return {
        "active_endpoint": DEFAULT_ENDPOINT_ID,
        "endpoints": {
            DEFAULT_ENDPOINT_ID: {
                "name": DEFAULT_ENDPOINT_NAME,
                "url": "",
                "api_key": "",
                "selected_model": ""
            }
        }
    }


def _blank_local_endpoint() -> dict:
    return {
        "name": DEFAULT_ENDPOINT_NAME,
        "url": "",
        "api_key": "",
        "selected_model": "",
    }


def _default_api_keys_data() -> dict:
    return {
        "openrouter": {
            "api_key": "",
            "base_url": "https://openrouter.ai/api/v1",
            "site_url": "https://github.com/detroittommy879/aicodeprep-gui",
            "app_name": "aicodeprep-gui",
        },
        "openai": {
            "api_key": "",
            "base_url": "https://api.openai.com/v1",
        },
        "gemini": {
            "api_key": "",
            "base_url": "https://generativelanguage.googleapis.com/v1beta",
        },
        "custom": {
            "api_key": "",
            "base_url": "",
            "name": DEFAULT_ENDPOINT_NAME,
            "selected_model": "",
        },
    }


def _get_api_keys_file() -> Path:
    return get_config_dir() / "api-keys.toml"


def _load_api_keys_data() -> dict:
    file_path = _get_api_keys_file()
    if not file_path.exists():
        data = _default_api_keys_data()
        with open(file_path, "w") as f:
            toml.dump(data, f)
        return data

    try:
        with open(file_path, "r") as f:
            return toml.load(f)
    except Exception:
        return _default_api_keys_data()


def _save_api_keys_data(data: dict) -> None:
    file_path = _get_api_keys_file()
    with open(file_path, "w") as f:
        toml.dump(data, f)


def _load_custom_provider_endpoint() -> dict:
    config = _load_api_keys_data()
    custom = config.get("custom", {}) or {}
    return {
        "name": (custom.get("name") or "").strip() or DEFAULT_ENDPOINT_NAME,
        "url": (custom.get("base_url") or "").strip(),
        "api_key": (custom.get("api_key") or "").strip(),
        "selected_model": (custom.get("selected_model") or "").strip(),
    }


def _has_real_compatible_endpoint(endpoint: dict | None) -> bool:
    if not isinstance(endpoint, dict):
        return False
    url = (endpoint.get("url") or "").strip()
    return bool(url)


def _has_endpoint_payload(endpoint: dict | None) -> bool:
    if not isinstance(endpoint, dict):
        return False
    if (endpoint.get("url") or "").strip():
        return True
    if (endpoint.get("api_key") or "").strip():
        return True
    if (endpoint.get("selected_model") or "").strip():
        return True
    name = (endpoint.get("name") or "").strip()
    return bool(name) and name != DEFAULT_ENDPOINT_NAME


def is_legacy_extra_endpoint(url: str | None) -> bool:
    """Return True for the retired hosted test endpoint from older releases."""
    return (url or "").strip().rstrip("/") in LEGACY_EXTRA_ENDPOINTS


def _normalize_endpoint(endpoint: dict | None) -> dict:
    source = endpoint or {}
    url = (source.get("url") or "").strip()
    api_key = (source.get("api_key") or "").strip()
    selected_model = (source.get("selected_model") or "").strip()
    return {
        "name": (source.get("name") or "").strip() or DEFAULT_ENDPOINT_NAME,
        "url": url,
        "api_key": api_key,
        "selected_model": selected_model,
    }


def _write_custom_provider_endpoint(endpoint: dict) -> None:
    config = _load_api_keys_data()
    custom = dict(config.get("custom", {}) or {})
    custom["name"] = (endpoint.get("name")
                      or "").strip() or DEFAULT_ENDPOINT_NAME
    custom["base_url"] = (endpoint.get("url") or "").strip()
    custom["api_key"] = (endpoint.get("api_key") or "").strip()
    custom["selected_model"] = (endpoint.get("selected_model") or "").strip()
    config["custom"] = custom
    _save_api_keys_data(config)


def _sync_local_endpoint_with_custom_provider(data: dict) -> tuple[dict, bool]:
    if not isinstance(data, dict):
        return data, False

    synced = dict(data)
    endpoints = dict(synced.get("endpoints", {}) or {})
    if not synced.get("active_endpoint"):
        synced["active_endpoint"] = DEFAULT_ENDPOINT_ID

    custom_endpoint = _normalize_endpoint(_load_custom_provider_endpoint())
    custom_has_payload = _has_endpoint_payload(custom_endpoint)
    local_exists = DEFAULT_ENDPOINT_ID in endpoints
    local_endpoint = _normalize_endpoint(endpoints.get(
        DEFAULT_ENDPOINT_ID)) if local_exists else None
    local_has_payload = _has_endpoint_payload(local_endpoint)

    if not local_exists and not endpoints:
        endpoints[DEFAULT_ENDPOINT_ID] = _blank_local_endpoint()
        synced["endpoints"] = endpoints
        return synced, True

    if not local_exists:
        if synced.get("active_endpoint") == DEFAULT_ENDPOINT_ID and custom_has_payload:
            endpoints[DEFAULT_ENDPOINT_ID] = custom_endpoint
            synced["endpoints"] = endpoints
            return synced, True
        return synced, False

    if local_has_payload and not custom_has_payload:
        # local has data but custom is empty — push local → custom
        _write_custom_provider_endpoint(local_endpoint)
        return synced, local_endpoint != endpoints.get(DEFAULT_ENDPOINT_ID)

    if local_has_payload and custom_has_payload:
        # Both have data — local is the source of truth; fix custom if it drifted
        # (e.g. a non-local active endpoint was previously mirrored to custom)
        if local_endpoint != custom_endpoint:
            _write_custom_provider_endpoint(local_endpoint)
        return synced, False

    if custom_has_payload and not local_has_payload:
        # local is blank but custom has data — hydrate local from custom
        desired_local = custom_endpoint
        if local_endpoint != desired_local:
            endpoints[DEFAULT_ENDPOINT_ID] = desired_local
            synced["endpoints"] = endpoints
            return synced, True
        return synced, False

    # Neither has payload — ensure local is blank
    desired_local = _blank_local_endpoint()
    if local_endpoint != desired_local:
        endpoints[DEFAULT_ENDPOINT_ID] = desired_local
        synced["endpoints"] = endpoints
        return synced, True

    return synced, False


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
                "name": "Local / Custom Endpoint",
                "url": "",
                "api_key": "",
                "selected_model": ""
            }
        }
    }
    """
    file_path = get_endpoints_file()
    if not file_path.exists():
        default_data = _default_endpoints_data()
        save_endpoints(default_data)
        return default_data

    try:
        with open(file_path, "r") as f:
            data = toml.load(f)
    except Exception:
        # Fallback if corrupted
        return _default_endpoints_data()

    if not isinstance(data, dict):
        data = _default_endpoints_data()

    # Ensure local endpoint always exists
    if "endpoints" not in data:
        data["endpoints"] = {}
    if DEFAULT_ENDPOINT_ID not in data["endpoints"]:
        data["endpoints"][DEFAULT_ENDPOINT_ID] = _blank_local_endpoint()

    synced_data, synced = _sync_local_endpoint_with_custom_provider(data)

    if synced:
        file_path = get_endpoints_file()
        with open(file_path, "w") as f:
            toml.dump(synced_data, f)
    return synced_data


def save_endpoints(data: dict) -> None:
    """Save endpoints config to TOML file."""
    endpoints = (data.get("endpoints", {}) or {})

    # Always mirror the LOCAL endpoint to api-keys.toml [custom].
    # Never mirror a non-local active endpoint there — that would pollute
    # api-keys.toml [custom] and cause the sync logic to overwrite local
    # on the next load_endpoints() call.
    local_endpoint = endpoints.get(DEFAULT_ENDPOINT_ID)
    if isinstance(local_endpoint, dict):
        normalized_local = _normalize_endpoint(local_endpoint)
        if _has_endpoint_payload(normalized_local):
            _write_custom_provider_endpoint(normalized_local)
        else:
            _write_custom_provider_endpoint(_blank_local_endpoint())

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
