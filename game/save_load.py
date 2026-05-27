from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SAVES_DIR = Path(__file__).parent.parent / "saves"

# Fase Q1 — multi-world save schema
SAVE_VERSION = 2
WORLD_IDS = ("world1", "world2")
WORLD_MAPS = {
    "world1": ("main", "dungeon", "dungeon_pn"),
    "world2": ("world2_main",),
}
WORLD2_DEFAULT_POSITION = {"x": 3, "y": 3}
WORLD2_DEFAULT_MAP = "world2_main"


def _slot_path(slot_name: str) -> Path:
    return SAVES_DIR / f"{slot_name}.json"


def list_saves() -> List[str]:
    if not SAVES_DIR.exists():
        return []
    return [
        f.stem
        for f in sorted(SAVES_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    ]


def has_save(slot_name: str) -> bool:
    return _slot_path(slot_name).exists()


def _empty_world_state(world_id: str) -> Dict[str, Any]:
    if world_id == "world1":
        return {
            "current_map": "main",
            "position": {"x": 20, "y": 43},
            "defeated_trainers":    {m: [] for m in WORLD_MAPS["world1"]},
            "cleared_wild_markers": {m: [] for m in WORLD_MAPS["world1"]},
        }
    return {
        "current_map": WORLD2_DEFAULT_MAP,
        "position": dict(WORLD2_DEFAULT_POSITION),
        "defeated_trainers":    {m: [] for m in WORLD_MAPS["world2"]},
        "cleared_wild_markers": {m: [] for m in WORLD_MAPS["world2"]},
    }


def _migrate_v1_to_v2(save_data: Dict[str, Any]) -> Dict[str, Any]:
    """Non-destructive in-memory migration of pre-Q1 saves to v2 schema."""
    if save_data.get("save_version", 1) >= 2:
        return save_data

    world1_state = {
        "current_map": save_data.get("current_map", "main"),
        "position":    save_data.get("position", {"x": 20, "y": 43}),
        "defeated_trainers":    save_data.get("defeated_trainers", {}) or {},
        "cleared_wild_markers": save_data.get("cleared_wild_markers", {}) or {},
    }
    # Old format with flat list of defeated_trainers
    if isinstance(world1_state["defeated_trainers"], list):
        world1_state["defeated_trainers"] = {"main": world1_state["defeated_trainers"]}
    # Ensure all world1 map keys exist
    for m in WORLD_MAPS["world1"]:
        world1_state["defeated_trainers"].setdefault(m, [])
        world1_state["cleared_wild_markers"].setdefault(m, [])

    old_steps = save_data.get("steps", 0)
    if isinstance(old_steps, dict):
        steps_dict = {"world1": int(old_steps.get("world1", 0)),
                      "world2": int(old_steps.get("world2", 0))}
    else:
        steps_dict = {"world1": int(old_steps or 0), "world2": 0}

    migrated = {
        "slot_name":         save_data.get("slot_name", ""),
        "save_version":      SAVE_VERSION,
        "current_world":     "world1",
        "chapter2_unlocked": bool(save_data.get("chapter2_unlocked", False)),
        "world2_completed":  bool(save_data.get("world2_completed", False)),
        "steps":             steps_dict,
        "team":              save_data.get("team", []),
        "bag":               save_data.get("bag", {}),
        "pokedex":           save_data.get("pokedex", []),
        "worlds": {
            "world1": world1_state,
            "world2": _empty_world_state("world2"),
        },
    }
    return migrated


def load_game(slot_name: str) -> Optional[Dict[str, Any]]:
    path = _slot_path(slot_name)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception:
        return None
    return _migrate_v1_to_v2(raw)


def load_world_state(save_data: Dict[str, Any], world_id: str) -> Dict[str, Any]:
    """Returns the per-world block (current_map, position, defeated, cleared)."""
    worlds = save_data.get("worlds", {})
    state = worlds.get(world_id)
    if not state:
        return _empty_world_state(world_id)
    # Ensure all map keys exist (forward-compat with maps added later)
    defeated = dict(state.get("defeated_trainers", {}))
    cleared  = dict(state.get("cleared_wild_markers", {}))
    for m in WORLD_MAPS.get(world_id, ()):
        defeated.setdefault(m, [])
        cleared.setdefault(m, [])
    return {
        "current_map": state.get("current_map", _empty_world_state(world_id)["current_map"]),
        "position":    state.get("position",    _empty_world_state(world_id)["position"]),
        "defeated_trainers":    defeated,
        "cleared_wild_markers": cleared,
    }


def load_defeated_dict(save_data: Dict[str, Any], world_id: str = "world1") -> Dict[str, List]:
    """Extracts defeated_trainers dict for the requested world. Returns tuples."""
    state = load_world_state(save_data, world_id)
    return {m: [tuple(p) for p in entries]
            for m, entries in state["defeated_trainers"].items()}


def load_cleared_markers(save_data: Dict[str, Any], world_id: str = "world1") -> Dict[str, List]:
    """Extracts cleared_wild_markers dict for the requested world. Returns tuples."""
    state = load_world_state(save_data, world_id)
    return {m: [tuple(p) for p in entries]
            for m, entries in state["cleared_wild_markers"].items()}


def _ser_entry(entry):
    return [entry[0], entry[1], entry[2] if len(entry) > 2 else 0]


def _ser_dict(d):
    return {k: [_ser_entry(e) for e in v] for k, v in d.items()}


def save_game(
    player_trainer,
    x: int,
    y: int,
    slot_name: str,
    *,
    current_map: str = "main",
    defeated_dict: Dict[str, List] = None,
    cleared_markers_dict: Dict[str, List] = None,
    steps: int = 0,
    chapter2_unlocked: bool = False,
    world2_completed: bool = False,
    current_world: str = "world1",
) -> None:
    """Persists the current world's state, merging with the other world's existing data.

    The caller passes the active world's state (position, defeated, cleared, steps).
    save_game reads the on-disk save (if any) to preserve the other world's data.
    """
    SAVES_DIR.mkdir(exist_ok=True)

    # Build team/bag/pokedex (global, not per-world)
    team_data = []
    for p in player_trainer.team:
        team_data.append({
            "name":        p.name,
            "level":       int(getattr(p, "level", getattr(p, "current_level", 1))),
            "health":      int(getattr(p, "health", 0)),
            "exp":         int(getattr(p, "exp", 0)),
            "pp":          dict(getattr(p, "_pp_current", {})),
            "status":      getattr(p, "status", None),
            "sleep_turns": int(getattr(p, "sleep_turns", 0)),
        })

    bag_data = dict(player_trainer.bag.counts) if getattr(player_trainer, "bag", None) else {}

    if defeated_dict is None:
        defeated_dict = {m: [] for m in WORLD_MAPS.get(current_world, ())}
    if cleared_markers_dict is None:
        cleared_markers_dict = {m: [] for m in WORLD_MAPS.get(current_world, ())}

    # Load existing save to preserve the *other* world's data
    existing = load_game(slot_name) or {}
    worlds = dict(existing.get("worlds", {}))
    for w in WORLD_IDS:
        worlds.setdefault(w, _empty_world_state(w))

    # Update active world
    worlds[current_world] = {
        "current_map": current_map,
        "position":    {"x": int(x), "y": int(y)},
        "defeated_trainers":    _ser_dict(defeated_dict),
        "cleared_wild_markers": _ser_dict(cleared_markers_dict),
    }

    # Merge steps: keep other world's count, update active world's
    existing_steps = existing.get("steps", {})
    if not isinstance(existing_steps, dict):
        existing_steps = {"world1": int(existing_steps or 0), "world2": 0}
    steps_dict = {w: int(existing_steps.get(w, 0)) for w in WORLD_IDS}
    steps_dict[current_world] = int(steps)

    data = {
        "slot_name":         slot_name,
        "save_version":      SAVE_VERSION,
        "current_world":     current_world,
        "chapter2_unlocked": bool(chapter2_unlocked or existing.get("chapter2_unlocked", False)),
        "world2_completed":  bool(world2_completed  or existing.get("world2_completed",  False)),
        "steps":             steps_dict,
        "team":              team_data,
        "bag":                bag_data,
        "pokedex":           list(getattr(player_trainer, "pokedex_seen", [])),
        "worlds":            worlds,
    }

    with open(_slot_path(slot_name), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def delete_save(slot_name: str) -> None:
    try:
        _slot_path(slot_name).unlink()
    except Exception:
        pass


def restore_player_trainer(save_data: Dict[str, Any]):
    from ..data_io import load_pokemons, load_attacks
    from ..controllers import HumanController
    from ..trainers import Trainer
    from .setup_game import _build_pokemon

    pokemon_db = load_pokemons()
    attacks_db = load_attacks()

    team = []
    for p_data in save_data.get("team", []):
        p = _build_pokemon(p_data["name"], int(p_data.get("level", 1)), pokemon_db, attacks_db)
        if p is not None:
            saved_hp = int(p_data.get("health", p.maximun_hp))
            p.health = min(max(0, saved_hp), p.maximun_hp)
            setattr(p, "exp", int(p_data.get("exp", 0)))
            for atk_name, pp_val in p_data.get("pp", {}).items():
                if atk_name in p._pp_current:
                    p._pp_current[atk_name] = max(0, min(int(pp_val), p._pp_max.get(atk_name, 20)))
            p.status = p_data.get("status", None)
            p.sleep_turns = int(p_data.get("sleep_turns", 0))
            team.append(p)

    if not team:
        from .setup_game import create_player_trainer
        return create_player_trainer()

    from ..inventory import Inventory
    bag_data = save_data.get("bag", {})
    if bag_data:
        bag = Inventory(bag_data)
    else:
        bag = Inventory({"potion": 2, "xdefense": 1})

    trainer = Trainer(name="Player", team=team, controller=HumanController(), bag=bag)
    raw_dex = save_data.get("pokedex", [])
    if raw_dex and isinstance(raw_dex[0], str):
        trainer.pokedex_seen = [{"name": n, "caught": False, "level_caught": None} for n in raw_dex]
    else:
        trainer.pokedex_seen = [e for e in raw_dex if isinstance(e, dict)]
    for p in team:
        trainer.register_caught(p.name, int(getattr(p, "current_level", 1)))
    return trainer
