from __future__ import annotations

from ..trainers import Trainer
from ..data_io import load_pokemons, load_attacks
from .ui_utils import _hp_bar
from ..ui_common import pause, pick_pokemon

_CATEGORY_ORDER  = ["healing", "revive", "buff", "capture", "evolution"]
_CATEGORY_LABELS = {
    "healing":   "Healing",
    "revive":    "Restore",
    "buff":      "Battle Items",
    "capture":   "Poké Balls",
    "evolution": "Evolution Stones",
}


def _switch_active_line(idx: int, p) -> str:
    status = "K.O." if not p.is_alive() else "OK"
    lv_str = f"Lv.{getattr(p, 'current_level', '?')}"
    bar    = _hp_bar(p, length=12)
    return f"{p.name:<10} {lv_str:<6}  {bar}  {status}"


def _switch_pokemon_out_of_battle(player_trainer: Trainer) -> None:
    def _fmt(idx, p):
        active = "  <- active" if idx == player_trainer.active_index else ""
        return _switch_active_line(idx, p) + active

    index = pick_pokemon(
        list(enumerate(player_trainer.team)),
        title="\n  Choose your active Pokémon:",
        formatter=_fmt,
    )
    if index is None:
        return
    if index == player_trainer.active_index:
        print("  ⚠️ That Pokémon is already active.")
        return
    if not player_trainer.team[index].is_alive():
        print("  ❌ Can't set a fainted Pokémon as active.")
        return
    player_trainer.active_index = index
    print(f"  ✅ {player_trainer.team[index].name} is now active!")
    pause("  Press Enter...")


def _use_item_out_of_battle(player_trainer: Trainer, bag) -> None:
    usable = bag.usable_items(in_battle=False)
    if not usable:
        print("  ❌ No usable items outside battle.")
        pause("  Press Enter...")
        return

    grouped: dict = {}
    for k in usable.keys():
        idef = bag.get_definitions(k) or {}
        cat  = idef.get("type", "other")
        grouped.setdefault(cat, []).append(k)
    cats_sorted = sorted(
        grouped.keys(),
        key=lambda c: _CATEGORY_ORDER.index(c) if c in _CATEGORY_ORDER else len(_CATEGORY_ORDER),
    )
    print("\n  Your items:")
    keys: list = []
    for cat in cats_sorted:
        label = _CATEGORY_LABELS.get(cat, cat.capitalize())
        print(f"\n    -- {label} --")
        for k in grouped[cat]:
            idef = bag.get_definitions(k) or {}
            qty  = usable[k]
            idx  = len(keys) + 1
            keys.append(k)
            print(f"    [{idx}] {idef.get('name', k)} x{qty} — {idef.get('description', '')}")
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

    # All three item families share the same flow: filter the team to the
    # valid targets, bail with a message if none qualify, then ask which one.
    # Only the filter, the heading and the per-row text differ.
    if item_type == "revive":
        candidates = [(i, p) for i, p in enumerate(player_trainer.team) if not p.is_alive()]
        empty_msg  = "  ⚠️ No fainted Pokémon to revive."
        title      = "\n  Choose a Pokémon to revive:"
        row        = lambda idx, p: f"{p.name} (0/{p.maximun_hp} HP)"
    elif item_type == "evolution":
        candidates = [(i, p) for i, p in enumerate(player_trainer.team) if p.is_alive()]
        empty_msg  = "  ⚠️ All Pokémon are fainted."
        title      = "\n  Choose a Pokémon to use the stone on:"
        row        = lambda idx, p: f"{p.name} Lv.{getattr(p, 'current_level', '?')} ({p.health}/{p.maximun_hp} HP)"
    else:
        candidates = [(i, p) for i, p in enumerate(player_trainer.team)
                      if p.is_alive() and p.health < p.maximun_hp]
        empty_msg  = "  ⚠️ All Pokémon are already at full health."
        title      = "\n  Choose a Pokémon:"
        row        = lambda idx, p: f"{p.name} ({p.health}/{p.maximun_hp} HP)"

    if not candidates:
        print(empty_msg)
        pause("  Press Enter...")
        return

    target_index = pick_pokemon(candidates, title=title, formatter=row)
    if target_index is None:
        return

    # Strict confirmation before consuming an irreversible item (evolution stones).
    if item_type == "evolution":
        target    = player_trainer.team[target_index]
        item_name = idef.get("name", item_key)
        print("\n  ⚠️  Evolution stones are used up permanently and cannot be undone.")
        confirm = input(f"  Use {item_name} on {target.name}? [y/N]: ").strip().lower()
        if confirm not in ("y", "yes"):
            print("  Cancelled — the stone was not used.")
            pause("  Press Enter...")
            return

    bag.use(item_key, player_trainer, in_battle=False, target_index=target_index)
    pause("  Press Enter...")


