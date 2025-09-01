from __future__ import annotations

from random import sample
from functools import lru_cache
from typing import Any, Dict, Iterable, List, Tuple

from .models import Pokemon
# 👉 Importa SOLO la fachada pública de data_io (sin internos):
from data_io import (
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


def _key_ci_map(d: Dict[str, Any]) -> Dict[str, Any]:
    return {str(k).strip().lower(): v for k, v in d.items()}


def _extract_owner_attacks(attacks_data: Any, owner_name: str) -> List[Dict[str, Any]]:
    owner_key = owner_name.strip().lower()
    # Shape A: normalized with "by_owner"
    if isinstance(attacks_data, dict) and "by_owner" in attacks_data:
        by_owner = attacks_data.get("by_owner", {})
        if isinstance(by_owner, dict):
            ci = _key_ci_map(by_owner)
            maybe = ci.get(owner_key, [])
            if isinstance(maybe, list) and all(isinstance(x, dict) for x in maybe):
                return list(maybe)

    # Shape B: raw legacy grouping (keys: "Pikachu", "Normal_attacks", ...)
    if isinstance(attacks_data, dict):
        ci = _key_ci_map(attacks_data)
        maybe = ci.get(owner_key, [])
        if isinstance(maybe, list) and all(isinstance(x, dict) for x in maybe):
            return list(maybe)

    return []


def _extract_normal_attacks(attacks_data: Any) -> List[Dict[str, Any]]:
    # Shape A
    if isinstance(attacks_data, dict) and "normal" in attacks_data:
        maybe = attacks_data.get("normal", [])
        if isinstance(maybe, list) and all(isinstance(x, dict) for x in maybe):
            return list(maybe)

    # Shape B (case-insensitive key "Normal_attacks")
    if isinstance(attacks_data, dict):
        ci = _key_ci_map(attacks_data)
        maybe = ci.get("normal_attacks", [])
        if isinstance(maybe, list) and all(isinstance(x, dict) for x in maybe):
            return list(maybe)

    return []


# -------------------- Pokémon factories --------------------

def _pokemon_from_def(
    pdef: Dict[str, Any],
    *,
    special_attacks: List[Dict[str, Any]],
    normal_attacks: List[Dict[str, Any]],
) -> Pokemon:
    
    name = pdef.get("name", "Unknown")
    element_type = pdef.get("element_type", "unknown")
    # The engine capitalizes on lookup; we keep lower-case canonical type here.
    health = int(pdef.get("health", 0))
    defense = int(pdef.get("defense", 0))
    special_defense = int(pdef.get("special_defense", 0))
    speed = int(pdef.get("speed", 0))
    evolution = pdef.get("evolution", None)
    evolution_level = pdef.get("evolution_level", None)
    current_level = pdef.get("current_level", None)

    # Convert canonical lowercase element_type to Title-case if you prefer visuals
    # but your damage/get_effectiveness already handles capitalization.
    return Pokemon(
        name=name,
        element_type=element_type,
        health=health,
        normal_attacks=normal_attacks or [],
        defense=defense,
        special_defense=special_defense,
        speed=speed,
        evolution=evolution,
        evolution_level=evolution_level,
        current_level=current_level,
        special_attacks=special_attacks or [],
    )


@lru_cache
def load_pokemons_json() -> List[Pokemon]:
    pokedex = load_pokemons()        # dict[str, dict] keyed by lower name
    attacks_data = _attacks_data()   # flexible shape supported
    normal = _extract_normal_attacks(attacks_data)

    objs: List[Pokemon] = []
    for key, pdef in pokedex.items():
        # pdef['name'] keeps the nicely-cased display name (e.g., "Pikachu")
        display_name = str(pdef.get("name", key)).strip()
        specials = _extract_owner_attacks(attacks_data, display_name)
        obj = _pokemon_from_def(pdef, special_attacks=specials, normal_attacks=normal)
        objs.append(obj)
    return objs


# -------------------- Back-compat: attacks passthrough --------------------

@lru_cache
def load_attacks_json() -> Dict[str, Any]:
    return _attacks_data()