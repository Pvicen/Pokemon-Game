from ..models import Pokemon, EvolvedPokemon
from ..utils import load_items, load_pokemons_json
from ..trainers import Trainer
from ..inventory import Inventory

class HumanController():
    
    def choose_action(self, trainer, enemy_trainer):
        
        while True:
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
            if option == 1:
                atk = self.ChooseAttack(trainer.ActivePokemon)
                return {"type": "attack", "attack": atk} if atk else {"type": "skip"}
                    
            elif option == 2:
                idx = self.ChooseSwitchPokemon(trainer)
                return {"type": "switch", "index": idx} if idx is not None else {"type": "skip"}
                
            # This is a placeholder for item usage logic
            elif option == 3:
                item = self.UseItem(trainer)
                return {"type": "item", "item": item} if item else {"type": "skip"}
                
            elif option == 0:
                return {"type": "flee"}
            
            else:
                print("❌ Invalid option, please choose 0-3.")
                
    
    def UseItem(self, trainer, enemy_trainer=None, in_battle: bool = True):
        bag = getattr(trainer, "bag", None)
        if bag is None:
            print("❌ No inventory available.")
            return None

        usable = bag.usable_items(in_battle=in_battle)
        if not usable:
            print("❌ No usable items.")
            return None

        print("\n🎒 Your items:")
        keys = list(usable.keys())
        for i, k in enumerate(keys, start=1):
            idef = bag.get_definitions(k) or {}
            desc = idef.get("description", "")
            quantity = usable[k]
            print(f"  [{i}] {idef.get('name', k)} x{quantity} — {desc}")
        print("  [0] Cancel")

        while True:
            choice = input("  Choose item: ").strip()
            if choice == "0":
                return None
            if not choice.isdigit():
                print("❌ Invalid input. Please enter a number.")
                continue
            index = int(choice) - 1
            if not (0 <= index < len(keys)):
                print("❌ Input out of range.")
                continue
            return keys[index]
        
        
    def SelectFirstPokemon(self, trainer, actor):
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
                
                
    @staticmethod
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
                
            choice = input("Choose your attack (number): ")
            if choice == "0":
                print("😴 You decided not to attack this turn.")
                return None
            if not choice.isdigit():
                print("❌ Invalid input, please enter a number.")
                continue
            
            index = int(choice) - 1
            if 0 <= index < len(all_attacks):
                return all_attacks[index]  
            print("❌ Invalid number, try again.")
    
    
    def ChooseSwitchPokemon(self, trainer):
        
        has_options = any(trainer.CheckPokemonSwitch(i) for i,_ in enumerate(trainer.team))
        if not has_options:
            print("🛑 No available Pokémon to switch.")
            return None
        
        print("Choose a Pokémon to switch (alive and different from the current):")
        for i, p in enumerate(trainer.team, start=1):
            status = "Ok" if p.is_alive() else "K.O"
            active = " (Active)" if i - 1 == trainer.active_index else ""
            print(f"[{i}] - {p.name} - {p.health}/{p.maximun_hp} - Status: {status}{active}")
        print("[0] - Cancel switch")
        
        while True:
            choice = input("Enter the number of the Pokémon to switch: ").strip()
            
            if choice == "0":
                return None
            
            if not choice.isdigit():
                print("❌ Invalid input, please enter a number.")
                return None
            
            index = int(choice) - 1
            if trainer.CheckPokemonSwitch(index):
                return index
            else:
                print("❌ Invalid choice. Make sure the Pokémon is alive and not the current active one.")


    def Human_turn(trainer, enemy_trainer):
        
        controller = trainer.controller or HumanController()
        action = controller.choose_action(trainer, enemy_trainer)
        return action or {"type": "skip"}