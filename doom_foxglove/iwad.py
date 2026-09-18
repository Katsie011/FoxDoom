"""Locate a legal IWAD. Freedoom or shareware only — never a commercial WAD we ship."""

from __future__ import annotations

import os
import zipfile
from pathlib import Path
from urllib.request import urlopen

REPO_ROOT = Path(__file__).resolve().parents[1]
WAD_DIR = REPO_ROOT / "wad"
FREEDOOM_ZIP_URL = (
    "https://github.com/freedoom/freedoom/releases/download/v0.13.0/freedoom-0.13.0.zip"
)


def _candidate_paths() -> list[Path]:
    env = os.environ.get("DOOM_IWAD") or os.environ.get("FREEDOOM1_WAD") or ""
    paths: list[Path] = []
    if env:
        paths.append(Path(env).expanduser())
    paths.extend(
        [
            WAD_DIR / "freedoom1.wad",
            WAD_DIR / "freedoom.wad",
            WAD_DIR / "doom1.wad",
        ]
    )
    try:
        import vizdoom

        install = Path(getattr(vizdoom, "install_path", "") or "")
        if install:
            paths.extend(
                [
                    install / "freedoom1.wad",
                    install / "freedoom2.wad",
                    install / "freedoom.wad",
                ]
            )
    except Exception:
        pass
    return paths


def find_iwad() -> Path | None:
    for path in _candidate_paths():
        if path.is_file():
            return path
    return None


def fetch_freedoom1(dest_dir: Path | None = None) -> Path:
    """Download the official Freedoom 0.13.0 zip and extract freedoom1.wad."""
    dest_dir = dest_dir or WAD_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / "freedoom1.wad"
    if target.is_file():
        return target
    zip_path = dest_dir / "freedoom-0.13.0.zip"
    if not zip_path.is_file():
        with urlopen(FREEDOOM_ZIP_URL, timeout=60) as resp:
            zip_path.write_bytes(resp.read())
    with zipfile.ZipFile(zip_path) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith("freedoom1.wad")]
        if not names:
            raise FileNotFoundError("freedoom zip did not contain freedoom1.wad")
        with zf.open(names[0]) as src, target.open("wb") as out:
            out.write(src.read())
    return target


def resolve_iwad(*, fetch: bool = False) -> Path | None:
    found = find_iwad()
    if found is not None:
        return found
    if fetch:
        try:
            return fetch_freedoom1()
        except Exception:
            return find_iwad()
    return None
