from __future__ import annotations

import random

from ..trainers import Trainer
from ..combat import pokemon_combat
from ..controllers import IAcontroller
from .setup_game import create_trainer_instance, get_zone_for_position, get_zone_by_id, _build_pokemon
from ..ui_common import pause


def _player_has_alive_pokemon(player_trainer: Trainer) -> bool:
    return any(p.is_alive() for p in player_trainer.team)


def _show_dialogue(name: str, lines: list) -> None:
    if not lines:
        return
    for line in lines:
        print(f"\n  {name}: \"{line}\"")
        pause("  ...")


def _give_reward(player_trainer: Trainer, reward_pool: list) -> None:
    if not reward_pool:
        return
    bag = getattr(player_trainer, "bag", None)
    if bag is None:
        return
    if isinstance(reward_pool[0], tuple):
        rewards = [r[0] for r in reward_pool]
        weights = [r[1] for r in reward_pool]
        reward = random.choices(rewards, weights=weights, k=1)[0]
    else:
        reward = random.choice(reward_pool)
    print("\n  You received:")
    for item_key, qty in reward.items():
        try:
            bag.add_items(item_key, qty)
            idef = bag.get_definitions(item_key) or {}
            item_name = idef.get("name", item_key)
            print(f"    + {item_name} x{qty}")
        except Exception:
            pass


def trigger_encounter(map_obj: dict, player_trainer: Trainer) -> bool:
    """Returns True if the encounter ended (trainer should be removed), False if skipped."""
    setup = map_obj["setup"]

    if setup.is_friendly:
        _show_dialogue(setup.name, setup.dialogue)
        _give_reward(player_trainer, setup.reward_pool)
        pause("  Press Enter to continue...")
        return True

    if not _player_has_alive_pokemon(player_trainer):
        print("\n  Your Pokemon are too exhausted to battle!")
        print("  Find a Pokemon Center to heal your team.")
        pause("  Press Enter to continue...")
        return False

    npc_trainer = create_trainer_instance(setup)
    if npc_trainer is None:
        return True

    for p in npc_trainer.team:
        player_trainer.register_seen(p.name)

    _show_dialogue(setup.name, setup.dialogue)
    print(f"\n  {setup.name} wants to battle!")
    pause("  Press Enter to start...")

    winner = pokemon_combat(player_trainer, npc_trainer, pause_between_turns=True)

    if winner is None:
        print("\n  You ran away!")
    elif winner == player_trainer.name:
        print(f"\n  {setup.defeat_message}")
        _give_reward(player_trainer, setup.reward_pool)
    else:
        print("\n  You lost... head to a Pokemon Center to heal your team.")

    pause("  Press Enter to return to map...")
    return winner == player_trainer.name


def trigger_wild_marker_encounter(marker_obj: dict, player_trainer: Trainer) -> bool:
    """Returns True to remove the marker (won or captured), False to keep it (fled or lost)."""
    name = marker_obj["name"]
    level = marker_obj["level"]

    if not _player_has_alive_pokemon(player_trainer):
        print("\n  Your Pokemon are too exhausted to battle!")
        print("  Find a Pokemon Center to heal your team.")
        pause("  Press Enter to continue...")
        return False

    from ..data_io import load_pokemons, load_attacks
    wild_pokemon = _build_pokemon(name, level, load_pokemons(), load_attacks())
    if wild_pokemon is None:
        return True

    wild_trainer = Trainer(
        name=f"Wild {name}",
        team=[wild_pokemon],
        controller=IAcontroller(),
    )

    player_trainer.register_seen(name)
    print(f"\n  A wild {name} (Lv. {level}) is blocking your path!")
    pause("  Press Enter to start...")

    winner = pokemon_combat(player_trainer, wild_trainer, pause_between_turns=True, wild=True)

    if winner == "captured":
        wild_pokemon.clear_status()
        player_trainer.register_caught(name, wild_pokemon.current_level)
        print(f"\n  {name} was added to your team!")
    elif winner is None:
        print(f"\n  You ran away from the wild {name}!")
    elif winner == player_trainer.name:
        print(f"\n  You defeated the wild {name}!")
    else:
        print(f"\n  You were defeated by the wild {name}...")

    pause("  Press Enter to return to map...")

    return winner == "captured" or winner == player_trainer.name


def trigger_wild_encounter(x: int, y: int, player_trainer: Trainer, zone_id: str = None,
                           world_id: str = "world1") -> None:
    if zone_id is None:
        zone_id = get_zone_for_position(x, y, world_id)
    if zone_id is None:
        return
    zone = get_zone_by_id(zone_id, world_id)
    if not zone or not zone.wild_pokemons:
        return

    if not _player_has_alive_pokemon(player_trainer):
        return

    if random.random() > zone.wild_encounter_chance:
        return

    weights = [e.spawn_chance for e in zone.wild_pokemons]
    entry = random.choices(zone.wild_pokemons, weights=weights, k=1)[0]
    level = random.randint(entry.min_level, entry.max_level)

    from ..data_io import load_pokemons, load_attacks
    pokemon_db = load_pokemons()
    attacks_db = load_attacks()
    wild_pokemon = _build_pokemon(entry.name, level, pokemon_db, attacks_db)
    if wild_pokemon is None:
        return

    wild_trainer = Trainer(
        name=f"Wild {entry.name}",
        team=[wild_pokemon],
        controller=IAcontroller(),
    )

    player_trainer.register_seen(entry.name)
    print(f"\n  A wild {entry.name} (Lv. {level}) appeared!")
    pause("  Press Enter to start...")

    winner = pokemon_combat(player_trainer, wild_trainer, pause_between_turns=True, wild=True)

    if winner == "captured":
        wild_pokemon.clear_status()
        player_trainer.register_caught(entry.name, wild_pokemon.current_level)
        print(f"\n  {entry.name} was added to your team!")
    elif winner is None:
        print(f"\n  You ran away from the wild {entry.name}!")
    elif winner == player_trainer.name:
        print(f"\n  You defeated the wild {entry.name}!")
    else:
        print(f"\n  You were defeated by the wild {entry.name}...")

    pause("  Press Enter to return to map...")
