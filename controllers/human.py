from ..models import Pokemon
from ..utils import load_items, load_pokemons_json
from ..trainers import Trainer
from ..inventory import Inventory
from ..game.ui_utils import _hp_bar

class HumanController():
    
    def choose_action(self, trainer, enemy_trainer, is_wild: bool = False):

        while True:
            print("\nChoose your action:")
            print("[1] - Attack")
            print("[2] - Switch Pokémon")
            print("[3] - Use Item")
            if is_wild:
                print("[4] - Throw Pokéball")
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

            elif option == 3:
                result = self.UseItem(trainer)
                if result is None:
                    return {"type": "skip"}
                item_key, target_index = result
                return {"type": "item", "item": item_key, "target_index": target_index}

            elif option == 4 and is_wild:
                return self._choose_ball(trainer)

            elif option == 0:
                return {"type": "flee"}

            else:
                max_opt = 4 if is_wild else 3
                print(f"❌ Invalid option, please choose 0-{max_opt}.")
                
    
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

            item_key = keys[index]
            idef = bag.get_definitions(item_key) or {}
            target_index = None

            if idef.get("type") == "revive":
                target_index = HumanController._pick_fainted(trainer)
                if target_index is None:
                    return None

            return item_key, target_index

    @staticmethod
    def _pick_fainted(trainer) -> int | None:
        fainted = [(i, p) for i, p in enumerate(trainer.team) if not p.is_alive()]
        if not fainted:
            print("  No fainted Pokémon to revive.")
            return None

        print("\n  Choose a Pokémon to revive:")
        for display, (team_idx, p) in enumerate(fainted, start=1):
            print(f"  [{display}] {p.name} (0/{p.maximun_hp} HP)")
        print("  [0] Cancel")

        while True:
            choice = input("  Choose: ").strip()
            if choice == "0":
                return None
            if not choice.isdigit():
                print("❌ Invalid input.")
                continue
            pick = int(choice) - 1
            if 0 <= pick < len(fainted):
                return fainted[pick][0]
            print(f"❌ Enter a number between 0 and {len(fainted)}.")
        
        
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
            print(f"  {getattr(actor, 'name', 'Pokemon')} has no attacks. Using Struggle!")
            return {"name": "Struggle", "type": "Normal", "damage": 50}

        available = [a for a in all_attacks if actor.get_pp(a.get("name", "")) > 0]

        if not available:
            print(f"\n  {actor.name} has no PP left! Using Struggle!")
            input("  Press Enter...")
            return {"name": "Struggle", "type": "Normal", "damage": 50}

        while True:
            print("\n🌀 Available attacks:")
            for i, atk in enumerate(available, start=1):
                if not isinstance(atk, dict) or not all(k in atk for k in ("name", "type", "damage")):
                    print("Invalid attack format")
                    return None
                atk_type = str(atk["type"]).capitalize()
                atk_dmg  = int(atk["damage"])
                pp_cur   = actor.get_pp(atk["name"])
                pp_max   = actor._pp_max.get(atk["name"], "?")
                print(f"[{i}]: {atk['name']} | Type: {atk_type} | Dmg: {atk_dmg} | PP: {pp_cur}/{pp_max}")
            print("[0: Cancel] / no attack")

            choice = input("Choose your attack (number): ")
            if choice == "0":
                print("😴 You decided not to attack this turn.")
                return None
            if not choice.isdigit():
                print("❌ Invalid input, please enter a number.")
                continue
            index = int(choice) - 1
            if 0 <= index < len(available):
                return available[index]
            print("❌ Invalid number, try again.")
    
    
    def ChooseSwitchPokemon(self, trainer):
        
        has_options = any(trainer.CheckPokemonSwitch(i) for i,_ in enumerate(trainer.team))
        if not has_options:
            print("🛑 No available Pokémon to switch.")
            return None
        
        print("Choose a Pokémon to switch (alive and different from the current):")
        for i, p in enumerate(trainer.team, start=1):
            status = "K.O" if not p.is_alive() else "OK"
            active = "  (Active)" if i - 1 == trainer.active_index else ""
            lv_str = f"Lv.{getattr(p, 'current_level', '?')}"
            bar    = _hp_bar(p, length=12)
            print(f"[{i}] {p.name:<10} {lv_str:<6}  {bar}  {status}{active}")
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


    def _choose_ball(self, trainer) -> dict:
        bag = getattr(trainer, "bag", None)
        if bag is None:
            print("❌ No bag available.")
            return {"type": "skip"}

        balls = {
            k: qty
            for k, qty in bag.counts.items()
            if qty > 0 and (idef := bag.get_definitions(k)) and idef.get("type") == "capture"
        }

        if not balls:
            print("❌ You don't have any Pokéballs!")
            return {"type": "skip"}

        print("\n⚾ Your Pokéballs:")
        keys = list(balls.keys())
        for i, k in enumerate(keys, start=1):
            idef = bag.get_definitions(k) or {}
            print(f"  [{i}] {idef.get('name', k)} x{balls[k]}")
        print("  [0] Cancel")

        while True:
            choice = input("  Choose ball: ").strip()
            if choice == "0":
                return {"type": "skip"}
            if not choice.isdigit():
                print("❌ Invalid input.")
                continue
            index = int(choice) - 1
            if 0 <= index < len(keys):
                return {"type": "capture", "ball": keys[index]}
            print(f"❌ Enter a number between 0 and {len(keys)}.")

    def Human_turn(trainer, enemy_trainer):
        
        controller = trainer.controller or HumanController()
        action = controller.choose_action(trainer, enemy_trainer)
        return action or {"type": "skip"}