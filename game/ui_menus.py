from __future__ import annotations

from ..trainers import Trainer
from ..data_io import load_pokemons, load_attacks


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


def _pokedex_detail(pokemon_name: str, pokemon_db: dict, attacks_db: dict, captured: bool) -> None:
    data = pokemon_db.get(pokemon_name, {})
    star = "★ " if captured else "  "
    display_name = data.get("name", pokemon_name)
    type_str = data.get("element_type", "???").capitalize()
    evo = data.get("evolution")
    evo_lvl = data.get("evolution_level")
    hp   = data.get("health", "?")
    atk  = data.get("base_attack", "?")
    df   = data.get("defense", "?")
    spd  = data.get("speed", "?")
    spdf = data.get("special_defense", "?")
    print("\n  ╔══════════════════════════════════════════╗")
    print(f"  ║  {star}{display_name:<16} — {type_str:<22}║")
    print("  ╠══════════════════════════════════════════╣")
    print(f"  ║  HP: {hp:<4} ATK: {atk:<4} DEF: {df:<4} SPD: {spd:<4}   ║")
    print(f"  ║  SP.DEF: {spdf:<4}                              ║")
    if evo and evo_lvl:
        evo_display = evo.capitalize()
        print(f"  ║  Evolves into: {evo_display:<10} (Lv {evo_lvl:<3})          ║")
    else:
        print(f"  ║  Does not evolve                          ║")
    attacks = attacks_db.get("by_owner", {}).get(pokemon_name, [])
    if attacks:
        print("  ║  Attacks:                                 ║")
        for atk_entry in attacks[:4]:
            aname = atk_entry.get("name", "?")
            atype = atk_entry.get("type", "?").capitalize()
            admg  = atk_entry.get("damage", "?")
            print(f"  ║    {aname:<18} {atype:<10} {admg:>3} dmg  ║")
    print("  ╚══════════════════════════════════════════╝")
    input("  Press Enter to go back...")


def open_pokedex(player_trainer: Trainer) -> None:
    pokemon_db = load_pokemons()
    attacks_db = load_attacks()
    all_names = list(pokemon_db.keys())
    seen = {n.lower() for n in getattr(player_trainer, "pokedex_seen", [])}
    total = len(all_names)

    while True:
        captured_count = sum(1 for n in all_names if n in seen)
        print(f"\n  ╔══════════════════════════════════════════╗")
        print(f"  ║     POKÉDEX  ({captured_count} captured / {total}){'':>15}║")
        print(f"  ╠══════════════════════════════════════════╣")
        for i, name in enumerate(all_names, start=1):
            star = "★" if name in seen else " "
            data = pokemon_db.get(name, {})
            display_name = data.get("name", name)
            ptype = data.get("element_type", "???").capitalize()
            lvl_val = data.get("current_level")
            if lvl_val is None:
                lvl_str = "  ?"
            elif str(lvl_val).lower() == "max":
                lvl_str = "Max"
            else:
                lvl_str = f"Lv {lvl_val}"
            print(f"  ║  [{i:>2}] {star} {display_name:<16} {ptype:<12} {lvl_str:<5}  ║")
        print(f"  ╚══════════════════════════════════════════╝")
        choice = input("  Enter number for detail, [0] to exit: ").strip()
        if choice == "0" or not choice.isdigit():
            return
        idx = int(choice) - 1
        if not (0 <= idx < total):
            print("  Invalid number.")
            continue
        name = all_names[idx]
        _pokedex_detail(name, pokemon_db, attacks_db, captured=(name in seen))


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
