from .models import EvolvedPokemon, Pokemon
from .damage import get_effectiveness, calculate_damage
from .utils import determine_attack_order
import os

def pokemon_combat(player_pokemon, enemy_pokemon):
    
    turn = 0
    first, second = determine_attack_order(player_pokemon, enemy_pokemon)
    
    while first.is_alive() and second.is_alive():
        
        print("\n" + "=" * 40)
        print(f"🌀 TURN {turn}")
        print("=" * 40 + "\n")


        input("\n🔽 End of shift. Press [ENTERL to continue...")
        os.system("cls" if os.name == "nt" else "clear")



        turn += 1

        input("\n🔽 End of shift. Press [ENTERL to continue...")
        os.system("cls" if os.name == "nt" else "clear")

    if first.is_alive():
        print(f"\n🎉 {first.name} has won the battle!")
    elif second.is_alive():
        print(f"\n🎉 {second.name} has won the battle!")
    else:
        print("\n🤝 It's a tie! Both players have fallen...")