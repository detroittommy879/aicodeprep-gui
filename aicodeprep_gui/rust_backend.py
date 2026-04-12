import hashlib
import json
import logging
import os
import platform
import stat
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests

from aicodeprep_gui.config import get_config_dir
from aicodeprep_gui.user_settings import get_section

logger = logging.getLogger(__name__)


@dataclass
class RustProcessResult:
    ok: bool
    files_processed: int = 0
    error: str = ""
    used_fallback: bool = False
    secret_map_file: Optional[str] = None


def worker_binary_name() -> str:
    return "aicp-rust-worker.exe" if platform.system() == "Windows" else "aicp-rust-worker"


def worker_cache_dir() -> Path:
    path = get_config_dir() / "rust-worker"
    path.mkdir(parents=True, exist_ok=True)
    return path


def default_worker_path() -> Path:
    return worker_cache_dir() / worker_binary_name()


def get_worker_path() -> Path:
    rust_cfg = get_section("rust_backend")
    configured = str(rust_cfg.get("worker_path", "")).strip()
    if configured:
        return Path(configured)
    return default_worker_path()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _platform_key() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if machine in {"amd64", "x86_64", "x64"}:
        machine = "x86_64"
    elif machine in {"arm64", "aarch64"}:
        machine = "aarch64"
    return f"{system}-{machine}"


def download_worker_binary(download_url: str, expected_sha256: str = "") -> tuple[bool, str]:
    url = download_url.strip()
    if not url:
        return False, "No download URL configured"

    if "{platform}" in url:
        url = url.replace("{platform}", _platform_key())

    target = get_worker_path()
    target.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        with requests.get(url, stream=True, timeout=60) as response:
            response.raise_for_status()
            with open(tmp_path, "wb") as handle:
                for chunk in response.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        handle.write(chunk)

        if expected_sha256.strip():
            actual = _sha256_file(tmp_path)
            if actual.lower() != expected_sha256.strip().lower():
                return False, "Downloaded worker checksum mismatch"

        os.replace(tmp_path, target)
        if platform.system() != "Windows":
            target.chmod(target.stat().st_mode | stat.S_IXUSR |
                         stat.S_IXGRP | stat.S_IXOTH)

        return True, str(target)
    except Exception as exc:
        logger.error(f"Failed to download Rust worker: {exc}")
        return False, str(exc)
    finally:
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except Exception:
            pass


def process_with_rust_worker(
    selected_files,
    output_file,
    fmt,
    prompt,
    prompt_to_top,
    prompt_to_bottom,
) -> RustProcessResult:
    rust_cfg = get_section("rust_backend")
    secret_cfg = rust_cfg.get("secret_guard", {}) if isinstance(
        rust_cfg.get("secret_guard", {}), dict) else {}

    worker = get_worker_path()
    if not worker.exists():
        auto_download = bool(rust_cfg.get("auto_download", False))
        download_url = str(rust_cfg.get("download_url", "")).strip()
        download_sha256 = str(rust_cfg.get("download_sha256", "")).strip()
        if auto_download and download_url:
            ok, result = download_worker_binary(download_url, download_sha256)
            if ok:
                worker = Path(result)
            else:
                return RustProcessResult(
                    ok=False,
                    error=f"Rust worker missing and auto-download failed: {result}",
                )
        else:
            return RustProcessResult(ok=False, error=f"Rust worker not found at {worker}")

    request_payload = {
        "selected_files": list(selected_files),
        "output_file": output_file,
        "format": fmt,
        "prompt": prompt,
        "prompt_to_top": bool(prompt_to_top),
        "prompt_to_bottom": bool(prompt_to_bottom),
        "cwd": os.getcwd(),
        "secret_mode": bool(secret_cfg.get("enabled", False)),
        "placeholder_prefix": str(secret_cfg.get("placeholder_prefix", "REDACTED_SECRET_")),
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as handle:
        request_path = handle.name
        json.dump(request_payload, handle)

    try:
        proc = subprocess.run(
            [str(worker), "--request", request_path],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if proc.returncode != 0:
            stderr = (proc.stderr or "").strip()
            stdout = (proc.stdout or "").strip()
            details = stderr or stdout or f"exit code {proc.returncode}"
            return RustProcessResult(ok=False, error=f"Rust worker failed: {details}")

        raw = (proc.stdout or "").strip()
        if not raw:
            return RustProcessResult(ok=False, error="Rust worker returned empty response")

        try:
            response = json.loads(raw)
        except json.JSONDecodeError as exc:
            return RustProcessResult(ok=False, error=f"Invalid Rust worker response: {exc}")

        if not response.get("ok", False):
            return RustProcessResult(ok=False, error=str(response.get("error", "Unknown Rust worker error")))

        return RustProcessResult(
            ok=True,
            files_processed=int(response.get("files_processed", 0)),
            secret_map_file=response.get("secret_map_file"),
        )
    except Exception as exc:
        logger.error(f"Rust worker execution error: {exc}")
        return RustProcessResult(ok=False, error=str(exc))
    finally:
        try:
            os.remove(request_path)
        except OSError:
            pass
