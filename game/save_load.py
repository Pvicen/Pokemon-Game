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


def save_game(
    player_trainer,
    x: int,
    y: int,
    defeated_positions: List[Tuple[int, int]],
    slot_name: str,
) -> None:
    SAVES_DIR.mkdir(exist_ok=True)
    team_data = []
    for p in player_trainer.team:
        team_data.append({
            "name": p.name,
            "level": int(getattr(p, "level", getattr(p, "current_level", 1))),
            "health": int(getattr(p, "health", 0)),
            "exp": int(getattr(p, "exp", 0)),
        })

    bag_data = {}
    if getattr(player_trainer, "bag", None) is not None:
        bag_data = dict(player_trainer.bag.counts)

    data = {
        "slot_name": slot_name,
        "position": {"x": x, "y": y},
        "team": team_data,
        "bag": bag_data,
        "defeated_trainers": [[pos[0], pos[1]] for pos in defeated_positions],
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

    return Trainer(name="Player", team=team, controller=HumanController(), bag=bag)
