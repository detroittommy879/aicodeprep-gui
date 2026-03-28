"""Shared Pro access state helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import logging
import re
from typing import Any, Optional

import requests

from aicodeprep_gui.user_settings import get_section, set_section


FREE_ACCESS_URL = "https://wuu73.org/aicp/aicp-free-now.md"
FREE_ACCESS_SECTION = "pro_free_access"
FREE_ACCESS_CACHE_TTL = timedelta(minutes=15)
FREE_ACCESS_TIMEOUT_SECONDS = 4

_TRUTHY_VALUES = {"1", "true", "yes", "on"}
_FALSY_VALUES = {"0", "false", "no", "off"}


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_timestamp(value: Any) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        normalized = value.strip()
        if normalized.endswith("Z"):
            normalized = normalized[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            return None
    else:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _parse_remote_free_flag(text: str) -> Optional[bool]:
    for raw_line in text.splitlines():
        line = raw_line.strip().strip('"').strip("'")
        if not line or line.startswith("#"):
            continue
        match = re.match(r"free\s*=\s*(.+)", line, re.IGNORECASE)
        if not match:
            continue
        token = match.group(1).strip().strip('"').strip("'").lower()
        if token in _TRUTHY_VALUES:
            return True
        if token in _FALSY_VALUES:
            return False
    return None


def _parse_remote_notice_message(text: str) -> str:
    for raw_line in text.splitlines():
        line = raw_line.strip().strip('"').strip("'")
        if not line or line.startswith("#"):
            continue
        match = re.match(r"(?:message|msg|notice)\s*=\s*(.+)",
                         line, re.IGNORECASE)
        if not match:
            continue
        token = match.group(1).strip().strip('"').strip("'")
        return token.replace("\\n", "\n").strip()
    return ""


def _has_verified_paid_license(data: Optional[dict[str, Any]] = None) -> bool:
    section = data if data is not None else get_section("pro_license")
    license_key = str(section.get("license_key", "") or "").strip()
    return bool(
        section.get("pro_enabled", False)
        and section.get("license_verified", False)
        and license_key
    )


def _read_cached_free_access(now: Optional[datetime] = None) -> Optional[bool]:
    cache = get_section(FREE_ACCESS_SECTION)
    checked_at = _parse_timestamp(cache.get("last_checked"))
    if checked_at is None:
        return None

    current_time = now or _now_utc()
    if current_time - checked_at > FREE_ACCESS_CACHE_TTL:
        return None
    return bool(cache.get("free_for_all", False))


def _read_cached_remote_access_state(now: Optional[datetime] = None) -> Optional[dict[str, Any]]:
    cache = get_section(FREE_ACCESS_SECTION)
    checked_at = _parse_timestamp(cache.get("last_checked"))
    if checked_at is None:
        return None

    current_time = now or _now_utc()
    if current_time - checked_at > FREE_ACCESS_CACHE_TTL:
        return None

    return {
        "free_for_all": bool(cache.get("free_for_all", False)),
        "announcement_message": str(cache.get("announcement_message", "") or "").strip(),
        "source_url": str(cache.get("source_url", FREE_ACCESS_URL) or FREE_ACCESS_URL),
        "last_checked": checked_at,
    }


def _write_cached_free_access(enabled: bool, checked_at: Optional[datetime] = None) -> None:
    timestamp = checked_at or _now_utc()
    set_section(
        FREE_ACCESS_SECTION,
        {
            "free_for_all": bool(enabled),
            "announcement_message": "",
            "last_checked": timestamp.isoformat(),
            "source_url": FREE_ACCESS_URL,
        },
    )


def _write_cached_remote_access_state(
    enabled: bool,
    announcement_message: str,
    checked_at: Optional[datetime] = None,
) -> None:
    timestamp = checked_at or _now_utc()
    set_section(
        FREE_ACCESS_SECTION,
        {
            "free_for_all": bool(enabled),
            "announcement_message": announcement_message.strip(),
            "last_checked": timestamp.isoformat(),
            "source_url": FREE_ACCESS_URL,
        },
    )


def get_remote_access_state(now: Optional[datetime] = None) -> dict[str, Any]:
    cached = _read_cached_remote_access_state(now=now)
    if cached is not None:
        return cached

    checked_at = now or _now_utc()
    try:
        response = requests.get(
            FREE_ACCESS_URL,
            timeout=FREE_ACCESS_TIMEOUT_SECONDS,
            headers={"Accept": "text/plain, text/markdown;q=0.9, */*;q=0.1"},
        )
        response.raise_for_status()
        free_enabled = bool(_parse_remote_free_flag(response.text))
        announcement_message = _parse_remote_notice_message(response.text)
        _write_cached_remote_access_state(
            free_enabled,
            announcement_message,
            checked_at=checked_at,
        )
        return {
            "free_for_all": free_enabled,
            "announcement_message": announcement_message,
            "source_url": FREE_ACCESS_URL,
            "last_checked": checked_at,
        }
    except requests.RequestException as exc:
        logging.warning("Could not fetch remote Pro free-access flag: %s", exc)
        return {
            "free_for_all": False,
            "announcement_message": "",
            "source_url": FREE_ACCESS_URL,
            "last_checked": checked_at,
        }


def is_free_access_enabled(now: Optional[datetime] = None) -> bool:
    cached = _read_cached_free_access(now=now)
    if cached is not None:
        return cached
    return bool(get_remote_access_state(now=now).get("free_for_all", False))


def is_pro_enabled(argv: Optional[list[str]] = None) -> bool:
    args = argv if argv is not None else []

    if "--notpro" in args:
        logging.info(
            "Pro features temporarily disabled via command-line (--notpro flag).")
        return False

    if "--262144" in args:
        logging.info("Pro features enabled via secret command-line flag.")
        return True

    try:
        paid_license = get_section("pro_license")
        if _has_verified_paid_license(paid_license):
            return True
        if is_free_access_enabled():
            logging.info(
                "Pro features temporarily enabled for everyone via remote flag.")
            return True
    except Exception as exc:
        logging.error("Settings error in is_pro_enabled: %s", exc)

    return False
