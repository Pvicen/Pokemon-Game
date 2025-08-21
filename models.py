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
        
        
    def ShowStats(self):
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
    
    
    def perform_combat(self, enemy, get_effectinveness, calculate_damage):
        self.health_bar()
        self.ShowStats()
        print("\n")
        enemy.health_bar()
        enemy.ShowStats()
        print("\n")
            
    def upgrade_pokemon(self):
        pass
        

class EvolvedPokemon(Pokemon):
    
    def __init__(self, name, element_type, health, base_attack, defense, speed, special_attacks, evolution_attack):
        super().__init__(name, element_type, health, base_attack, defense, speed, special_attacks)
        self.evolution_attack = evolution_attack
        self.used_evolution_attack = False
        
    def ShowStats(self):
        super().ShowStats()
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