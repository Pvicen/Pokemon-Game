from .models import Pokemon, EvolvedPokemon
from .combat import pokemon_combat
from .map import map
from .damage import get_effectiveness, calculate_damage
from .utils import load_pokemons_json


def main():
    print("🔰 Welcome to the Pokémon Battle Arena 🔰\n")

    # Create map
    
    pokemons = load_pokemons_json()
    
    player_pokemon = pokemons[1]
    enemy_pokemon = pokemons[3]
    
    # Start the battle
    pokemon_combat(player_pokemon, enemy_pokemon)
    

if __name__ == "__main__":
    main()

# Agregar las siguientes cosas:
# 1) Agregar el mapa interativo
# 2) Eleccion de pokemon a usar
# 3) Crear una historia
# 4) Crear sistema de evolucion
# 5) crear el sistema de inventario
# 6) Hacer que el enemigo ataque segun mas le convenga