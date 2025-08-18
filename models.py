from .damage import get_effectiveness, calculate_damage, damage_without_element

class Pokemon:
    
    def __init__(self, name, element_type, health, normal_attacks, defense, special_defense, speed, evolution, evolution_level, current_level, special_attacks = None):
        
        # Stats
        self.name = name
        self.element_type = element_type
        self.health = health
        self.defense = defense
        self.special_defense = special_defense
        self.speed = speed
        self.maximun_hp = health
        
        # Attacks
        self.special_attacks = special_attacks if special_attacks else []
        self.normal_attacks = normal_attacks if normal_attacks else []
        
        # Evolution
        self.evolution = evolution
        self.evolution_level = evolution_level
        self.current_level = current_level
        
        # Items
    def inventory(self, enemy):
        pass
        
        
    def show_stats(self):
        print(f"Attributes of {self.name}:", sep="")
        print(f"-type: {self.element_type}")
        print(f"-Health: {self.health}")
        print(f"-Defense: {self.defense}")
        print(f"-Special_defense: {self.special_defense}")
        print(f"-Speed: {self.speed}")
        print(f"-Evolution: {self.evolution}")
        print(f"-Evolution_level: {self.evolution_level}")
        print(f"-Current_level: {self.current_level}")
    
    def is_alive(self):
        if self.health < 0:
            self.health = 0
        return self.health > 0
    
    
    def health_bar(self):
        length = 20
        units = int((self.health * length) / self.maximun_hp)
        bar = "█" * units + " " * (length - units)
        print(f"❤️  Vida de {self.name}: [{bar}] {self.health}/{self.maximun_hp}")
        
    def use_attack(self, enemy, final_damage):
        
        print("\n🎯 State of the enemy BEFORE the attack:")
        enemy.health_bar()

        print("\n🔽 ATTACK IN PROGRESS 🔽")
        
        print("\n🌀 Avaliable attacks:")
            
        all_attacks = list(self.normal_attacks) + list(self.special_attacks)
            
        for i, atk in enumerate(all_attacks, start=1):
            if isinstance(atk, dict):
                print(f"[{i}] -Name: {atk['name']} -Damage: {atk['damage']} -Type: {atk['type']}")
            else:
                print(f"[{i}] ⚠️ ¡Malformed attack! Content: {atk}")

        print("Press enter for not attack in this turn")

        choice = input("Choose the attack: ")
            
        if choice.isdigit():
            index = int(choice)- 1
                
            if 0 <= index < len(all_attacks):
                selected_attack = all_attacks[index]
                attack_name = selected_attack["name"]
                attack_type = selected_attack["type"]
                attack_damage = selected_attack["damage"]

                print(f"\n⚔️ ¡{self.name} use {attack_name}!")
            
                if attack_type == "Normal":
                    damage, message = damage_without_element(self, enemy, attack_damage)
                    print(message)
                    enemy.health -= damage
                    print(f"✨ {self.name} has made with normal attacks {damage}, points of damage.")
                else:
                    damage = max(1, int(attack_damage - enemy.special_defense * 0.5))
                    print(f"✨ {self.name} has made with elemtal attack {damage}, points of damage.")
                    enemy.health -= damage
                    
                enemy.is_alive()
            else:
                print("❌ Número de ataque fuera de rango. No se realiza acción.")
        else:
            print(f"😴 {self.name} decidió no atacar este turno.")
                
        print(f"{enemy.name} now has {enemy.health} HP")
        print("\n" + "=" * 50 + "\n")
            
    def perform_combat(self, enemy, get_effectinveness, calculate_damage):
        self.health_bar()
        self.show_stats()
        print("\n")
        
        multiplier, effecntiveness_message = get_effectinveness(self.element_type, enemy.element_type)
        print(effecntiveness_message)
        
        self.use_attack(enemy, final_damage=None)
            
    def choose_item(self):
        print("\nThese are the avaliable items\n"
                "[1] Chose ribbon, base_attack + 7\n"
                "[2] Toothed helmet, base_attack + 13\n"
				"[3] Superpotion, health + 50\n"
       			"[4] Hyperpotion, health + 100\n"
       			"[5] do nothing\n")
        option = input("chosose your option: ")

        if option == "5":
            print(f"{self.name}, has decide not to use any item")
            return

        if option in self.items:
            obj = self.items[option]
            if obj["used"]:
                print(f"\nYou have already used the items: {obj['name']}")
            else:
                obj["effect"]()
                obj["used"] = True
                print(f"\nYou use the items: {obj['name']}\n")
        else:
            print("❌ Option out of range (1 to 5)")
        
        if self.health > self.maximun_hp:
            self.health = self.maximun_hp
        
    def upgrade_pokemon(self):
        pass
        

class EvolvedPokemon(Pokemon):
    
    def __init__(self, name, element_type, health, base_attack, defense, speed, special_attacks, evolution_attack):
        super().__init__(name, element_type, health, base_attack, defense, speed, special_attacks)
        self.evolution_attack = evolution_attack
        self.used_evolution_attack = False
        
    def show_stats(self):
        super().show_stats()
        print(f"-Evolution_Attack: {self.evolution_attack}")
    
    def combined_attack(self, enemy):
        
        if not self.used_evolution_attack:
            print(f"{self.name} HASSS MADEEE ¡¡¡¡¡¡¡COMBINED ATTAAACKKKK!!!!!!!")
            total_attack = self.base_attack + self.evolution_attack
            enemy.health -= total_attack
            enemy.is_alive()
            print(f"{self.name} Has made {total_attack} points of damage to {enemy.name}")
            self.used_evolution_attack = True
            
        else:
            self.use_attack(enemy)