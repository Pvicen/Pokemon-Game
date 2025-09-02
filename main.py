# English code
from __future__ import annotations

from .data_io import (
    load_all_data,
    load_attacks,
    load_pokemons,
    load_items,
    load_type_chart,
    DataValidationError,
    DataIOError,
    DataPathError,
)
from .models import Pokemon
from .trainers import Trainer  # si aplica
from .combat import pokemon_combat  # o la función/clase que expongas
from .controllers import HumanController, IAcontroller

def main():
    print("🔰 Welcome to the Pokémon Battle Arena 🔰\n")


    A = load_attacks(); P = load_pokemons(); T = load_type_chart(); I = load_items()
    print("DATA_IO:", isinstance(A, dict), isinstance(T, dict), isinstance(I, dict), len(P) > 0)
    
        # Example trainers
    player_team = [P[1], P[2], P[3]]
    enemy_team  = [P[4], P[5], P[6]]
    
    
    player = Trainer(name="Player", team=player_team, controller=HumanController())
    enemy  = Trainer(name="Rival",  team=enemy_team,  controller=IAcontroller())


    pokemon_combat(player, enemy)
    

if __name__ == "__main__":
    main()

# Agregar las siguientes cosas:
# 1) Agregar el mapa interativo 
# 2) Crear sistema de niveles y experiencia 
# 3) Arreglar los bugs relacionados con el combat.py
# 4) Unificar como crear los equipos como elegir los pokemons, etc.