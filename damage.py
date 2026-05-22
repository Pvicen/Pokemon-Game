from __future__ import annotations
import random
from typing import Tuple

from .data_io import load_type_chart

TYPE_CHART = load_type_chart()


def _stages_value(pokemon, key:str):
    if hasattr(pokemon, "_temp_buffs"):
        return int(getattr(pokemon, "_temp_buffs", {}).get(key, 0))
    return 0


def _stages_multiplier(stages: int):
    return 1.0 + 0.1 * stages


def _effectiveness_base_attack(base_attack: int, attacker, kind: str):
    stages = _stages_value(attacker, kind)
    mult = _stages_multiplier(stages)
    return max(1, int(round(base_attack * mult)))


def _effectiveness_defense(base_defense: int, defender, stat_name: str):
    stages = _stages_value(defender, stat_name)
    mult = _stages_multiplier(stages)
    return max(1, int(round(base_defense * mult)))


def _lookup_chart(attacker_type: str, defende_type: str):
    attacker = (attacker_type or "").strip()
    defender = (defende_type or "").strip()
    if not attacker or not defender:
        return 1.0
    
    attacker_l = attacker.lower()
    defender_l = defender.lower()

    row = TYPE_CHART.get(attacker_l) or TYPE_CHART.get(defender_l)
    if not isinstance(row, dict):
        return 1.0
    
    return float(row.get(defender_l, row.get(defender_l.title(), 1.0)))
    

def get_effectiveness(attacker_type: str, defender_type: str) -> Tuple[float, str]:
    mult = _lookup_chart(attacker_type, defender_type)
    if mult > 1.0:
        msg = "💥 Special attack is super effective!"
    elif mult < 1.0 and mult > 0.0:
        msg = "😐 Special attack is not very effective..."
    elif mult == 0.0:
        msg = "🛡️ It has no effect!"
    else:
        msg = "🔸 Normal effectiveness."
    return mult, msg


def calculate_damage(attacker, defender, base_attack, attack_type="special"):
    buff_special = _effectiveness_base_attack(base_attack, attacker, "special_attacks")
    effectiveness, _ = get_effectiveness(attacker.element_type, defender.element_type)
    new_damage = buff_special * effectiveness
    eff_special_defense = _effectiveness_defense(getattr(defender, "special_defense", 0), defender, "special_defense")
    return max(1, int(new_damage - eff_special_defense * 0.5))


def damage_without_element(attacker, defender, base_attack):
    buff_normal = _effectiveness_base_attack(base_attack, attacker, "normal_attacks")
    random_bonus = random.randint(-3, 3)
    eff_normal_defense = _effectiveness_defense(getattr(defender, "defense", 0), defender, "defense")
    
    raw_damage = buff_normal + random_bonus
    damage_after_defense = max(1, int(raw_damage - eff_normal_defense * 0.4))
    
    if random_bonus > 0:
        message = "💥 ¡Critical HITTTT!"
    elif random_bonus < 0:
        message = "💤 Was a weak Hit"
    else:
        message = "😐 Normal Hit"
        
    return damage_after_defense, message