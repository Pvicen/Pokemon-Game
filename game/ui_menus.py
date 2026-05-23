from __future__ import annotations

from ..trainers import Trainer


def _switch_pokemon_out_of_battle(player_trainer: Trainer) -> None:
    print("\n  Choose your active Pokémon:")
    for i, p in enumerate(player_trainer.team, start=1):
        status = "OK" if p.is_alive() else "K.O."
        active = " <- active" if i - 1 == player_trainer.active_index else ""
        print(f"    [{i}] {p.name} ({p.health}/{p.maximun_hp}) — {status}{active}")
    print("    [0] Cancel")

    choice = input("  Choose: ").strip()
    if choice == "0" or not choice.isdigit():
        return
    index = int(choice) - 1
    if not (0 <= index < len(player_trainer.team)):
        print("  ❌ Invalid.")
        return
    if index == player_trainer.active_index:
        print("  ⚠️ That Pokémon is already active.")
        return
    if not player_trainer.team[index].is_alive():
        print("  ❌ Can't set a fainted Pokémon as active.")
        return
    player_trainer.active_index = index
    print(f"  ✅ {player_trainer.team[index].name} is now active!")
    input("  Press Enter...")


def _use_item_out_of_battle(player_trainer: Trainer, bag) -> None:
    usable = bag.usable_items(in_battle=False)
    if not usable:
        print("  ❌ No usable items outside battle.")
        input("  Press Enter...")
        return

    print("\n  Your items:")
    keys = list(usable.keys())
    for i, k in enumerate(keys, start=1):
        idef = bag.get_definitions(k) or {}
        qty = usable[k]
        print(f"    [{i}] {idef.get('name', k)} x{qty} — {idef.get('description', '')}")
    print("    [0] Cancel")

    choice = input("  Choose item: ").strip()
    if choice == "0" or not choice.isdigit():
        return
    index = int(choice) - 1
    if not (0 <= index < len(keys)):
        print("  ❌ Invalid option.")
        return

    item_key = keys[index]
    idef = bag.get_definitions(item_key) or {}
    item_type = idef.get("type")

    if item_type == "revive":
        fainted = [(i, p) for i, p in enumerate(player_trainer.team) if not p.is_alive()]
        if not fainted:
            print("  ⚠️ No fainted Pokémon to revive.")
            input("  Press Enter...")
            return
        print("\n  Choose a Pokémon to revive:")
        for display, (team_idx, p) in enumerate(fainted, start=1):
            print(f"    [{display}] {p.name} (0/{p.maximun_hp} HP)")
        print("    [0] Cancel")
        c = input("  Choose: ").strip()
        if c == "0" or not c.isdigit():
            return
        pick = int(c) - 1
        if not (0 <= pick < len(fainted)):
            print("  ❌ Invalid.")
            return
        target_index = fainted[pick][0]
    else:
        healable = [(i, p) for i, p in enumerate(player_trainer.team)
                    if p.is_alive() and p.health < p.maximun_hp]
        if not healable:
            print("  ⚠️ All Pokémon are already at full health.")
            input("  Press Enter...")
            return
        print("\n  Choose a Pokémon:")
        for display, (team_idx, p) in enumerate(healable, start=1):
            print(f"    [{display}] {p.name} ({p.health}/{p.maximun_hp} HP)")
        print("    [0] Cancel")
        c = input("  Choose: ").strip()
        if c == "0" or not c.isdigit():
            return
        pick = int(c) - 1
        if not (0 <= pick < len(healable)):
            print("  ❌ Invalid.")
            return
        target_index = healable[pick][0]

    bag.use(item_key, player_trainer, in_battle=False, target_index=target_index)
    input("  Press Enter...")


def open_bag_menu(player_trainer: Trainer) -> None:
    bag = getattr(player_trainer, "bag", None)
    if bag is None:
        print("\n  No bag available.")
        input("  Press Enter...")
        return
    while True:
        print("\n  ╔══════════════════════════════╗")
        print("  ║         INVENTORY BAG        ║")
        print("  ╚══════════════════════════════╝")
        print("  [1] Use item")
        print("  [2] Switch active Pokémon")
        print("  [0] Close")
        choice = input("  Choose: ").strip()
        if choice == "0":
            return
        elif choice == "1":
            _use_item_out_of_battle(player_trainer, bag)
        elif choice == "2":
            _switch_pokemon_out_of_battle(player_trainer)
        else:
            print("  ❌ Invalid option.")
