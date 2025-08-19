import json
import random
import os
from .models import Pokemon, EvolvedPokemon

def determine_attack_order(pokemon1, pokemon2):
    if pokemon1.speed > pokemon2.speed:
        return pokemon1, pokemon2
    
    elif pokemon2.speed > pokemon1.speed:
        return pokemon2, pokemon1
    
    else:
        return random.sample([pokemon1, pokemon2], 2)


def load_attacks_json():
    attack_path = os.path.join(os.path.dirname(__file__), "data", "attacks.json")
    with open(attack_path, "r") as file:
        return json.load(file)


def load_pokemons_json():
    data_path = os.path.join(os.path.dirname(__file__), "data", "pokemons.json")
    with open(data_path, "r") as file:
        data = json.load(file)
        
    attacks_data = load_attacks_json()

    pokemons = []
    for name, attrs in data.items():
        if not name.strip():
            continue
        
        special_attacks = attacks_data.get(name, [])
        normal_attacks = attacks_data.get("Normal_attacks", [])
        
        pokemon = Pokemon(
            name = name,
            normal_attacks = normal_attacks,
            special_attacks = special_attacks,
            health = attrs.get("Health", 0),
            element_type = attrs.get("Element_type", "unknown"),
            defense = attrs.get("Defense", 0),
            special_defense = attrs.get("Special_defense", 0),
            speed = attrs.get("Speed", 0),
            evolution = attrs.get("Evolution", None),
            evolution_level = attrs.get("Evolution_level", None),
            current_level = attrs.get("Current_level", None),
        )
        pokemons.append(pokemon)
    
    return pokemons


def load_items():
    
    items_path = os.path.join(os.path.dirname(__file__), "data", "items.json")
    with open(items_path, "r", encoding="utf-8") as file:
        items = json.load(file)

    items_dict = {}
    
    for name, effect in items.items():
        print(name, effect)
        items_dict[name] = effect

    return items_dict   
        
    