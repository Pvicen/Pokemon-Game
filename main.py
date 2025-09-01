from .data_io import load_pokemons_json, load_items, load_attacks_json, load_type_chart
from .trainers import Trainer
from .controllers import HumanController, IAcontroller
from .combat import pokemon_combat

def main():
    print("🔰 Welcome to the Pokémon Battle Arena 🔰\n")

    # Create map
    A = load_attacks_json(); P = load_pokemons_json(); T = load_type_chart(); I = load_items()
    print(isinstance(A, dict), len(P) > 0, isinstance(T, dict), isinstance(I, dict))

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
# 3) hacer combate funcional 