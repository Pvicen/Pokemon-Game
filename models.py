from __future__ import annotations
from typing import Dict, Any, Optional, List

class Pokemon:
    def __init__(
        self,
        name: str,
        element_type: str,
        health: int,
        normal_attacks: Optional[List[Dict[str, Any]]] = None,
        defense: int = 0,
        special_defense: int = 0,
        speed: int = 0,
        evolution: Optional[str] = None,
        evolution_level: Optional[int] = None,
        current_level: Optional[int | str] = None,
        special_attacks: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        # --- base identity ---
        self.name: str = str(name)
        self.element_type: str = str(element_type).strip().lower() if element_type is not None else "unknown"

        # --- stats ---
        self.health: int = max(0, int(health))
        self.maximun_hp: int = max(1, int(health))
        self.max_hp: int = self.maximun_hp
        self.defense: int = max(0, int(defense))
        self.special_defense: int = max(0, int(special_defense))
        self.speed: int = max(0, int(speed))

        # --- attacks ---
        self.special_attacks: List[Dict[str, Any]] = list(special_attacks) if special_attacks else []
        self.normal_attacks: List[Dict[str, Any]] = list(normal_attacks) if normal_attacks else []

        # --- evolution info ---
        self.evolution: Optional[str] = (str(evolution).strip().lower() if evolution else None)
        self.evolution_level: Optional[int] = (int(evolution_level) if evolution_level is not None else None)
        self.current_level: Optional[int | str] = current_level
        
        
        self._temp_buffs: Dict[str, int] = {}

    # ---------------- basic status ----------------

    def is_alive(self) -> bool:
        if self.health < 0:
            self.health = 0
        return self.health > 0

    def clamp_hp(self) -> None:
        if self.health < 0:
            self.health = 0
        if self.health > self.maximun_hp:
            self.health = self.maximun_hp

    # ---------------- damage / healing ----------------

    def take_damage(self, amount: int) -> int:
        dmg = max(0, int(amount))
        before = self.health
        self.health = max(0, before - dmg)
        return before - self.health

    def heal(self, amount: int) -> int:
        inc = max(0, int(amount))
        before = self.health
        self.health = min(self.maximun_hp, before + inc)
        return self.health - before

    def heal_percent(self, ratio: float) -> int:
        r = float(ratio)
        if r <= 0.0:
            return 0
        target = int(round(self.maximun_hp * r))
        want = target - self.health
        return self.heal(max(0, want))

    # ---------------- stages / buffs ----------------

    def get_stage(self, stat: str) -> int:
        return int(self._temp_buffs.get(stat, 0))

    def apply_stage_buff(self, stat: str, delta: int) -> int:
        cur = self.get_stage(stat)
        new = cur + int(delta)
        self._temp_buffs[stat] = new
        return new

    def clear_battle_buffs(self) -> None:
        self._temp_buffs.clear()

    # ---------------- convenience ----------------

    @property
    def all_attacks(self) -> List[Dict[str, Any]]:
        """Return the concatenation of special + normal attacks (a new list)."""
        return list(self.special_attacks) + list(self.normal_attacks)

    def show_stats(self) -> None:
        """Simple pretty print (non-essential, kept for debugging)."""
        print(f"Attributes of {self.name}:")
        print(f"- Type: {self.element_type}")
        print(f"- Health: {self.health}/{self.maximun_hp}")
        print(f"- Defense: {self.defense}")
        print(f"- Special Defense: {self.special_defense}")
        print(f"- Speed: {self.speed}")
        print(f"- Evolution: {self.evolution}")
        print(f"- Evolution Level: {self.evolution_level}")
        print(f"- Current Level: {self.current_level}")
        
        

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
