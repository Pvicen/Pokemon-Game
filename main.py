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
from .trainers import Trainer
from .combat import pokemon_combat  
from .controllers import HumanController, IAcontroller

def main():
    
    print("🔰 Welcome to the Pokémon Battle Arena 🔰\n")

    

if __name__ == "__main__":
    main()

# Agregar las siguientes cosas:
# 1) Agregar el mapa interativo 
# 4) Unificar como crear los equipos como elegir los pokemons, etc.
# 5) Hacer que acepte pokemons con mas de un tipo