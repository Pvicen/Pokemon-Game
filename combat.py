from __future__ import annotations

import os
from typing import Any, Dict, Optional, Tuple

from .models import Pokemon
from .damage import get_effectiveness, calculate_damage, damage_without_element
from .utils import determine_attack_order
from .inventory import Inventory
from .controllers import HumanController, IAcontroller

CLEAR_CMD = "cls" if os.name == "nt" else "clear"

def _hp_bar(pokemon: Pokemon, length: int= 20):
    hp = max(0, int(getattr(pokemon, "health", 0)))
    max_hp = max(1, int(getattr(pokemon, "maximun_hp", 1)))
    units= max(0, min(length, int(hp * length)/ max_hp))
    bar = "█" * units + " " * (length - units)
    return f"[{bar}] {hp}/{max_hp}"


def _print_status(p1: Pokemon, p2: Pokemon):
    print(f"❤️ {p1.name:12} { _hp_bar(p1) }    VS    ❤️ {p2.name:12} { _hp_bar(p2) }")
    
    
def _choose_controller(trainer, enemy_trainer) -> Dict[str, Any]:
    
    controller = getattr(trainer, "choose_action", None)
    
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
    atk_type = str(attack.get("type", "Normal")).capitalize
    base_dmg = int(attack.get("damage", 0))
    
    if atk_type == "Normal":
        dmg, hit_msg = damage_without_element(attacker, defender, base_dmg)
        eff_msg = "🔸 Normal effectiveness."
    else:
        dmg = int(calculate_damage(attacker, defender, base_dmg, attack_type = atk_type))
        eff_mult, eff_text = get_effectiveness(attacker.element_type, defender.element_type)
        eff_msg = eff_text
        
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


def _apply_switch(trainer, index: int):
    if trainer.SwitchPokemon(index):
        return f"🔄 {trainer.name} switched to {trainer.ActivePokemon.name}!"
    return f"❌ {trainer.name} failed to switch Pokémon."


def _apply_item(trainer, enemy_trainer, item_key: str):
    if not item_key:
        return "❌ No item chosen."
    ok = trainer.UseItems(item_key, enemy_trainer=enemy_trainer, in_battle=True)
    return f"🎒 Used '{item_key}'." if ok else f"❌ Could not use '{item_key}'."


def _resolve_action(actor_trainer, target_trainer, action: Dict[str, Any]):
    action_type = action.get("type", "skip")
    
    if action_type == "flee":
        actor_trainer._fled = True
        return f"🏃 {actor_trainer.name} fled the battle!"

    elif action_type == "switch":
        idx = action.get("index", None)
        if idx is None:
            return "❌ No switch index provided."
        return _apply_switch(actor_trainer, idx)
    
    elif action_type == "item":
        item_key = action.get("item", "")
        return _apply_item(item_key, actor_trainer, target_trainer)
    
    elif action_type == "attack":
        atk = action.get("attack", None)
        if atk is None:
            return "😴 No attack selected."
        dmg, msg = _apply_attack(actor_trainer.ActivePokemon, target_trainer.ActivePokemon, atk)
        target_trainer.ActivePokemon.health = max(0, target_trainer.ActivePokemon.health)
        return msg
    
    return  "...Skipped the turn"


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
        return None
    
    if not trainer.HasAvaliablePokemon():
        return None
    
    controller = getattr(trainer, "controller", None)
    
    if isinstance(controller, HumanController):
        print(f"⚠️ {trainer.name}'s {active.name} fainted!")
        
        while True:
            index = controller.choose_action(trainer)
            if index is None:
                print("❌ You must switch, cannot cancel when fainted.")
                continue
            if trainer.SwitchPokemon(index):
                return f"⚠️ {trainer.name} sends out {trainer.ActivePokemon.name}!"
            else:
                print("❌ Invalid choice, try again.")
                
    if isinstance(controller, IAcontroller):
        index = IAcontroller.BestSwitch(trainer, enemy_trainer.ActivePokemon)
        if index is not None and trainer.SwitchPokemon(index):
            return f"🤖 {trainer.name} sends out {trainer.ActivePokemon.name}!"
        return None
    
    for i, p in enumerate(trainer.team):
        alive = p.is_alive() if not callable(getattr(p, "is_alive", None)) else p.is_alive()
        if alive and i != trainer.active_index:
            trainer.active_index = i
            return f"⚠️ {trainer.name} sends out {trainer.ActivePokemon.name}!"
    
    return None

def pokemon_combat(trainer1, trainer2):
    trainer1._fled = False
    trainer2._fled = False
    turn = 1
    
    while True:
        os.system(CLEAR_CMD)
        
        end_msg = _is_battle_over(trainer1, trainer2)
        if end_msg:
            print("\n" + "=" * 60)
            print(end_msg)
            print("=" * 60 + "\n")
            break
        
        msg1 = _handle_faint_and_switch(trainer1, trainer2)
        msg2 = _handle_faint_and_switch(trainer1, trainer2)
        
        print("\n" + "=" * 60)
        print(f"🌀 TURN {turn}")
        print("=" * 60)
        
        _print_status(trainer1.ActivePokemon, trainer2.ActivePokemon)
        if msg1:
            print(msg1)
        if msg2:
            print(msg2)
            
        end_msg = _is_battle_over(trainer1, trainer2)
        if end_msg:
            print("\n" + "=" * 60)
            print(end_msg)
            print("=" * 60 + "\n")
            break
        
        first_p, second_p = determine_attack_order(trainer1.ActivePokemon, trainer2.ActivePokemon)
        if first_p is trainer1.ActivePokemon:
            first_trainer, second_trainer = trainer1, trainer2
        else:
            first_trainer, second_trainer = trainer2, trainer1
            
        action1 = _choose_controller(first_trainer, second_trainer)
        msg_first = _resolve_action(first_trainer, second_trainer, action1)
        print("\n" + msg_first)
        _print_status(first_trainer.ActivePokemon, second_trainer.ActivePokemon)
        
        end_msg = _is_battle_over(trainer1, trainer2)
        if end_msg:
            print("\n" + "=" * 60)
            print(end_msg)
            print("=" * 60 + "\n")
            break
        
        forced = _handle_faint_and_switch(second_trainer, first_trainer)
        if forced:
            print(forced)
            _print_status(first_trainer.ActivePokemon, second_trainer.ActivePokemon)
            
        action2 = _choose_controller(second_trainer, first_trainer)
        msg_second = _resolve_action(second_trainer, first_trainer, action2)
        print("\n" + msg_second)
        _print_status(first_trainer.ActivePokemon, second_trainer.ActivePokemon)
        
        input("\n🔽 End of turn. Press [ENTER] to continue...")
        turn += 1
    
    try:
        Inventory.clear_battle_state_trainers([trainer1, trainer2])
    except Exception:
        for trainer in (trainer1, trainer2):
            for pokemon in getattr(trainer, "team", []):
                if hasattr(pokemon, "_temp_buffs"):
                    try:
                        delattr(pokemon, "_temp_buffs")
                    except Exception:
                        setattr(pokemon, "_temp_buffs", {})