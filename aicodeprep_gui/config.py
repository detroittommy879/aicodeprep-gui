"""Configuration management for aicodeprep-gui.

Handles API keys, endpoints, and other user settings stored in ~/.aicodeprep-gui/
"""

import os
import toml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def get_config_dir() -> Path:
    """Get the user configuration directory (~/.aicodeprep-gui/)."""
    home = Path.home()
    config_dir = home / ".aicodeprep-gui"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_api_keys_file() -> Path:
    """Get the API keys configuration file path."""
    return get_config_dir() / "api-keys.toml"


def ensure_api_keys_file():
    """Create the API keys file with default structure if it doesn't exist."""
    api_keys_file = get_api_keys_file()

    if not api_keys_file.exists():
        default_config = {
            "openrouter": {
                "api_key": "",
                "base_url": "https://openrouter.ai/api/v1",
                "site_url": "https://github.com/detroittommy879/aicodeprep-gui",
                "app_name": "aicodeprep-gui"
            },
            "openai": {
                "api_key": "",
                "base_url": "https://api.openai.com/v1"
            },
            "gemini": {
                "api_key": "",
                "base_url": "https://generativelanguage.googleapis.com/v1beta"
            },
            "custom": {
                "api_key": "",
                "base_url": "",
                "name": "Custom OpenAI-Compatible Endpoint"
            }
        }

        try:
            with open(api_keys_file, 'w') as f:
                toml.dump(default_config, f)
            logger.info(f"Created default API keys file: {api_keys_file}")
        except Exception as e:
            logger.error(f"Failed to create API keys file: {e}")


def load_api_config() -> Dict[str, Any]:
    """Load the API configuration from the TOML file."""
    ensure_api_keys_file()
    api_keys_file = get_api_keys_file()

    try:
        with open(api_keys_file, 'r') as f:
            return toml.load(f)
    except Exception as e:
        logger.error(f"Failed to load API keys file: {e}")
        return {}


def get_api_key(provider: str) -> Optional[str]:
    """Get an API key for a specific provider."""
    config = load_api_config()
    provider_config = config.get(provider, {})
    api_key = provider_config.get("api_key", "").strip()
    return api_key if api_key else None


def get_provider_config(provider: str) -> Dict[str, Any]:
    """Get the full configuration for a provider."""
    config = load_api_config()
    return config.get(provider, {})


def save_api_config(config: Dict[str, Any]):
    """Save the API configuration to the TOML file."""
    api_keys_file = get_api_keys_file()

    try:
        with open(api_keys_file, 'w') as f:
            toml.dump(config, f)
        logger.info(f"Saved API keys file: {api_keys_file}")
    except Exception as e:
        logger.error(f"Failed to save API keys file: {e}")


def update_api_key(provider: str, api_key: str):
    """Update an API key for a specific provider."""
    config = load_api_config()
    if provider not in config:
        config[provider] = {}
    config[provider]["api_key"] = api_key
    save_api_config(config)


def show_config_instructions():
    """Show user instructions for configuring API keys."""
    config_file = get_api_keys_file()

    message = f"""
API Configuration Required

To use Flow Studio with AI providers, please edit your configuration file:
{config_file}

Example configuration:
[openrouter]
api_key = "sk-or-v1-your-key-here"
base_url = "https://openrouter.ai/api/v1"

[openai]
api_key = "sk-your-openai-key-here"
base_url = "https://api.openai.com/v1"

The file will be created automatically with default settings.
Just add your API keys to the appropriate sections.
"""

    return message.strip()
