import json
import random
from pathlib import Path
from functools import lru_cache
from typing import Any, Dict
from .models import Pokemon, EvolvedPokemon

def determine_attack_order(p1, p2):
    if p1.speed > p2.speed:
        return p1, p2
    
    elif p2.speed > p1.speed:
        return p2, p1
    
    else:
        return tuple(random.sample([p1, p2], 2))

def _project_root():
    here = Path(__file__).resolve().parent
    
    for base_carpet in (here, here.parent, here.parent.parent):
        d = base_carpet / "data"
        if d.exists() and d.is_dir():
            return base_carpet
    raise FileNotFoundError("Data directory not found in the project structure.")

def _data_dir():
    return _project_root() / "data"


def _read_json(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
        
    except FileNotFoundError as e:
        raise FileNotFoundError(f"❌ File not found: {path.name} in {path.parent} directory.") from e
    
    except json.JSONDecodeError as e:
        raise ValueError(f"❌ Error decoding JSON from file: {path.name}. Please check the file format (line {e.lineno}, columna  {e.colno}).") from e
    

@lru_cache
def load_attacks_json() -> dict:
    
    data = _read_json(_data_dir() / "attacks.json")
    
    if not isinstance(data, dict):
        raise ValueError("❌ Invalid format in attacks.json. Expected a dict of attacks.")
    
    for key, lst in data.items():
        
        if not isinstance(lst, list):
            raise ValueError(f"❌ Invalid format for attack '{key}' in attacks.json. Expected a list of attacks.")
        
        for atk in lst:
            if not (isinstance(atk, dict) and all(k in atk for k in ("name", "type", "damage"))):
                raise ValueError(f"❌ Invalid attack format in '{key}:{atk}'.")
    
    return data

@lru_cache
def load_pokemons_json() -> list[Pokemon]:
    
    data = _read_json(_data_dir() / "pokemons.json")
    
    if not isinstance(data, dict):
        raise ValueError("❌ Invalid format in pokemons.json. Expected a dict of Pokémon.")
    attacks_map= load_attacks_json()
    
    pokemons:list[Pokemon] = []
    
    for name, attrs in data.items():
        if not isinstance(attrs, dict) or not name.strip():
            raise ValueError(f"❌ Invalid format for Pokémon '{name}' in pokemons.json. Expected a dict of attributes.")
        
        special_attacks = attacks_map.get(name, [])
        normal_attacks = attacks_map.get("Normal_attacks", [])
        pokemons.append(Pokemon(
            name=name,
            normal_attacks=normal_attacks,
            special_attacks=special_attacks,
            health=attrs.get("Health", 0),
            element_type=attrs.get("Element_type", "unknown"),
            defense=attrs.get("Defense", 0),
            special_defense=attrs.get("Special_defense", 0),
            speed=attrs.get("Speed", 0),
            evolution=attrs.get("Evolution", None),
            evolution_level=attrs.get("Evolution_level", None),
            current_level=attrs.get("Current_level", None),
        ))
    
    return pokemons


@lru_cache
def load_type_chart() -> dict:
    data = _read_json(_data_dir() / "type_effectiveness.json")
    if not isinstance(data, dict):
        raise ValueError("❌ Invalid format in type_effectiveness.json. Expected a dict of type effectiveness.")
    return data


def _Validating_Items(key: str, item: dict[str, Any]) -> Dict[str, Any]:
    
    _ALLOWED_ITEM_TYPES = {"healing", "revive", "buff"}
    _ALLOWED_TARGETS = {"ally", "enemy"}
    _ALLOWED_EFFECTS_KINDS = {"heal", "revive", "buff"}
    _ALLOWED_BUFF_STATS = {"attack", "defense", "special_defense", "special_attacks"}
    
    if not isinstance(item, dict):
        raise ValueError(f"❌ Invalid item entry for '{key}': expected object, got {type(item).__name__}")

    name = str(item.get("name")or key).strip()
    item_type = str(item.get("type", "")).strip().lower()
    target = str(item.get("target", "")).strip().lower()
    effect = item.get("effect", None)

    if not name:
        raise ValueError(f"❌ Item '{key}' is missing a 'name'.")
    if item_type not in _ALLOWED_ITEM_TYPES:
        raise ValueError(f"❌ Item '{name}' has invalid 'type': {item_type!r}. Allowed: {_ALLOWED_ITEM_TYPES}")
    if target not in _ALLOWED_TARGETS:
        raise ValueError(f"❌ Item '{name}' has invalid 'target': {target!r}. Allowed: {_ALLOWED_TARGETS}")
    if not isinstance(effect, dict):
         raise ValueError(f"❌ Item '{name}' must provide an 'effect' object.")

    kind = str(effect.get("effect", "")).strip().lower()
    if kind not in _ALLOWED_EFFECTS_KINDS:
         raise ValueError(f"❌ Item '{name}' has invalid effect.kind={kind!r}. Allowed: {_ALLOWED_EFFECTS_KINDS}")

    if item_type == "healing":
        if kind != "heal":
            raise ValueError(f"❌ Item '{name}' type=healing must use effect.kind='heal'.")
        amount = effect.get("amount", None)
        percent = effect.get("percent", None)
        if amount is None and percent is None:
            raise ValueError(f"❌ Item '{name}' (heal) 'amount' must be integer.")
        if amount is not None:
            try:
                effect["amount"] = int(amount)
            except Exception:
                 raise ValueError(f"❌ Item '{name}' (heal) 'percent' must be a float in (0.0, 1.0].")ç
        if percent is not None:
            try:
                effect["percent"] = float(percent)
                if not (0.0 < effect["percent"] <= 1.0):
                    raise ValueError
            except Exception:
                 raise ValueError(f"❌ Item '{name}' (heal) 'percent' must be a float in (0.0, 1.0].")
             
    if item_type == "revive":
        if kind != "revive":
            raise ValueError(f"❌ Item '{name}' type=revive must use effect.kind='revive'.")
        revive_hp = str(effect.get("revive_hp", "")).strip().lower()
        if revive_hp not in {"full", "half"}:
            raise ValueError(f"❌ Item '{name}' (revive) 'revive_hp' must be 'half' or 'full'.")
            
    if item_type == "buff":
        if kind != "buff":
             raise ValueError(f"❌ Item '{name}' type=buff must use effect.kind='buff'.")
        stat = str(effect.get("stat", "")).strip()
        stages = effect.get("stages", None)

        if stat not in _ALLOWED_BUFF_STATS:
            raise ValueError(
                f"❌ Item '{name}' (buff) 'stat' must be one of: {_ALLOWED_BUFF_STATS}, got {stat!r}."
            )
        try:
            effect["stages"] = int(stages)
        except Exception:
            raise ValueError(f"❌ Item '{name}' (buff) 'stages' must be integer.")
        
        battle_only =  bool(effect.get("battle_only", False))
        reusable = bool(effect.get("reusable", False))
        description = item.get("description", "")
        if description is not None:
            description = str(description)
        
        return {
            "name": name,
            "type": item_type,
            "target": target,
            "effect": effect,
            "battle_only": battle_only,
            "reusable": reusable,
            "description": description,
        } 
        
        
@lru_cache
def load_items() -> dict:
    
    data = _read_json(_data_dir() / "items.json")
    
    if not isinstance(data, dict):
        raise ValueError("❌ Invalid format in items.json. Expected a dict of items.")

    normalized: Dict[str, Dict[str, Any]] = {}
    for key, item in data.items():
        normalized[key] = _Validating_Items(key, item)
    
    return normalized