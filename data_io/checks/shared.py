from typing import Any, Iterable
from ..errors import DataValidationError


def require_type(obj: Any, expected_type: type, *, where: str) -> None:
    if not isinstance(obj, expected_type):
        raise DataValidationError(
            f"❌ {where}: expected {expected_type.__name__}, got {type(obj).__name__}"
        )


def require_keys(d: dict, required: Iterable[str], *, where: str) -> None:
    missing = [k for k in required if k not in d]
    if missing:
        raise DataValidationError(
            f"❌ {where}: missing keys {missing}. Got {list(d.keys())}"
        )


def ensure_list_of_dicts(obj: Any, *, where: str) -> list[dict]:
    if isinstance(obj, list) and all(isinstance(x, dict) for x in obj):
        return obj
    if isinstance(obj, dict):
        return [v for v in obj.values() if isinstance(v, dict)]
    raise DataValidationError(
        f"❌ {where}: must be list[dict] or dict of dicts; got {type(obj).__name__}"
    )


def normalize_string(val: Any, *, where: str, lowercase: bool = True) -> str:
    if not isinstance(val, str):
        raise DataValidationError(f"❌ {where}: expected string, got {type(val).__name__}")
    s = val.strip()
    if not s:
        raise DataValidationError(f"❌ {where}: string cannot be empty")
    return s.lower() if lowercase else s


def normalize_number(val: Any, *, where: str, min_value: float | None = None) -> float:
    if not isinstance(val, (int, float)):
        raise DataValidationError(f"❌ {where}: expected number, got {type(val).__name__}")
    f = float(val)
    if min_value is not None and f < min_value:
        raise DataValidationError(f"❌ {where}: must be >= {min_value}, got {f}")
    # Devuelve int si es entero, float si no
    return int(f) if f.is_integer() else f
