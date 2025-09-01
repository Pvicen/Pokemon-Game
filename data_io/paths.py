from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Optional

from .errors import DataPathError


# You can adapt these to your project name if you want stronger namespacing
_ENV_PROJECT_ROOT_CANDIDATES = (
    "Pokemon",
    "C:\Users\moral\Documents\Pokemon",
)
_ENV_DATA_DIR_CANDIDATES = (
    "POKEMON_GAME_DATA_DIR",
    "DATA_DIR",
)

_DEFAULT_DATA_SUBDIR = "data"

_MARKERS_DEFAULT = (
    "pyproject.toml",  # modern Python projects
    ".git",            # git repo root
    _DEFAULT_DATA_SUBDIR,  # fallback if a top-level "data" exists
)


def _read_env_path(keys: Iterable[str]) -> Optional[Path]:
    for key in keys:
        raw = os.environ.get(key)
        if not raw:
            continue
        p = Path(raw).expanduser()
        # Don't resolve before existence check to provide clearer errors
        if not p.exists():
            raise DataPathError(
                f"Environment variable {key} points to a non-existing path: {p}"
            )
        return p.resolve()
    return None


def _has_any_marker(p: Path, markers: Iterable[str]) -> bool:
    for m in markers:
        if (p / m).exists():
            return True
    return False


def _walk_up_find_root(start: Path, markers: Iterable[str]) -> Optional[Path]:
    cur = start
    # Limit the walk to avoid pathological cases; 40 is plenty for normal trees
    for _ in range(40):
        if _has_any_marker(cur, markers):
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return None


@lru_cache
def project_root(*, markers: Iterable[str] = _MARKERS_DEFAULT) -> Path:
    # 1) Env override
    env_path = _read_env_path(_ENV_PROJECT_ROOT_CANDIDATES)
    if env_path is not None:
        if not env_path.is_dir():
            raise DataPathError(f"PROJECT_ROOT must be a directory, got: {env_path}")
        return env_path

    # 2) Walk upwards from current file
    here = Path(__file__).resolve()
    pkg_root = here.parent  # data_io/
    guess = _walk_up_find_root(start=pkg_root, markers=markers)
    if guess is not None:
        return guess

    # 3) Fallback: try two levels up (…/your_pkg/)
    fallback = pkg_root.parent
    if fallback.exists():
        return fallback

    raise DataPathError(
        "Could not determine project root. "
        "Set an environment variable (e.g., POKEMON_GAME_PROJECT_ROOT) "
        "or add a marker file like 'pyproject.toml' at your repo root."
    )


@lru_cache
def data_dir() -> Path:
    # 1) Env override
    env_path = _read_env_path(_ENV_DATA_DIR_CANDIDATES)
    if env_path is not None:
        if not env_path.is_dir():
            raise DataPathError(f"DATA_DIR must be a directory, got: {env_path}")
        return env_path

    # 2) Default relative to project root
    p = project_root() / _DEFAULT_DATA_SUBDIR
    if not p.exists():
        raise DataPathError(
            f"Data directory not found: {p}\n"
            f"Create it or set POKEMON_GAME_DATA_DIR/ DATA_DIR environment variable."
        )
    if not p.is_dir():
        raise DataPathError(f"Expected a directory at: {p}")
    return p.resolve()


def ensure_data_dir(*, create: bool = False) -> Path:
    p = _read_env_path(_ENV_DATA_DIR_CANDIDATES)
    if p is None:
        p = project_root() / _DEFAULT_DATA_SUBDIR

    if p.exists():
        if not p.is_dir():
            raise DataPathError(f"Expected a directory at: {p}")
        return p.resolve()

    if create:
        p.mkdir(parents=True, exist_ok=True)
        return p.resolve()

    raise DataPathError(
        f"Data directory does not exist: {p}\n"
        f"Create it manually or call ensure_data_dir(create=True), "
        f"or set POKEMON_GAME_DATA_DIR / DATA_DIR."
    )


def set_project_root(path: Path | str) -> None:
    p = Path(path).expanduser().resolve()
    if not p.exists() or not p.is_dir():
        raise DataPathError(f"Invalid project root: {p}")
    os.environ[_ENV_PROJECT_ROOT_CANDIDATES[0]] = str(p)
    reset_cache()


def set_data_dir(path: Path | str) -> None:
    p = Path(path).expanduser().resolve()
    if not p.exists() or not p.is_dir():
        raise DataPathError(f"Invalid data dir: {p}")
    os.environ[_ENV_DATA_DIR_CANDIDATES[0]] = str(p)
    reset_cache()


def reset_cache() -> None:
    project_root.cache_clear()  # type: ignore[attr-defined]
    data_dir.cache_clear()      # type: ignore[attr-defined]