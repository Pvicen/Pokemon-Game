from ..models import Pokemon, EvolvedPokemon
from ..utils import load_items, load_pokemons_json


class HumanController():
    
    def UseItem(actor):
        
        items = load_items()
        
        print("Avaliavle items for use")
        
    def SelecPokemon(actor):
        
        initial_pokemons = load_pokemons_json()
        
        print("Hello player, Now you need choose your first pokemon thats your options")
        
        for pokemon in initial_pokemons:
            print(f"name: {pokemon['name']} type: {pokemon['type']} level: {pokemon['level']}")
            

    def ChooseAttack(actor):

        all_attacks = []
        
        if getattr(actor, "special_attacks", None):
            all_attacks.extend(list(actor.special_attacks))
            
        if getattr(actor, "normal_attacks", None):
            all_attacks.extend(list(actor.normal_attacks))
        
        if not all_attacks:
            print(f"🤖 {getattr(actor, 'name', 'Pokémon')} don’t have available attacks.")
            return None
        
        if not isinstance(atk, dict) or not all( k in atk for k in ("name", "type", "damage")):
                print("Invalid attack format")
                return None
        
        while True:
            print("\n🌀 Available attacks:")
            for i, atk in enumerate(all_attacks, start=1):
                atk_type = str(atk["type"]).capitalize()
                atk_dmg = int(atk["damage"])
                print(f"[{i}: {atk['name']} | Type: {atk_type} | Damage: {atk_dmg}")
            print("[0: Cancel] / no attack")
                
            print("\n")
                
            choice = input("Choose your attack (number): ")
            
            if choice == "0":
                print("😴 You decided not to attack this turn.")
                return None
            
            if not choice.isdigit():
                print("❌ Invalid input, please enter a number.")
                continue
            
            index = int(choice) - 1
                
            if 0 <= index < len(all_attacks):
                chosen_attack = all_attacks[index]
                return chosen_attack
            else:   
                print("❌ Invalid number, no attack executed.")
                return None


    def Human_turn(actor, target):
        
        attack = HumanController.ChooseAttack(actor)

        if not attack:
            print(f"😴 {actor.name} decided not to attack this turn.")
            return

        name = attack["name"]
        base_dmg = int(attack["damage"])
        type = str(attack["type"]).capitalize()

        print(f"\n😎 {actor.name} attacked with {name} (type: {type}, damage: {base_dmg})"  )