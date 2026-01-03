import logging
from typing import Optional

from packaging.version import parse as parse_version

try:
    import requests
except ImportError:
    requests = None

from . import __version__

UPDATE_URL = "https://wuu73.org/aicp/aicp-ver.md"

def get_update_info() -> Optional[str]:
    """
    Fetches update information from a simple markdown file on a server.

    The file is expected to have at least two lines:
    1. ### 1.2.3
    2. #### Message to display for the update

    Returns:
        A string message to display if an update is available, otherwise None.
        Returns None if requests is not installed, on network errors, or if the
        file format is incorrect.
    """
    if not requests:
        logging.warning("Requests library not installed, skipping update check.")
        return None

    try:
        response = requests.get(UPDATE_URL, timeout=5)
        response.raise_for_status()

        lines = response.text.strip().split('\n')
        if len(lines) < 2:
            logging.warning(f"Update check: Fetched file from {UPDATE_URL} has fewer than 2 lines.")
            return None

        latest_version_line = lines[0].strip()
        update_message_line = lines[1].strip()

        # Extract version from a line like "### 1.1.0"
        if latest_version_line.startswith("###"):
            latest_version_str = latest_version_line.replace("###", "").strip()
        else:
            logging.warning(f"Update check: Malformed version line: '{latest_version_line}'")
            return None

        # Extract message from a line like "#### New Version available!..."
        if update_message_line.startswith("####"):
            update_message = update_message_line.replace("####", "").strip()
        else:
            logging.warning(f"Update check: Malformed message line: '{update_message_line}'")
            return None

        # Compare versions using packaging.version
        if parse_version(latest_version_str) > parse_version(__version__):
            logging.info(f"Update available: {latest_version_str} (current: {__version__})")
            return update_message
        else:
            # This is not an error, just for debugging.
            logging.info(f"Application is up to date. (current: {__version__}, latest: {latest_version_str})")
            return None

    except Exception as e:
        # Silently fail on any error (network, parsing, etc.) as requested.
        logging.warning(f"Update check failed with an exception: {e}")
        return None

def is_newer_version(current: str, latest: str) -> bool:
    """
    Helper function to compare two version strings.
    Returns True if latest > current.
    """
    try:
        return parse_version(latest) > parse_version(current)
    except Exception:
        return False
