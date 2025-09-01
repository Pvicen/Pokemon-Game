# data_io/checks/type_effectiveness.py
from __future__ import annotations
from typing import Any
from .shared import require_type
from ..errors import DataValidationError

def validate_type_chart(raw: Any) -> None:
    require_type(raw, dict, where="type_chart")

    # Accept common keys
    matrix = raw.get("matrix") or raw.get("chart") or raw.get("effectiveness")
    if matrix is None:
        # Support bare nested dict directly as raw:
        # { "fire": {"grass": 2.0, ...}, ... }
        # If so, use the whole raw as matrix
        matrix = raw

    require_type(matrix, dict, where="type_chart.matrix")

    # Collect types
    atk_types = set(matrix.keys())
    if not atk_types:
        raise DataValidationError("type_chart: no attacking types found")

    # Cross-validate inner dicts
    for atk, inner in matrix.items():
        if not isinstance(inner, dict):
            raise DataValidationError(f"type_chart.matrix['{atk}'] must be an object mapping to defenders")
        for dtyp, mult in inner.items():
            if not isinstance(dtyp, str) or not dtyp.strip():
                raise DataValidationError(f"type_chart[{atk}] has invalid defender key: {dtyp!r}")
            if not isinstance(mult, (int, float)):
                raise DataValidationError(f"type_chart[{atk}][{dtyp}] multiplier must be number, got {type(mult).__name__}")
            if mult < 0:
                raise DataValidationError(f"type_chart[{atk}][{dtyp}] multiplier must be >= 0")

    # Optionally: check symmetry domain (defenders must be a subset of all known types)
    def_types = set()
    for inner in matrix.values():
        def_types |= set(inner.keys())
    if not def_types:
        raise DataValidationError("type_chart: no defender types found")

    # Optional strictness: require square coverage
    # (comment this out if you want to allow partial coverage)
    # for atk in atk_types:
    #     missing = def_types - set(matrix[atk].keys())
    #     if missing:
    #         raise DataValidationError(f"type_chart[{atk}] missing defenders: {sorted(missing)}")

def normalize_type_chart(raw: Any) -> dict[str, dict[str, float]]:
    # Accept same flexible input as validator
    matrix = raw.get("matrix") or raw.get("chart") or raw.get("effectiveness") if isinstance(raw, dict) else None
    if matrix is None:
        matrix = raw

    norm: dict[str, dict[str, float]] = {}
    for atk, inner in (matrix or {}).items():
        akey = str(atk).strip().lower()
        out: dict[str, float] = {}
        if isinstance(inner, dict):
            for dtyp, mult in inner.items():
                dkey = str(dtyp).strip().lower()
                out[dkey] = float(mult)
        norm[akey] = out
    return norm