import hashlib
import json
import logging
import os
import platform
import shutil
import stat
import subprocess
import tempfile
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import List, Optional, Tuple

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


@dataclass
class RustScanResult:
    ok: bool
    files: Optional[List[Tuple[str, str, bool]]] = None
    error: str = ""
    used_fallback: bool = False


def worker_binary_name() -> str:
    return "aicp-rust-worker.exe" if platform.system() == "Windows" else "aicp-rust-worker"


def worker_cache_dir() -> Path:
    path = get_config_dir() / "rust-worker"
    path.mkdir(parents=True, exist_ok=True)
    return path


def default_worker_path() -> Path:
    return worker_cache_dir() / worker_binary_name()


def local_dev_worker_path() -> Optional[Path]:
    package_dir = Path(__file__).resolve().parent
    repo_root = package_dir.parent
    direct_worker = repo_root / "rust_worker" / "target" / "debug" / worker_binary_name()
    if direct_worker.exists():
        return direct_worker

    return None


def packaged_worker_resource_path() -> str:
    return f"rust/bin/{_platform_key()}/{worker_binary_name()}"


def install_packaged_worker_binary() -> Optional[Path]:
    """Copy a bundled worker binary into the writable worker cache if present."""
    try:
        worker_resource = resources.files("aicodeprep_gui").joinpath(
            packaged_worker_resource_path()
        )
        if not worker_resource.is_file():
            return None

        target = default_worker_path()
        with resources.as_file(worker_resource) as source:
            source_path = Path(source)
            if target.exists() and _sha256_file(target) == _sha256_file(source_path):
                return target

            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, target)
            if platform.system() != "Windows":
                target.chmod(target.stat().st_mode | stat.S_IXUSR |
                             stat.S_IXGRP | stat.S_IXOTH)
            return target
    except Exception as exc:
        logger.debug("Packaged Rust worker is not available: %s", exc)
        return None


def get_worker_path() -> Path:
    rust_cfg = get_section("rust_backend")
    configured = str(rust_cfg.get("worker_path", "")).strip()
    if configured:
        return Path(configured)

    cached = default_worker_path()
    if cached.exists():
        return cached

    local_dev = local_dev_worker_path()
    if local_dev is not None:
        return local_dev

    packaged = install_packaged_worker_binary()
    return packaged or cached


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


def ensure_worker_binary() -> tuple[Optional[Path], str]:
    rust_cfg = get_section("rust_backend")
    worker = get_worker_path()
    if worker.exists():
        return worker, ""

    auto_download = bool(rust_cfg.get("auto_download", False))
    download_url = str(rust_cfg.get("download_url", "")).strip()
    download_sha256 = str(rust_cfg.get("download_sha256", "")).strip()
    if auto_download and download_url:
        ok, result = download_worker_binary(download_url, download_sha256)
        if ok:
            return Path(result), ""
        return None, f"Rust worker missing and auto-download failed: {result}"

    return None, f"Rust worker not found at {worker}"


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

    worker, worker_error = ensure_worker_binary()
    if worker is None:
        return RustProcessResult(ok=False, error=worker_error)
    logger.info("Using Rust worker for context generation: %s", worker)

    request_payload = {
        "op": "pack",
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


def scan_with_rust_worker(
    root_dir: str,
    config: dict,
    respect_gitignore: bool = False,
) -> RustScanResult:
    worker, worker_error = ensure_worker_binary()
    if worker is None:
        return RustScanResult(ok=False, error=worker_error)
    logger.info("Using Rust worker for directory scan: %s", worker)

    request_payload = {
        "op": "scan",
        "root_dir": os.path.abspath(root_dir),
        "code_extensions": list(config.get("code_extensions", [])),
        "exclude_patterns": list(config.get("exclude_patterns", [])),
        "default_include_patterns": list(config.get("default_include_patterns", [])),
        "max_file_size": int(config.get("max_file_size", 1000000)),
        "respect_gitignore": bool(respect_gitignore),
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
            return RustScanResult(ok=False, error=f"Rust scan failed: {details}")

        raw = (proc.stdout or "").strip()
        if not raw:
            return RustScanResult(ok=False, error="Rust scan returned empty response")

        try:
            response = json.loads(raw)
        except json.JSONDecodeError as exc:
            return RustScanResult(ok=False, error=f"Invalid Rust scan response: {exc}")

        if not response.get("ok", False):
            return RustScanResult(ok=False, error=str(response.get("error", "Unknown Rust scan error")))

        files = []
        for item in response.get("files", []):
            abs_path = str(item.get("path", ""))
            rel_path = os.path.normpath(str(item.get("rel_path", "")))
            if abs_path and rel_path:
                files.append((abs_path, rel_path, bool(item.get("is_checked", False))))

        return RustScanResult(ok=True, files=files)
    except Exception as exc:
        logger.error("Rust scan execution error: %s", exc)
        return RustScanResult(ok=False, error=str(exc))
    finally:
        try:
            os.remove(request_path)
        except OSError:
            pass
