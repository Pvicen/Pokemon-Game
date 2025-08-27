from .models import Pokemon, EvolvedPokemon
from .combat import pokemon_combat
from .map import map
from .damage import get_effectiveness, calculate_damage
from .utils import load_attacks_json, load_pokemons, load_type_chart, load_items


def main():
    print("🔰 Welcome to the Pokémon Battle Arena 🔰\n")

    # Create map
    A = load_attacks_json(); P = load_pokemons(); T = load_type_chart(); I = load_items()
    print(isinstance(A, dict), len(P) > 0, isinstance(T, dict), isinstance(I, dict))
    
    pokemons = load_pokemons()
    
    player_pokemon = pokemons[1]
    enemy_pokemon = pokemons[3]
    
    # Start the battle
    pokemon_combat(player_pokemon, enemy_pokemon)
    

if __name__ == "__main__":
    main()

# Agregar las siguientes cosas:
# 1) Agregar el mapa interativo 
# 2) Crear sistema de niveles y experiencia 
# 3) hacer combate funcional 