from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Optional

from .paths import data_dir
from .errors import DataIOError, DataPathError, DataValidationError


# ---------- small helpers ----------

def _shorten(text: str, max_len: int = 300) -> str:
    s = " ".join(text.split())  # collapse whitespace
    if len(s) <= max_len:
        return s
    return s[: max_len - 3] + "..."

def _check_exists(p: Path) -> None:
    if not p.exists():
        raise DataPathError(f"File not found: {p}")
    if not p.is_file():
        raise DataPathError(f"Expected a file, got directory: {p}")

def _resolve_in_data(subpath: str | os.PathLike[str]) -> Path:
    base = data_dir()
    p = (base / Path(subpath)).resolve()
    # Security guard: keep inside data_dir
    if not str(p).startswith(str(base.resolve())):
        raise DataPathError(f"Refusing to escape data dir. Resolved: {p}, base: {base}")
    return p


# ---------- core reading primitives ----------

def read_text(path: Path, *, encoding: str = "utf-8") -> str:
    _check_exists(path)
    try:
        with path.open("r", encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError as e:
        raise DataIOError(f"Failed to decode file as {encoding}: {path}\n{e}") from e
    except OSError as e:
        raise DataIOError(f"I/O error reading file: {path}\n{e}") from e


def read_json(path: Path, *, encoding: str = "utf-8") -> Any:
    raw = read_text(path, encoding=encoding)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        preview = _shorten(raw)
        raise DataIOError(
            f"Invalid JSON: {path}\n"
            f"At line {e.lineno}, column {e.colno}: {e.msg}\n"
            f"Preview: {preview}"
        ) from e


@lru_cache
def read_json_cached(path: Path) -> Any:
    return read_json(path)


# ---------- convenience for paths under data/ ----------

def read_json_from_data(rel_path: str) -> Any:
    p = _resolve_in_data(rel_path)
    return read_json(p)

def read_json_from_data_cached(rel_path: str) -> Any:
    p = _resolve_in_data(rel_path)
    return read_json_cached(p)


# ---------- high-level orchestration ----------

ValidatorFn = Callable[[Any], None]
NormalizerFn = Callable[[Any], Any]

def load_dataset(
    rel_path: str,
    *,
    validator: Optional[ValidatorFn] = None,
    normalizer: Optional[NormalizerFn] = None,
    use_cache: bool = True,
) -> Any:
    
    try:
        raw = (
            read_json_from_data_cached(rel_path)
            if use_cache
            else read_json_from_data(rel_path)
        )
    except (DataPathError, DataIOError):
        # bubble up with full context
        raise

    if validator is not None:
        try:
            validator(raw)
        except DataValidationError:
            raise
        except Exception as e:
            # Ensure unexpected exceptions in validators are surfaced as DataValidationError
            raise DataValidationError(
                f"Validator raised an unexpected error for {rel_path}: {e}"
            ) from e

    if normalizer is not None:
        try:
            return normalizer(raw)
        except Exception as e:
            # Normalizers should not mutate input irreversibly; if they fail, we wrap
            raise DataIOError(
                f"Normalizer failed for {rel_path}: {e}"
            ) from e

    return raw