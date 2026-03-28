import logging
from pathlib import Path
from typing import Any, Dict, Optional

import toml

from aicodeprep_gui.config import get_config_dir

logger = logging.getLogger(__name__)

SETTINGS_FILENAME = "settings.toml"
ADS_SECTION = "ads"
ADS_DISABLED_KEY = "disabled"


def _coerce_bool(value: Any, default: Any = None) -> Any:
    """Best-effort bool coercion for persisted settings values."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    return default


def get_settings_file() -> Path:
    """Return the path to the user settings file in ~/.aicodeprep-gui/."""
    return get_config_dir() / SETTINGS_FILENAME


def load_settings() -> Dict[str, Any]:
    """Load settings from disk; returns an empty dict if missing or invalid."""
    settings_file = get_settings_file()
    if settings_file.exists():
        try:
            return toml.load(settings_file)
        except Exception as exc:
            logger.error(
                f"Failed to load settings file {settings_file}: {exc}")
            return {}

    legacy = load_legacy_qsettings()
    return legacy if legacy else {}


def save_settings(data: Dict[str, Any]) -> None:
    """Persist settings to disk."""
    settings_file = get_settings_file()
    try:
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        with open(settings_file, "w", encoding="utf-8") as handle:
            toml.dump(data, handle)
    except Exception as exc:
        logger.error(f"Failed to save settings file {settings_file}: {exc}")


def get_section(section: str) -> Dict[str, Any]:
    """Return a settings section as a dict."""
    data = load_settings()
    return data.get(section, {}) if isinstance(data, dict) else {}


def set_section(section: str, values: Dict[str, Any]) -> None:
    """Replace a settings section with provided values."""
    data = load_settings()
    if not isinstance(data, dict):
        data = {}
    data[section] = values
    save_settings(data)


def get_setting(section: str, key: str, default: Any = None) -> Any:
    """Get a setting value from a section."""
    section_data = get_section(section)
    return section_data.get(key, default)


def set_setting(section: str, key: str, value: Any) -> None:
    """Set a single setting value."""
    section_data = get_section(section)
    section_data[key] = value
    set_section(section, section_data)


def get_ads_disabled_setting(default: Any = False) -> Any:
    """Return the user-global ads disabled preference.

    Reads the dedicated ads section first, then falls back to the older
    pro_options.ads_disabled key and migrates it forward into the user
    settings file.
    """
    value = _coerce_bool(get_setting(
        ADS_SECTION, ADS_DISABLED_KEY, None), None)
    if value is not None:
        return value

    legacy_value = _coerce_bool(
        get_setting("pro_options", "ads_disabled", None),
        None,
    )
    if legacy_value is not None:
        set_setting(ADS_SECTION, ADS_DISABLED_KEY, legacy_value)
        return legacy_value

    return default


def set_ads_disabled_setting(disabled: bool) -> None:
    """Persist the user-global ads disabled preference."""
    set_setting(ADS_SECTION, ADS_DISABLED_KEY, bool(disabled))


def delete_settings_file() -> None:
    """Delete the settings file if it exists."""
    settings_file = get_settings_file()
    if settings_file.exists():
        try:
            settings_file.unlink()
        except Exception as exc:
            logger.error(
                f"Failed to delete settings file {settings_file}: {exc}")


def load_legacy_qsettings() -> Dict[str, Any]:
    """Load settings from legacy QSettings storage if present."""
    try:
        from PySide6.QtCore import QSettings
    except Exception:
        return {}

    data: Dict[str, Any] = {}

    # Appearance
    appearance = {}
    appearance_settings = QSettings("aicodeprep-gui", "Appearance")
    if appearance_settings.contains("dark_mode"):
        appearance["dark_mode"] = appearance_settings.value(
            "dark_mode", type=bool)
    if appearance_settings.contains("dark_mode_enabled"):
        appearance.setdefault("dark_mode", appearance_settings.value(
            "dark_mode_enabled", type=bool))
    if appearance_settings.contains("font_size_multiplier"):
        appearance["font_size_multiplier"] = appearance_settings.value(
            "font_size_multiplier", type=int)
    if appearance:
        data["appearance"] = appearance

    # Panel visibility
    panel = {}
    panel_settings = QSettings("aicodeprep-gui", "PanelVisibility")
    if panel_settings.contains("options_visible"):
        panel["options_visible"] = panel_settings.value(
            "options_visible", True, type=bool)
    if panel_settings.contains("premium_visible"):
        panel["premium_visible"] = panel_settings.value(
            "premium_visible", False, type=bool)
    if panel:
        data["panel_visibility"] = panel

    # Prompt options
    prompt = {}
    prompt_settings = QSettings("aicodeprep-gui", "PromptOptions")
    if prompt_settings.contains("prompt_to_top"):
        prompt["prompt_to_top"] = prompt_settings.value(
            "prompt_to_top", True, type=bool)
    if prompt_settings.contains("prompt_to_bottom"):
        prompt["prompt_to_bottom"] = prompt_settings.value(
            "prompt_to_bottom", True, type=bool)
    if prompt:
        data["prompt_options"] = prompt

    # Language
    language_settings = QSettings("aicodeprep-gui", "Language")
    if language_settings.contains("current_language"):
        data["language"] = {
            "current_language": language_settings.value("current_language")
        }

    # User identity
    identity = {}
    identity_settings = QSettings("aicodeprep-gui", "UserIdentity")
    for key, cast in (
        ("user_uuid", str),
        ("generate_count", int),
        ("install_date", str),
        ("has_voted_on_features_v2", bool),
        ("v1.2.0_update_seen", bool),
    ):
        if identity_settings.contains(key):
            identity[key] = identity_settings.value(key, type=cast)
    if identity:
        data["user_identity"] = identity

    # Pro license
    pro = {}
    pro_settings = QSettings("aicodeprep-gui", "ProLicense")
    for key, cast in (
        ("pro_enabled", bool),
        ("license_key", str),
        ("license_verified", bool),
        ("activation_date", str),
        ("uses_count", int),
    ):
        if pro_settings.contains(key):
            pro[key] = pro_settings.value(key, type=cast)
    if pro:
        data["pro_license"] = pro

    # Flow Studio
    flow = {}
    flow_settings = QSettings("aicodeprep-gui", "FlowStudio")
    if flow_settings.contains("last_import_dir"):
        flow["last_import_dir"] = flow_settings.value("last_import_dir")
    if flow_settings.contains("last_export_dir"):
        flow["last_export_dir"] = flow_settings.value("last_export_dir")
    if flow:
        data["flow_studio"] = flow

    # Presets
    presets_settings = QSettings("aicodeprep-gui", "ButtonPresets")
    presets = {}
    presets_settings.beginGroup("presets")
    for key in presets_settings.childKeys():
        presets[key] = presets_settings.value(key, "")
    presets_settings.endGroup()

    presets_settings.beginGroup("internal")
    preset_version = presets_settings.value("preset_version", 0, type=int)
    presets_settings.endGroup()

    if presets or preset_version:
        data["presets"] = {
            "preset_version": preset_version,
            "items": presets,
        }

    return data


def legacy_qsettings_present() -> bool:
    """Return True if legacy QSettings storage has values."""
    legacy = load_legacy_qsettings()
    return bool(legacy)


def clear_legacy_qsettings() -> None:
    """Clear legacy QSettings entries."""
    try:
        from PySide6.QtCore import QSettings
    except Exception:
        return

    for group in (
        "ButtonPresets",
        "PromptOptions",
        "UserIdentity",
        "ProLicense",
        "Appearance",
        "PanelVisibility",
        "Language",
        "FlowStudio",
    ):
        try:
            QSettings("aicodeprep-gui", group).clear()
        except Exception:
            continue


def migrate_legacy_qsettings() -> bool:
    """Migrate legacy QSettings to settings.toml if present."""
    if get_settings_file().exists():
        return False
    legacy = load_legacy_qsettings()
    if not legacy:
        return False
    save_settings(legacy)
    return True
