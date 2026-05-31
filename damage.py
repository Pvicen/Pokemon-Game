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

    # B1 fix: use ONLY the attacker's row. The previous fallback
    # (`or TYPE_CHART.get(defender_l)`) silently used the defender's row as if it
    # were the attacker's when the attacker type was missing → wrong effectiveness.
    row = TYPE_CHART.get(attacker_l)
    if not isinstance(row, dict):
        return 1.0
    
    return float(row.get(defender_l, row.get(defender_l.title(), 1.0)))
    

def get_effectiveness(attacker_type: str, defender_type: str) -> Tuple[float, str]:
    mult = _lookup_chart(attacker_type, defender_type)
    if mult > 1.0:
        msg = "💥 It's super effective!"
    elif mult < 1.0 and mult > 0.0:
        msg = "😐 It's not very effective..."
    elif mult == 0.0:
        msg = "🛡️ It has no effect!"
    else:
        msg = "🔸 Normal effectiveness."
    return mult, msg


def _level_factor(attacker) -> float:
    level = max(1, int(getattr(attacker, "current_level", 1) or 1))
    return 1.0 + (level - 1) * 0.03


def calculate_damage(attacker, defender, base_attack, attack_type="special"):
    buff_special = _effectiveness_base_attack(base_attack, attacker, "special_attacks")
    effectiveness, _ = get_effectiveness(attacker.element_type, defender.element_type)
    scaled = buff_special * effectiveness * _level_factor(attacker)
    eff_def = _effectiveness_defense(getattr(defender, "special_defense", 0), defender, "special_defense")
    defense_divisor = 1.0 + (eff_def / 100.0)
    return max(1, int(scaled / defense_divisor))


def damage_without_element(attacker, defender, base_attack):
    buff_normal = _effectiveness_base_attack(base_attack, attacker, "normal_attacks")
    scaled = buff_normal * _level_factor(attacker)
    eff_def = _effectiveness_defense(getattr(defender, "defense", 0), defender, "defense")
    defense_divisor = 1.0 + (eff_def / 100.0)
    base_damage = max(1, int(scaled / defense_divisor))

    random_bonus = random.randint(-1, 1)
    if random_bonus > 0:
        message = "Critical Hit!"
    elif random_bonus < 0:
        message = "Weak Hit"
    else:
        message = "Normal Hit"

    return max(1, base_damage + random_bonus), message