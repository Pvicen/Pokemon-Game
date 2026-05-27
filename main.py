from __future__ import annotations

from .game.setup_game import create_player_trainer, choose_starter
from .game.save_load import (
    list_saves, load_game, delete_save, restore_player_trainer,
    load_defeated_dict, load_cleared_markers, load_world_state,
    WORLD_IDS, WORLD2_DEFAULT_MAP, WORLD2_DEFAULT_POSITION,
)
from .map import run_map
from .map.dungeon import run_dungeon
from .map.dungeon_pn import run_dungeon_pn
from .map.world2 import run_world2_map


def _flush_kb() -> None:
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        pass


def _main_menu() -> tuple[str | None, bool]:
    saves = list_saves()

    print("\n  ╔══════════════════════════╗")
    print("  ║      POKEMON  GAME       ║")
    print("  ╚══════════════════════════╝\n")

    if saves:
        print("  Saved games:")
        for i, name in enumerate(saves, 1):
            print(f"    [{i}] {name}")
        print()
        print("  [N] New game")
        print("  [D] Delete a save")
        print()
        _flush_kb()
        choice = input("  Choose: ").strip().lower()

        if choice == "n":
            return _ask_save_name(saves), True
        if choice == "d":
            _flush_kb()
            name = input("  Save name to delete: ").strip()
            if name in saves:
                delete_save(name)
                print(f"  '{name}' deleted.")
            else:
                print("  Save not found.")
            return _main_menu()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(saves):
                return saves[idx], False
        print("  Invalid choice.")
        return _main_menu()
    else:
        print("  No saved games found.\n")
        _flush_kb()
        input("  Press Enter to start a new game...")
        return _ask_save_name([]), True


def _ask_save_name(existing: list[str]) -> str:
    _flush_kb()
    while True:
        name = input("\n  Enter a name for your save: ").strip()
        if not name:
            print("  Name cannot be empty.")
            continue
        if name in existing:
            print(f"  '{name}' already exists. Choose a different name.")
            continue
        return name


def _empty_runtime_world_state(world_id: str) -> dict:
    if world_id == "world1":
        return {
            "current_map": "main",
            "position": (None, None),
            "defeated_dict": {"main": [], "dungeon": [], "dungeon_pn": []},
            "cleared_markers_dict": {"main": [], "dungeon": [], "dungeon_pn": []},
        }
    return {
        "current_map": WORLD2_DEFAULT_MAP,
        "position": (WORLD2_DEFAULT_POSITION["x"], WORLD2_DEFAULT_POSITION["y"]),
        "defeated_dict": {"world2_main": []},
        "cleared_markers_dict": {"world2_main": []},
    }


def _load_runtime_state(save_data: dict) -> tuple[dict, dict, str, bool, bool]:
    """Returns (worlds_state, steps_dict, current_world, chapter2_unlocked, world2_completed)."""
    worlds_state = {w: _empty_runtime_world_state(w) for w in WORLD_IDS}
    for w in WORLD_IDS:
        state = load_world_state(save_data, w)
        worlds_state[w]["current_map"] = state["current_map"]
        worlds_state[w]["position"] = (state["position"].get("x"), state["position"].get("y"))
        worlds_state[w]["defeated_dict"] = load_defeated_dict(save_data, w)
        worlds_state[w]["cleared_markers_dict"] = load_cleared_markers(save_data, w)

    steps_raw = save_data.get("steps", {})
    if isinstance(steps_raw, dict):
        steps_dict = {"world1": int(steps_raw.get("world1", 0)),
                      "world2": int(steps_raw.get("world2", 0))}
    else:
        steps_dict = {"world1": int(steps_raw or 0), "world2": 0}

    current_world     = save_data.get("current_world", "world1")
    chapter2_unlocked = bool(save_data.get("chapter2_unlocked", False))
    world2_completed  = bool(save_data.get("world2_completed",  False))
    return worlds_state, steps_dict, current_world, chapter2_unlocked, world2_completed


def main():
    slot_name, is_new = _main_menu()

    player_trainer = None
    current_world  = "world1"
    chapter2_unlocked = False
    world2_completed  = False
    steps_dict   = {"world1": 0, "world2": 0}
    worlds_state = {w: _empty_runtime_world_state(w) for w in WORLD_IDS}

    if not is_new:
        save_data = load_game(slot_name)
        if save_data:
            player_trainer = restore_player_trainer(save_data)
            worlds_state, steps_dict, current_world, chapter2_unlocked, world2_completed = \
                _load_runtime_state(save_data)
            lead = player_trainer.team[0]
            print(f"\n  Welcome back! {lead.name} Lv.{lead.current_level} is ready.")
            _flush_kb()
            input("  Press Enter to continue...")

    if player_trainer is None:
        starter_names = choose_starter()
        player_trainer = create_player_trainer(starter_names)

    while True:
        state = worlds_state[current_world]
        start_pos     = state["position"]
        defeated_dict = state["defeated_dict"]
        cleared_dict  = state["cleared_markers_dict"]
        current_map   = state["current_map"]
        steps         = steps_dict[current_world]

        if current_world == "world1":
            if current_map == "main":
                result = run_map(player_trainer, start_pos=start_pos,
                                 defeated_dict=defeated_dict,
                                 cleared_markers_dict=cleared_dict,
                                 slot_name=slot_name, steps=steps,
                                 chapter2_unlocked=chapter2_unlocked)
            elif current_map == "dungeon":
                result = run_dungeon(player_trainer, start_pos=start_pos,
                                     defeated_dict=defeated_dict,
                                     cleared_markers_dict=cleared_dict,
                                     slot_name=slot_name, steps=steps)
            elif current_map == "dungeon_pn":
                result = run_dungeon_pn(player_trainer, start_pos=start_pos,
                                        defeated_dict=defeated_dict,
                                        cleared_markers_dict=cleared_dict,
                                        slot_name=slot_name, steps=steps)
            else:
                worlds_state["world1"]["current_map"] = "main"
                continue
        elif current_world == "world2":
            if current_map == "world2_main":
                result = run_world2_map(player_trainer, start_pos=start_pos,
                                        defeated_dict=defeated_dict,
                                        cleared_markers_dict=cleared_dict,
                                        slot_name=slot_name, steps=steps,
                                        chapter2_unlocked=chapter2_unlocked,
                                        world2_completed=world2_completed)
            else:
                worlds_state["world2"]["current_map"] = WORLD2_DEFAULT_MAP
                continue
        else:
            break

        if result == "quit":
            break

        # Cross-world travel
        if result == "travel_to_world2":
            current_world = "world2"
        elif result == "travel_to_world1":
            current_world = "world1"

        # Reload authoritative state from disk after every transition.
        # TODO (deuda técnica heredada): defeated_dict y cleared_markers_dict se recargan
        # del disco en cada transición. Refactor a mutación-por-referencia diferido a post-Q4.
        save_data = load_game(slot_name)
        if save_data is None:
            break
        worlds_state, steps_dict, _saved_world, chapter2_unlocked, world2_completed = \
            _load_runtime_state(save_data)
        # current_world ya está fijado por la lógica de travel; no usamos _saved_world


if __name__ == "__main__":
    main()
