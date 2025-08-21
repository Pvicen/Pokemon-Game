from ..models import Pokemon, EvolvedPokemon
from ..utils import load_items, load_pokemons_json
from ..trainers import Trainer

class HumanController():
    
    def choose_action(self, trainer, enemy_trainer):
        print("\nChoose your action:")
        print("[1] - Attack")
        print("[2] - Switch Pokémon")
        print("[3] - Use Item")
        print("[0] - Flee")
        
        option = input("Enter your choice: ").strip()
        
        if not option.isdigit():
            print("❌ Invalid input, please enter a number.")
            return None
        
        option = int(option)
        if option.isdigit():
            
            if option == 1:
                atk = self.ChooseAttack(trainer.ActivePokemon)
                return {"type": "attack", "attack": atk} if atk else {"type": "skip"}
                
            elif option == 2:
                idx = self.SwitchPokemon(trainer)
                return {"type": "switch", "index": idx} if idx is not None else {"type": "skip"}
            
            # This is a placeholder for item usage logic
            # You can implement item usage logic in the Trainer class
            # and call it here.
            elif option == 3:
                item = self.UseItem(trainer)
                return {"type": "item", "item": item} if item else {"type": "skip"}
            
            elif option == 0:
                print("You chose to flee from the battle.")
                return {"type": "flee"}
                
                
            
    
    
    def UseItem(actor):
        
        items = load_items()
        
        print("Avaliavle items for use")
        
    def SelecFirstPokemon(trainer, actor):
        
        pokemons = load_pokemons_json()
        ALLOWED_POKEMONS = ["Squirtle", "Charmander", "Bulbasaur", "Pikachu"]
        initials = [p for p in pokemons if p.name in ALLOWED_POKEMONS]
        
        if not initials:
            print("No initial Pokémon available.")
            return None
        
        print("👋 ¡Hello player¡, Now you need choose your first pokemon her`s your options")
        
        for i, p in enumerate(initials, start=1):
            print(f"[{i}] -Name: {p.name} \n-Health: {p.health} \n-Element: {p.element_type}"
                  f"\n-Evolution: {p.evolution}  \nEvolution_level: {p.evolution_level}")
            
        while True:
            choice = input("Choose your Pokémon (number): ").strip()
            
            if not choice.isdigit():
                print("❌ Invalid input, please enter a number.")
                continue
            
            index = int(choice) - 1
            
            if 0 <= index < len(initials):
                chosen_pokemon = initials[index]
                print(f"\n✅ 🎉 You have chosen {chosen_pokemon.name}  (Tipo {chosen_pokemon.element_type}). ¡¡Good luck!!")
                return chosen_pokemon
            else:
                print(f"❌❌ Number out of range (1-{len(initials)}). Try again...")
                

    def ChooseAttack(actor):

        all_attacks = []
        
        if getattr(actor, "special_attacks", None):
            all_attacks.extend(list(actor.special_attacks))
            
        if getattr(actor, "normal_attacks", None):
            all_attacks.extend(list(actor.normal_attacks))
        
        if not all_attacks:
            print(f"🤖 {getattr(actor, 'name', 'Pokémon')} don’t have available attacks.")
            return None
        
        while True:
            
            print("\n🌀 Available attacks:")
            
            for i, atk in enumerate(all_attacks, start=1):
                
                if not isinstance(atk, dict) or not all( k in atk for k in ("name", "type", "damage")):
                    print("Invalid attack format")
                    return None
                
                atk_type = str(atk["type"]).capitalize()
                atk_dmg = int(atk["damage"])
                print(f"[{i}]: {atk['name']} | Type: {atk_type} | Damage: {atk_dmg}")
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
    
    
    def ChooseSwitchPokemon(self, trainer):
        
        print("Choose a Pokémon to switch (alive and different from the current):")
        for i, p in enumerate(trainer.team, start=1):
            status = "Ok" if p.is_alive() else "K.O"
            active = " (Active)" if i - 1 == trainer.active_index else ""
            print(f"[{i}] - {p.name} {active} - {p.health}/{p.maximun_hp} - Status: {status}{active}")

        choice = input("Enter the number of the Pokémon to switch: ").strip()
        
        if not choice.isdigit():
            print("❌ Invalid input, please enter a number.")
            return None
        
        index = int(choice) - 1
        return index if trainer.SwitchPokemon(index) else None

    def Human_turn(actor, target):
        
        pass