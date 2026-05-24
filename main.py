from __future__ import annotations

from .game.setup_game import create_player_trainer, choose_starter
from .game.save_load import list_saves, load_game, delete_save, restore_player_trainer, load_defeated_dict, load_cleared_markers
from .map import run_map
from .map.dungeon import run_dungeon


def _flush_kb() -> None:
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        pass


def _main_menu() -> tuple[str | None, bool]:
    """Returns (slot_name, is_new_game). slot_name is None only on error."""
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


def main():
    slot_name, is_new = _main_menu()

    player_trainer = None
    start_pos = None
    current_map = "main"
    defeated_dict        = {"main": [], "dungeon": []}
    cleared_markers_dict = {"main": [], "dungeon": []}

    if not is_new:
        save_data = load_game(slot_name)
        if save_data:
            player_trainer = restore_player_trainer(save_data)
            pos = save_data.get("position", {})
            start_pos = (pos.get("x", None), pos.get("y", None))
            defeated_dict        = load_defeated_dict(save_data)
            cleared_markers_dict = load_cleared_markers(save_data)
            current_map = save_data.get("current_map", "main")
            lead = player_trainer.team[0]
            print(f"\n  Welcome back! {lead.name} Lv.{lead.current_level} is ready.")
            _flush_kb()
            input("  Press Enter to continue...")

    if player_trainer is None:
        starter_names = choose_starter()
        player_trainer = create_player_trainer(starter_names)

    while True:
        if current_map == "main":
            result = run_map(player_trainer, start_pos=start_pos,
                             defeated_dict=defeated_dict,
                             cleared_markers_dict=cleared_markers_dict,
                             slot_name=slot_name)
        elif current_map == "dungeon":
            result = run_dungeon(player_trainer, start_pos=start_pos,
                                 defeated_dict=defeated_dict,
                                 cleared_markers_dict=cleared_markers_dict,
                                 slot_name=slot_name)
        else:
            break

        if result == "quit":
            break

        # Reload save to get authoritative position + defeated state for next map
        save_data = load_game(slot_name)
        if save_data is None:
            break
        pos = save_data.get("position", {})
        start_pos = (pos.get("x"), pos.get("y"))
        # TODO (Deuda Técnica): Refactorizar defeated_dict para que pase por referencia (mutación en RAM)
        # igual que cleared_markers_dict, evitando esta recarga redundante del disco en cada transición.
        defeated_dict = load_defeated_dict(save_data)
        current_map = save_data.get("current_map", "main")
        # cleared_markers_dict NO se recarga — ya está actualizado en RAM por referencia directa


if __name__ == "__main__":
    main()
