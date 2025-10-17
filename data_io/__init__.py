from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

# 1) Core public pieces from sibling modules
from .errors import DataPathError, DataValidationError, DataIOError
from .paths import data_dir
from .loaders import load_dataset

# 2) Validators & normalizers from the checks/ subpackage
from .checks.attacks import validate_attacks, normalize_attacks
from .checks.pokemons import validate_pokemons, normalize_pokemons
from .checks.items import validate_items, normalize_items
from .checks.type_effectiveness import validate_type_chart, normalize_type_chart


# 3) High-level loaders that apply validator + normalizer via load_dataset
def load_attacks() -> dict:
    return load_dataset(
        "attacks.json",
        validator=validate_attacks,
        normalizer=normalize_attacks,
        use_cache=True,
    )


def load_pokemons() -> dict:
    return load_dataset(
        "pokemons.json",
        validator=validate_pokemons,
        normalizer=normalize_pokemons,
        use_cache=True,
    )


def load_items() -> dict:
    return load_dataset(
        "items.json",
        validator=validate_items,
        normalizer=normalize_items,
        use_cache=True,
    )


def load_type_chart() -> dict:
    return load_dataset(
        "type_effectiveness.json",
        validator=validate_type_chart,
        normalizer=normalize_type_chart,
        use_cache=True,
    )


def load_all_data() -> dict:
    return {
        "attacks": load_attacks(),
        "pokemons": load_pokemons(),
        "items": load_items(),
        "type_chart": load_type_chart(),
    }


# 4) Backward-compatibility shims (optional but helpful):
#    If your codebase used old names like `*_json` or `*_schema`,
#    provide thin wrappers that warn once and call the new functions.
def _deprecate(old: str, new: str) -> None:
    warnings.warn(
        f"`{old}` is deprecated; use `{new}` instead.",
        DeprecationWarning,
        stacklevel=2,
    )


def load_attacks_json() -> dict:
    _deprecate("load_attacks_json", "load_attacks")
    return load_attacks()


def load_pokemons_json() -> dict:
    _deprecate("load_pokemons_json", "load_pokemons")
    return load_pokemons()


def load_items_json() -> dict:
    _deprecate("load_items_json", "load_items")
    return load_items()


def load_type_chart_json() -> dict:
    _deprecate("load_type_chart_json", "load_type_chart")
    return load_type_chart()


# Aliases for "schema" naming, if these appeared elsewhere
def validate_pokemon_schema(*args, **kwargs):
    _deprecate("validate_pokemon_schema", "validate_pokemons")
    return validate_pokemons(*args, **kwargs)


def validate_attacks_schema(*args, **kwargs):
    _deprecate("validate_attacks_schema", "validate_attacks")
    return validate_attacks(*args, **kwargs)


def validate_items_schema(*args, **kwargs):
    _deprecate("validate_items_schema", "validate_items")
    return validate_items(*args, **kwargs)


def validate_type_chart_schema(*args, **kwargs):
    _deprecate("validate_type_chart_schema", "validate_type_chart")
    return validate_type_chart(*args, **kwargs)


try:
    from .errors import MalformedJSONError  # type: ignore
except Exception:
    class MalformedJSONError(Exception):
        pass

try:
    from .errors import FileNotFoundInDataDir  # type: ignore
except Exception:
    class FileNotFoundInDataDir(FileNotFoundError):  # fallback
        pass


# 5) Public surface
__all__ = [
    # High-level loaders
    "load_attacks",
    "load_pokemons",
    "load_items",
    "load_type_chart",
    "load_all_data",
    # Low-level building block
    "load_dataset",
    # Paths helper
    "data_dir",
    # Validators & normalizers
    "validate_attacks",
    "normalize_attacks",
    "validate_pokemons",
    "normalize_pokemons",
    "validate_items",
    "normalize_items",
    "validate_type_chart",
    "normalize_type_chart",
    # Errors
    "DataPathError",
    "DataValidationError",
    "DataIOError",
    "MalformedJSONError",
    "FileNotFoundInDataDir",
    # Back-compat aliases (you may remove them later)
    "load_attacks_json",
    "load_pokemons_json",
    "load_items_json",
    "load_type_chart_json",
    "validate_pokemon_schema",
    "validate_attacks_schema",
    "validate_items_schema",
    "validate_type_chart_schema",
]