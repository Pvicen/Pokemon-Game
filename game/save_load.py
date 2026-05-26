from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SAVES_DIR = Path(__file__).parent.parent / "saves"


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


def load_game(slot_name: str) -> Optional[Dict[str, Any]]:
    path = _slot_path(slot_name)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def load_defeated_dict(save_data: Dict[str, Any]) -> Dict[str, List]:
    """Extracts defeated_trainers dict from save. Handles old saves (list format)."""
    dt = save_data.get("defeated_trainers", {})
    if isinstance(dt, list):
        return {"main": [tuple(p) for p in dt], "dungeon": [], "dungeon_pn": []}
    return {
        "main":       [tuple(p) for p in dt.get("main",       [])],
        "dungeon":    [tuple(p) for p in dt.get("dungeon",    [])],
        "dungeon_pn": [tuple(p) for p in dt.get("dungeon_pn", [])],
    }


def load_cleared_markers(save_data: Dict[str, Any]) -> Dict[str, List]:
    """Extracts cleared_wild_markers dict. Old saves without this key return empty lists."""
    cm = save_data.get("cleared_wild_markers", {})
    return {
        "main":       [tuple(p) for p in cm.get("main",       [])],
        "dungeon":    [tuple(p) for p in cm.get("dungeon",    [])],
        "dungeon_pn": [tuple(p) for p in cm.get("dungeon_pn", [])],
    }


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
) -> None:
    SAVES_DIR.mkdir(exist_ok=True)
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

    bag_data = {}
    if getattr(player_trainer, "bag", None) is not None:
        bag_data = dict(player_trainer.bag.counts)

    if defeated_dict is None:
        defeated_dict = {"main": [], "dungeon": [], "dungeon_pn": []}
    if cleared_markers_dict is None:
        cleared_markers_dict = {"main": [], "dungeon": [], "dungeon_pn": []}

    def _ser(entry):
        return [entry[0], entry[1], entry[2] if len(entry) > 2 else 0]

    data = {
        "slot_name": slot_name,
        "current_map": current_map,
        "steps": int(steps),
        "chapter2_unlocked": bool(chapter2_unlocked),
        "position": {"x": x, "y": y},
        "team": team_data,
        "bag": bag_data,
        "defeated_trainers": {
            "main":       [_ser(e) for e in defeated_dict.get("main",       [])],
            "dungeon":    [_ser(e) for e in defeated_dict.get("dungeon",    [])],
            "dungeon_pn": [_ser(e) for e in defeated_dict.get("dungeon_pn", [])],
        },
        "cleared_wild_markers": {
            "main":       [_ser(e) for e in cleared_markers_dict.get("main",       [])],
            "dungeon":    [_ser(e) for e in cleared_markers_dict.get("dungeon",    [])],
            "dungeon_pn": [_ser(e) for e in cleared_markers_dict.get("dungeon_pn", [])],
        },
        "pokedex": list(getattr(player_trainer, "pokedex_seen", [])),
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
            # Restore PP — old saves without "pp" key keep max PP (safe default)
            for atk_name, pp_val in p_data.get("pp", {}).items():
                if atk_name in p._pp_current:
                    p._pp_current[atk_name] = max(0, min(int(pp_val), p._pp_max.get(atk_name, 20)))
            # Restore status — old saves without these keys default to no status
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
        # Backward-compat: old saves stored list of strings
        trainer.pokedex_seen = [{"name": n, "caught": False, "level_caught": None} for n in raw_dex]
    else:
        trainer.pokedex_seen = [e for e in raw_dex if isinstance(e, dict)]
    for p in team:
        trainer.register_caught(p.name, int(getattr(p, "current_level", 1)))
    return trainer
