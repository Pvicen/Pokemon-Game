from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
import os

from .models import Pokemon
from .trainers import Trainer 
from .damage import calculate_damage, get_effectiveness, damage_without_element
from .inventory import Inventory
from .controllers import HumanController, IAcontroller
from .utils import determine_attack_order


CLEAR_CMD = "cls" if os.name == "nt" else "clear"

# UI -----------------helpers---------------------

def _hp_bar(pokemon: Pokemon, length: int= 20):
    hp = max(0, int(getattr(pokemon, "health", 0)))
    max_hp = max(1, int(getattr(pokemon, "maximun_hp", 1)))
    units= max(0, min(length, int(hp * length)/ max_hp))
    bar = "█" * units + " " * (length - units)
    return f"[{bar}] {hp}/{max_hp}"


def _print_status(p1: Pokemon, p2: Pokemon):
    print(f"❤️ {p1.name:12} { _hp_bar(p1) }    VS    ❤️ {p2.name:12} { _hp_bar(p2) }")
    

def _cleanup_battle(trainer_a: Trainer, trainer_b: Trainer) -> None:
    try:
        from .inventory import Inventory  # type: ignore
        Inventory.clear_battle_state_trainers((trainer_a, trainer_b))
        return
    except Exception:
        # fallback: manual per-pokemon cleanup
        for t in (trainer_a, trainer_b):
            for p in getattr(t, "team", []):
                _clear_buffs_of(p)
    

def _clear_screen() -> None:
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def _clear_buffs_of(p: Pokemon) -> None:
    try:
        # Lazy import to avoid potential import cycles at module import time
        from .inventory import Inventory
        Inventory.clear_temp_buffs(p)
        return
    except Exception:
        # Fallback if Inventory isn't available or helper changed name
        if hasattr(p, "clear_battle_buffs"):
            p.clear_battle_buffs()
        else:
            # last-resort, keep the attribute but reset it
            try:
                delattr(p, "_temp_buffs")
            except Exception:
                setattr(p, "_temp_buffs", {})


# ---------------- Action selection ----------------
    
def _choose_action(trainer, enemy_trainer) -> Dict[str, Any]:
    
    controller = getattr(trainer, "controller", None)
    
    if controller and hasattr(controller, "choose_action"):
        return controller.choose_action(trainer, enemy_trainer) or {"type": "skip"}
    
    if controller and hasattr(controller, "IA_turn"):
        return controller.IA_turn(trainer, enemy_trainer) or {"type": "skip"}
    
    actor = trainer.ActivePokemon
    attacks = []
    if getattr(actor, "special_attacks", None):
        attacks.extend(actor.special_attacks)
    if getattr(actor, "normal_attacks", None):
        attacks.extend(actor.normal_attacks)
    if attacks:
        return {"type": "attack", "attack": attacks[0]}
    return {"type": "skip"}


def _apply_attack(attacker: Pokemon, defender: Pokemon, attack: Dict[str: Any]) -> Tuple[int, str]:
    
    if not attack or not isinstance(attack, dict):
        return 0, f"❌ {getattr(attacker, 'name', 'Pokémon')} failed to act (invalid attack)."
    
    atk_name = str(attack.get("name", "Unknown"))
    atk_type = str(attack.get("type", "Normal")).capitalize()
    base_dmg = int(attack.get("damage", 0))
    
    if atk_type == "Normal":
        dmg, hit_msg = damage_without_element(attacker, defender, base_dmg)
        eff_msg = "🔸 Normal effectiveness."
    else:
        dmg = int(calculate_damage(attacker, defender, base_dmg, attack_type = atk_type))
        _, eff_msg = get_effectiveness(attacker.element_type, defender.element_type)
        
    before = max(0, defender.health)
    defender.health = max(0, defender.health - max(0, dmg))
    after = defender.health

    msg_lines = [
        f"🗡️  {attacker.name} used {atk_name}!",
        f"   → Damage: {max(0, before - after)}",
        f"   → {eff_msg}",
        f"   → {defender.name} HP: {before} → {after}"
    ]
    return (before - after), "\n".join(msg_lines)


def _take_turn(attacker_trainer: Trainer, defender_trainer: Trainer) -> bool:
    actor = attacker_trainer.ActivePokemon
    target = defender_trainer.ActivePokemon

    if not actor.is_alive():
        # try to switch before action
        if not _handle_faint_and_switch(attacker_trainer, defender_trainer):
            return False
        actor = attacker_trainer.ActivePokemon

    action = _choose_action(attacker_trainer, defender_trainer)
    atype = action.get("type", "skip")

    if atype == "attack":
        attack = action.get("attack")
        dmg, msg = _apply_attack(actor, target, attack)
        print(msg)
        # If defender fainted, handle switch
        if not target.is_alive():
            return _handle_faint_and_switch(defender_trainer, attacker_trainer)
        return True

    elif atype == "switch":
        index = action.get("index", None)
        if index is None:
            print("↩️  Switch canceled.")
            return True
        outgoing = attacker_trainer.ActivePokemon
        ok = attacker_trainer.SwitchPokemon(int(index))
        if not ok:
            print("❌ Invalid switch.")
        else:
            _clear_buffs_of(outgoing) 
            print(f"✅ {attacker_trainer.name} will fight with {attacker_trainer.ActivePokemon.name}!")
        return True

    elif atype == "item":
        item_key = action.get("item", None)
        if item_key is None:
            print("🎒 No item used.")
            return True
        ok = attacker_trainer.UseItems(item_key, enemy_trainer=defender_trainer, in_battle=True)
        if ok:
            print(f"✨ {attacker_trainer.name} used {item_key}.")
        else:
            print(f"❌ {attacker_trainer.name} failed to use {item_key}.")
        return True

    elif atype == "flee":
        print(f"🏃 {attacker_trainer.name} fled the battle!")
        return False

    # skip / unknown
    print(f"… {attacker_trainer.name} did nothing.")
    return True