def _pokedex_detail(pokemon_name: str, pokemon_db: dict, attacks_db: dict, entry: dict | None = None) -> None:
    data = pokemon_db.get(pokemon_name, {})
    caught = entry.get("caught", False) if entry else False
    level_caught = entry.get("level_caught") if entry else None
    if caught:
        star = "★ "
    elif entry:
        star = "◆ "
    else:
        star = "  "
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
    if caught and level_caught is not None:
        print(f"  ║  Caught at Lv. {level_caught:<4}                         ║")
    elif entry:
        print(f"  ║  Seen (not yet caught)                    ║")
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
    pause("  Press Enter to go back...")


def open_pokedex(player_trainer: Trainer) -> None:
    pokemon_db = load_pokemons()
    attacks_db = load_attacks()
    all_names = list(pokemon_db.keys())
    total = len(all_names)

    raw_dex = getattr(player_trainer, "pokedex_seen", [])
    dex_lookup: dict[str, dict] = {}
    for e in raw_dex:
        if isinstance(e, dict):
            dex_lookup[e["name"].lower()] = e
        else:
            dex_lookup[str(e).lower()] = {"name": str(e), "caught": False, "level_caught": None}

    while True:
        caught_count = sum(1 for e in dex_lookup.values() if e.get("caught"))
        seen_count   = len(dex_lookup)
        print(f"\n  ╔══════════════════════════════════════════╗")
        print(f"  ║  POKÉDEX  {caught_count}★ caught  {seen_count}◆ seen / {total}{'':>6}║")
        print(f"  ╠══════════════════════════════════════════╣")
        for i, name in enumerate(all_names, start=1):
            entry = dex_lookup.get(name)
            if entry and entry.get("caught"):
                symbol = "★"
            elif entry:
                symbol = "◆"
            else:
                symbol = " "
            data = pokemon_db.get(name, {})
            display_name = data.get("name", name)
            ptype = data.get("element_type", "???").capitalize()
            if entry and entry.get("caught") and entry.get("level_caught") is not None:
                lvl_str = f"Lv{entry['level_caught']}"
            else:
                lvl_str = "  ?"
            print(f"  ║  [{i:>2}] {symbol} {display_name:<16} {ptype:<12} {lvl_str:<5}  ║")
        print(f"  ╚══════════════════════════════════════════╝")
        choice = input("  Enter number for detail, [0] to exit: ").strip()
        if choice == "0" or not choice.isdigit():
            return
        idx = int(choice) - 1
        if not (0 <= idx < total):
            print("  Invalid number.")
            continue
        name = all_names[idx]
        _pokedex_detail(name, pokemon_db, attacks_db, entry=dex_lookup.get(name))


def show_team_summary(player_trainer: Trainer) -> None:
    print("\n  ╔══════════════════════════════╗")
    print("  ║         YOUR TEAM            ║")
    print("  ╚══════════════════════════════╝")
    for i, p in enumerate(player_trainer.team):
        status = "K.O." if not p.is_alive() else "OK"
        active = "  <- active" if i == player_trainer.active_index else ""
        lv_str = f"Lv.{getattr(p, 'current_level', '?')}"
        bar    = _hp_bar(p, length=12)
        print(f"  [{i+1}] {p.name:<10} {lv_str:<6}  {bar}  {status}{active}")
    pause("\n  Press Enter to continue...")


def open_bag_menu(player_trainer: Trainer) -> None:
    bag = getattr(player_trainer, "bag", None)
    if bag is None:
        print("\n  No bag available.")
        pause("  Press Enter...")
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
