from __future__ import annotations
import random
from typing import Dict, Any, Optional, List, Union


def _coerce_level(val: Union[int, float, str, None]) -> int:
    if val is None:
        return 1
    if isinstance(val, (int, float)):
        return max(1, int(val))
    if isinstance(val, str):
        s = val.strip()
        if s.isdigit():
            return max(1, int(s))
        return 1
    return 1


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
        evolution_by_item: Optional[Dict[str, str]] = None,
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

        # --- PP tracking ---
        self._pp_max: Dict[str, int] = {}
        self._pp_current: Dict[str, int] = {}
        for atk in (self.special_attacks + self.normal_attacks):
            atk_name = atk.get("name", "")
            if atk_name and atk_name not in self._pp_max:
                pp = int(atk.get("pp", 20))
                self._pp_max[atk_name] = pp
                self._pp_current[atk_name] = pp

        # --- evolution info ---
        self.evolution: Optional[str] = (str(evolution).strip().lower() if evolution else None)
        self.evolution_level: Optional[int] = (int(evolution_level) if evolution_level is not None else None)
        self.current_level: Optional[int | str] = current_level
        self.xp: int = 0
        self.xp_to_next: int = 50
        self.evolution_by_item: Dict[str, str] = evolution_by_item or {}

        self._temp_buffs: Dict[str, int] = {}

        # --- status condition ---
        self.status: Optional[str] = None    # "poison" | "paralysis" | "sleep" | None
        self.sleep_turns: int = 0

        # --- passive ability ---
        self.ability: Optional[str] = None


    # ---------------- XP and levels ----------------
    def gain_xp(self, amount: int) -> None:
        if amount <= 0:
            return
        self.exp = int(self.exp) + int(amount)

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

    # ---------------- status conditions ----------------

    def apply_status(self, status: str) -> bool:
        """Apply a status condition. Returns False if already has one."""
        if self.status is not None:
            return False
        self.status = status
        if status == "sleep":
            self.sleep_turns = random.randint(1, 3)
        return True

    def clear_status(self) -> None:
        self.status = None
        self.sleep_turns = 0

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

    # ---------------- PP management ----------------

    def get_pp(self, attack_name: str) -> int:
        return self._pp_current.get(attack_name, 0)

    def use_pp(self, attack_name: str) -> None:
        if attack_name in self._pp_current:
            self._pp_current[attack_name] = max(0, self._pp_current[attack_name] - 1)

    def restore_all_pp(self) -> None:
        for name, max_pp in self._pp_max.items():
            self._pp_current[name] = max_pp

    def has_any_pp(self) -> bool:
        return any(v > 0 for v in self._pp_current.values())

    # ---------------- convenience ----------------

    @property
    def all_attacks(self) -> List[Dict[str, Any]]:
        return list(self.special_attacks) + list(self.normal_attacks)

    def show_stats(self) -> None:
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
    
    def __init__(self, name, element_type, health, defense, speed, special_attacks, evolution_attack):
        super().__init__(name, element_type, health, defense, speed, special_attacks)
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

    