def _is_battle_over(trainer1, trainer2):
    
    if getattr(trainer1, "_fled", False):
        return f"🏁 {trainer2.name} wins! (opponent fled)"
    if getattr(trainer2, "_fled", False):
        return f"🏁 {trainer1.name} wins! (opponent fled)"
    
    has1 = trainer1.HasAvaliablePokemon()
    has2 = trainer2.HasAvaliablePokemon()
   
    if not has1 and not has2:
        return "🤝 It's a tie! Both trainers are out of usable Pokémon."
    if not has1:
        return f"🎉 {trainer2.name} wins the battle!"
    if not has2:
        return f"🎉 {trainer1.name} wins the battle!"
    return None
     
    
def _handle_faint_and_switch(trainer, enemy_trainer):
    active = trainer.ActivePokemon
    if active.is_alive():
        return True

    print(f"☠️  {active.name} fainted!")
    
    _clear_buffs_of(active)

    controller = getattr(trainer, "controller", None)

    # Human path: ask for a switch using controller API if available
    if controller and hasattr(controller, "ChooseSwitchPokemon"):
        idx = controller.ChooseSwitchPokemon(trainer)
        if idx is not None and trainer.SwitchPokemon(idx):
            return True

    # AI path: try to compute best switch using IAcontroller if available
    if controller and hasattr(controller, "BestSwitch"):
        try:
            idx = controller.BestSwitch(trainer, enemy_trainer.ActivePokemon)
            if idx is not None and trainer.SwitchPokemon(idx):
                return True
        except Exception:
            pass

    # Fallback: pick first alive different from current
    for i, p in enumerate(trainer.team):
        if i != trainer.active_index and p.is_alive():
            if trainer.SwitchPokemon(i):
                return True

    # No available Pokémon
    print(f"🏳️  {trainer.name} has no available Pokémon!")
    return False


def pokemon_combat(trainer_a, trainer_b, *, pause_between_turns:bool=False, clear_between_turns: bool=False):
    print("⚔️  BATTLE START!")
    _print_status(trainer_a)
    _print_status(trainer_b)
    print()

    # Battle loop
    round_n = 1
    while True:
        print(f"\n===== ROUND {round_n} =====")
        # Early exit if someone already lost
        if not trainer_a.HasAvaliablePokemon():
            print(f"🏆 Winner: {trainer_b.name}")
            _cleanup_battle(trainer_a, trainer_b)
            return trainer_b.name
        if not trainer_b.HasAvaliablePokemon():
            print(f"🏆 Winner: {trainer_a.name}")
            _cleanup_battle(trainer_a, trainer_b)
            return trainer_a.name

        a_first, b_second = determine_attack_order(trainer_a.ActivePokemon, trainer_b.ActivePokemon)
        # Map order to trainers
        first_trainer = trainer_a if a_first is trainer_a.ActivePokemon else trainer_b
        second_trainer = trainer_b if first_trainer is trainer_a else trainer_a

        # FIRST ACTS
        if not _take_turn(first_trainer, second_trainer):
            # someone fled or has no Pokémon
            winner = second_trainer.name if first_trainer.HasAvaliablePokemon() is False else None
            if winner is None:
                # If first ended voluntarily (flee), second is winner
                winner = second_trainer.name
            print(f"🏆 Winner: {winner}")
            _cleanup_battle(trainer_a, trainer_b)
            return winner

        # If second lost after first action, check victory:
        if not second_trainer.HasAvaliablePokemon():
            print(f"🏆 Winner: {first_trainer.name}")
            return first_trainer.name

        # SECOND ACTS
        if not _take_turn(second_trainer, first_trainer):
            winner = first_trainer.name
            print(f"🏆 Winner: {winner}")
            _cleanup_battle(trainer_a, trainer_b)
            return winner

        # Post-round status
        print("\n--- Status ---")
        _print_status(trainer_a)
        _print_status(trainer_b)

        # Optional pause (for UX when juegas a mano)
        if pause_between_turns:
            try:
                input("Press Enter to continue...")
            except KeyboardInterrupt:
                print("\n⏹️  Battle interrupted.")
                _cleanup_battle(trainer_a, trainer_b)
                return None
            
        if clear_between_turns:
            return None

        round_n += 1