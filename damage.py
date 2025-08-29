from requests import get
from .utils import load_type_chart
import random

# Open json file
POKEMON_TYPE_EFFECTIVENESS = load_type_chart()

# ---------- helpers for temp buff stages ----------

def _stages_value(pokemon, key:str):
    if hasattr(pokemon, "_temp_buffs"):
        return getattr(pokemon, "_temp_buffs", {}).get(key, 0)
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

# ---------- effectiveness ----------

# get damage multiplier
def get_effectiveness(attacker_type: str, defender_type: str) -> float:
    type_data = POKEMON_TYPE_EFFECTIVENESS.get(attacker_type.capitalize(), {})
    multiplier = type_data.get(defender_type.capitalize(), 1.0)

    if multiplier > 1.0:
        message = "💥 ¡Special attakcs are too effective!"
    elif multiplier < 1.0:
        message = "😐 Special attacks are not at all effective..."
    else:
        message = "🔸 Special attack is normal."      
    return multiplier, message


# Get damage with element
def calculate_damage(attacker, defender, base_attack, attack_type="special"):
    buff_special = _effectiveness_base_attack(base_attack, attacker, "special_attacks")
    effectiveness, _ = get_effectiveness(attacker.element_type, defender.element_type)
    new_damage = buff_special * effectiveness
    eff_special_defense = _effectiveness_base_attack(getattr(defender, "special_defense", 0), defender, "special_defense")
    
    final_damage = max(1, int(new_damage - eff_special_defense * 0.5))
    return final_damage


# Get damage withtout element
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