from ..models import Pokemon, EvolvedPokemon
from ..utils import load_items, load_pokemons_json


class HumanController():
    
    def UseItem(actor):
        
        items = load_items()
        
        print("Avaliavle items for use")
        
    def SelecPokemon(actor):
        
        initial_pokemons = load_pokemons_json()
        option1 = initial_pokemons[2]
        option2 = initial_pokemons[4]
        option3 = initial_pokemons[6]
        print("Hello player, Now you need choose your first pokemon thats your options")
        

    def ChooseAttack(actor):

        all_attacks = list(actor.normal_attakcs) + list(actor.special_attakcs)

        for atk in all_attacks:
            if isinstance(atk, dict):
                continue

        if not atk:
            print("Attacks not avaliable")
            return

        if atk["normal"] == "normal":
            print(f"name: {atk["name"]} type: {atk["type"]} damage: {atk["damage"]}") 
        else:
            print(f"name: {atk["name"]} type: {atk["type"]} damage: {atk["damage"]}")

        