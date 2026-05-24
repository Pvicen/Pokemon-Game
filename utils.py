from __future__ import annotations

from random import sample
from functools import lru_cache
from typing import Any, Dict, Iterable, List, Tuple

from .models import Pokemon

from .data_io import (
    load_attacks,
    load_pokemons,
    load_items as _io_load_items,
    load_type_chart as _io_load_type_chart,
)


def determine_attack_order(pokemon1, pokemon2):
    s1 = getattr(pokemon1, "speed", None)
    s2 = getattr(pokemon2, "speed", None)
    if s1 is None or s2 is None:
        raise AttributeError("Both participants must have a 'speed' attribute.")

    # Paralysis halves effective speed
    if getattr(pokemon1, "status", None) == "paralysis":
        s1 = s1 // 2
    if getattr(pokemon2, "status", None) == "paralysis":
        s2 = s2 // 2

    if s1 > s2:
        return pokemon1, pokemon2
    if s2 > s1:
        return pokemon2, pokemon1
    # tie-breaker
    return tuple(sample([pokemon1, pokemon2], k=2))


def clamp(value: float | int, lo: float | int, hi: float | int):
    if lo > hi:
        lo, hi = hi, lo
    return lo if value < lo else hi if value > hi else value


@lru_cache
def load_items() -> Dict[str, Dict[str, Any]]:
    return _io_load_items()


@lru_cache
def load_type_chart() -> Dict[str, Dict[str, float]]:
    return _io_load_type_chart()


@lru_cache
def _attacks_data() -> Any:
    return load_attacks()


def _ci_map(d: Dict[str, Any]) -> Dict[str, Any]:
    return {str(k).strip().lower(): v for k, v in d.items()}


def _owner_attacks(attacks_data: Dict[str, Any], owner_name: str) -> List[Dict[str, Any]]:
    owner_key = owner_name.strip().lower()
    by_owner = attacks_data.get("by_owner", {})
    if isinstance(by_owner, dict):
        ci = _ci_map(by_owner)
        maybe = ci.get(owner_key, [])
        if isinstance(maybe, list):
            return list(maybe)
    return []

def _normal_attacks(attacks_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    normal = attacks_data.get("normal", [])
    return list(normal) if isinstance(normal, list) else []


@lru_cache
def load_pokemons_json() -> List[Pokemon]:
    pokedex = load_pokemons()        # dict[lower_name] -> canonical def
    attacks_data = _attacks_data()   # canonical from data_io
    normal = _normal_attacks(attacks_data)

    out: List[Pokemon] = []
    for key, pdef in pokedex.items():
        display_name = str(pdef.get("name", key)).strip()
        specials = _owner_attacks(attacks_data, display_name)

        obj = Pokemon(
            name=display_name,
            element_type=pdef.get("element_type", "unknown"),
            health=int(pdef.get("health", 0)),
            normal_attacks=normal or [],
            defense=int(pdef.get("defense", 0)),
            special_defense=int(pdef.get("special_defense", 0)),
            speed=int(pdef.get("speed", 0)),
            evolution=pdef.get("evolution", None),
            evolution_level=pdef.get("evolution_level", None),
            current_level=pdef.get("current_level", None),
            special_attacks=specials or [],
        )
        out.append(obj)
    return out


@lru_cache
def load_attacks_json() -> Dict[str, Any]:
    return _attacks_data()