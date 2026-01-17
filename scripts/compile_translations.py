"""scripts/compile_translations.py

Compile existing Qt translation files (*.ts) to runtime (*.qm).

Use this when you've already edited the .ts files and just need to regenerate
.qm files for the app to load.

Run:
  uv run python scripts/compile_translations.py

Or compile a subset:
  uv run python scripts/compile_translations.py es fr zh_CN
"""

from __future__ import annotations

import sys
import subprocess
from pathlib import Path
from shutil import which
from typing import Iterable, Optional


def _find_lrelease(project_root: Path) -> Optional[Path]:
    # Prefer wrapper first (common on Windows when PySide6 is installed)
    for name in ("pyside6-lrelease", "lrelease"):
        found = which(name)
        if found:
            return Path(found)

    # Fallback: locate inside PySide6 wheel
    try:
        import PySide6  # type: ignore

        pyside_dir = Path(PySide6.__file__).resolve().parent
        candidates = []
        if sys.platform == "win32":
            candidates.extend([
                pyside_dir / "lrelease.exe",
                pyside_dir / "Qt" / "libexec" / "lrelease.exe",
            ])
        else:
            candidates.extend([
                pyside_dir / "lrelease",
                pyside_dir / "Qt" / "libexec" / "lrelease",
            ])
        for candidate in candidates:
            if candidate.exists():
                return candidate
    except Exception:
        pass

    # Legacy fallback: common venv layout
    venv_dir = project_root / ".venv"
    if sys.platform == "win32":
        legacy = venv_dir / "Lib" / "site-packages" / "PySide6" / "lrelease.exe"
    else:
        legacy = (
            venv_dir
            / "lib"
            / f"python{sys.version_info.major}.{sys.version_info.minor}"
            / "site-packages"
            / "PySide6"
            / "lrelease"
        )
    if legacy.exists():
        return legacy

    return None


def _iter_ts_files(trans_dir: Path, languages: Optional[Iterable[str]]) -> list[Path]:
    if languages:
        ts_files = [trans_dir /
                    f"aicodeprep_gui_{lang}.ts" for lang in languages]
        return [p for p in ts_files if p.exists()]

    return sorted(trans_dir.glob("aicodeprep_gui_*.ts"))


def main() -> int:
    project_root = Path(__file__).parent.parent
    trans_dir = project_root / "aicodeprep_gui" / "i18n" / "translations"

    if not trans_dir.exists():
        print(f"Translations directory not found: {trans_dir}")
        return 1

    languages = sys.argv[1:] if len(sys.argv) > 1 else None

    lrelease = _find_lrelease(project_root)
    if not lrelease:
        print("Error: could not find lrelease (or pyside6-lrelease).")
        print("Make sure PySide6 is installed and run via `uv run ...`.")
        return 1

    ts_files = _iter_ts_files(trans_dir, languages)
    if not ts_files:
        print(f"No .ts files found in: {trans_dir}")
        return 0

    failed = 0
    for ts_file in ts_files:
        qm_file = ts_file.with_suffix(".qm")
        print(f"Compiling {ts_file.name} -> {qm_file.name}...")
        result = subprocess.run(
            [str(lrelease), str(ts_file), "-qm", str(qm_file)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            failed += 1
            stderr = (result.stderr or "").strip()
            if stderr:
                print(stderr)

    if failed:
        print(f"Done with errors: {failed} file(s) failed")
        return 1

    print(f"Done. Compiled {len(ts_files)} file(s) into: {trans_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
