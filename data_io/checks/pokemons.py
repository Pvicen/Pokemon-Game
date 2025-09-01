from __future__ import annotations

from typing import Any, Iterable, Optional
from .shared import require_type, require_keys, normalize_string, normalize_number
from ..errors import DataValidationError


# --- Configuration / schema expectations -------------------------------------

# Campos requeridos mínimos para que el Pokémon sea utilizable en tu motor actual.
_REQUIRED_FIELDS: tuple[str, ...] = (
    "Health",
    "Defense",
    "Special_defense",
    "Speed",
    "Element_type",  # admitimos también "types" como alternativa flexible (ver más abajo)
)

# Campos opcionales
_OPTIONAL_FIELDS: tuple[str, ...] = (
    "Base_attack",
    "Evolution",
    "Evolution_level",
    "Current_level",  # admitimos también "current_level"
)


def _coerce_int(value: Any, *, where: str, min_value: int = 0) -> int:
    """
    Convierte a int con validación de mínimo. Lanza DataValidationError si no es número válido.
    """
    iv = int(normalize_number(value, where=where, min_value=min_value))
    return iv


def _coerce_level(value: Any, *, where: str) -> int | str | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return _coerce_int(value, where=where, min_value=0)

    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        if s.isdigit():
            return _coerce_int(int(s), where=where, min_value=0)
        if s.lower() == "max":
            return "max"
        # Si es otra cosa (e.g., "1-2"), considéralo inválido:
        raise DataValidationError(f"❌ {where}: invalid current level value {value!r}. Expected integer or 'Max'.")

    raise DataValidationError(f"❌ {where}: unsupported type for level: {type(value).__name__}")


def _coerce_element_type(entry: dict, *, where: str) -> str:
    # Caso 1: Element_type (formato actual de tu JSON)
    if "Element_type" in entry:
        et = normalize_string(entry["Element_type"], where=f"{where}.Element_type", lowercase=True)
        return et

    # Caso 2 (opcional / futuro): lista de tipos
    if "types" in entry:
        ts = entry["types"]
        if not isinstance(ts, list) or not ts:
            raise DataValidationError(f"❌ {where}.types must be a non-empty list of strings.")
        first = normalize_string(ts[0], where=f"{where}.types[0]", lowercase=True)
        return first

    raise DataValidationError(f"❌ {where}: missing 'Element_type' (or 'types').")


def _coerce_evolution(value: Any, *, where: str) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        return s.lower()
    raise DataValidationError(f"❌ {where}: evolution must be string or empty.")


def _coerce_evolution_level(value: Any, *, where: str) -> Optional[int]:
    if value is None:
        return None
    return _coerce_int(value, where=where, min_value=0)


def _canonical_name(key: str) -> tuple[str, str]:
    raw = key.strip()
    if not raw:
        raise DataValidationError("❌ pokemons: empty key for Pokémon name.")
    return raw, raw.lower()


# --- Validator ---------------------------------------------------------------

def validate_pokemons(raw: Any) -> None:
    require_type(raw, dict, where="pokemons")

    for name, entry in raw.items():
        where = f"pokemons['{name}']"
        require_type(entry, dict, where=where)

        # Requeridos (si Element_type no está, admitimos 'types' en _coerce_element_type)
        for k in _REQUIRED_FIELDS:
            if k == "Element_type":
                # chequeo diferido en _coerce_element_type()
                continue
            if k not in entry:
                raise DataValidationError(f"❌ {where}: missing required key '{k}'.")

        # Tipos numéricos válidos:
        for num_key in ("Health", "Defense", "Special_defense", "Speed"):
            _ = _coerce_int(entry[num_key], where=f"{where}.{num_key}", min_value=0)

        # Base_attack opcional
        if "Base_attack" in entry:
            _ = _coerce_int(entry["Base_attack"], where=f"{where}.Base_attack", min_value=0)

        # Element type o types[]:
        _ = _coerce_element_type(entry, where=where)

        # Evolución opcional
        if "Evolution_level" in entry:
            _ = _coerce_evolution_level(entry.get("Evolution_level"), where=f"{where}.Evolution_level")

        # Current level (acepta Current_level o current_level)
        lvl_val = entry.get("Current_level", entry.get("current_level", None))
        if lvl_val is not None:
            _ = _coerce_level(lvl_val, where=f"{where}.Current_level")

        # Evolution opcional (cadena vacía -> None)
        if "Evolution" in entry:
            _ = _coerce_evolution(entry.get("Evolution"), where=f"{where}.Evolution")


# --- Normalizer --------------------------------------------------------------

def normalize_pokemons(raw: Any) -> dict[str, dict]:
    validate_pokemons(raw)  # asegúrate de validar antes de normalizar

    norm: dict[str, dict] = {}
    for name, entry in raw.items():
        where = f"pokemons['{name}']"
        raw_name, key = _canonical_name(name)

        health = _coerce_int(entry["Health"], where=f"{where}.Health", min_value=0)
        defense = _coerce_int(entry["Defense"], where=f"{where}.Defense", min_value=0)
        sp_def = _coerce_int(entry["Special_defense"], where=f"{where}.Special_defense", min_value=0)
        speed = _coerce_int(entry["Speed"], where=f"{where}.Speed", min_value=0)

        base_attack = entry.get("Base_attack", 0)
        if base_attack is None:
            base_attack = 0
        else:
            base_attack = _coerce_int(base_attack, where=f"{where}.Base_attack", min_value=0)

        element_type = _coerce_element_type(entry, where=where)

        evolution = _coerce_evolution(entry.get("Evolution"), where=f"{where}.Evolution")
        evolution_level = _coerce_evolution_level(entry.get("Evolution_level"), where=f"{where}.Evolution_level")

        curr_level_val = entry.get("Current_level", entry.get("current_level", None))
        current_level = _coerce_level(curr_level_val, where=f"{where}.Current_level") if curr_level_val is not None else None

        norm[key] = {
            "name": raw_name,
            "element_type": element_type,   # minúsculas; tu damage.py capitaliza internamente al consultar tabla
            "health": health,
            "defense": defense,
            "special_defense": sp_def,
            "speed": speed,
            "base_attack": base_attack,
            "evolution": evolution,         # None si vacío
            "evolution_level": evolution_level,
            "current_level": current_level,
            # Hooks para etapas posteriores (no poblamos aquí):
            # "special_attacks": [],
            # "normal_attacks": [],
        }

    return norm