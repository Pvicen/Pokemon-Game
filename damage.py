from .utils import load_type_chart
import random

# Open json file
POKEMON_TYPE_EFFECTIVENESS = load_type_chart()

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
    effectiveness, _ = get_effectiveness(attacker.element_type, defender.element_type)
    new_damage = base_attack * effectiveness
    final_damage = max(1, int(new_damage - defender.special_defense * 0.5))
    return final_damage

# Get damage withtout element
def damage_without_element(attacker, defender, base_attack):
    random_bonus = random.randint(-3, 3)
    raw_damage = base_attack + random_bonus
    damage_after_defense = max(1, int(raw_damage - defender.defense * 0.4))
    
    if random_bonus > 0:
        message = "💥 ¡Golpe crítico!"
    elif random_bonus < 0:
        message = "💤 Fue un golpe débil..."
    else:
        message = "😐 Golpe normal."
    
    return damage_after_defense, message