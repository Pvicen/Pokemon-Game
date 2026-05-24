from __future__ import annotations
from typing import Optional, Dict, Any

from .utils import clamp
from .data_io import load_items

class Inventory:
    
    def __init__(self, initial_counts: Optional[Dict[str, int]] = None):
        self.counts: dict[str, int] = {}
        self._definitions = load_items()
        if initial_counts:
            for item_name, quantity in initial_counts.items():
                self.add_items(item_name, quantity)
            
        
    def add_items (self, key: str, quantity: int = 1) -> None:
        if key not in self._definitions:
            raise ValueError(f"❌ Item '{key}' is not defined.")
        
        if quantity <= 0:
            raise ValueError("❌ Quantity to add must be positive.")
        
        self.counts[key] = self.counts.get(key, 0) + quantity
        
    
    def remove_items(self, key:str, quantity: int = 1) -> None:
        
        if self.counts.get(key, 0) < quantity:
            raise ValueError(f"❌ Not enough '{key}' items to remove.")
        self.counts[key] -= quantity
        if self.counts[key] <= 0:
            self.counts.pop(key, None)
            print(f"The item {[key]} has_item been remove successfully")
        return True
    
    
    def count(self, key: str) -> int:
        return self.counts.get(key, 0)
    
    
    def show_items(self) -> None:
        if not self.counts:
            print("🎒 Inventory is empty.")
            return
        print("🎒 Your items:")
        for k, amount in self.counts.items():
            print(f" - {k}: {amount}")
            
    
    def list_items(self, key:str) -> Optional[Dict[str, Any]]:
        return dict(self.counts)
    
    
    def has_item(self, key: str) -> bool:
        return self.count(key) > 0
    
    
    def get_definitions(self, key: str) -> Optional[Dict[str, Any]]:
        return self._definitions.get(key)
    
    
    def usable_items(self, in_battle: bool = True) -> Dict[str, int]:
        return {
            k: qty
            for k, qty in self.counts.items()
            if qty > 0
            and (idef := self.get_definitions(k))
            and (in_battle or not idef.get("battle_only", False))
            and idef.get("type") != "capture"
            and not (in_battle and idef.get("type") == "evolution")
        }
    
    
    def use(
        self,
        item_key: str,
        user_trainer,
        in_battle: bool = True,
        target_trainer= None,
        target_index: int | None = None,
        ) -> bool:

        idef = self.get_definitions(item_key)
        if not idef:
            raise ValueError(f"❌ Unknown item '{item_key}'")

        if in_battle is False and idef.get("battle_only", False):
            print(f"❌ '{idef['name']}' can only be used in battle.")
            return False

        reusable = bool(idef.get("reusable", False))
        if not reusable and not self.has_item(item_key):
            print(f"❌ You don't have '{idef['name']}' in your bag.")
            return False

        item_type = idef.get("type", None)
        target_kind = idef.get("target", "ally")

        if target_kind == "ally":
            if user_trainer is None:
                print("❌ No ally trainer provided.")
                return False
            if target_index is not None:
                if not (0 <= target_index < len(user_trainer.team)):
                    print("❌ Invalid target index.")
                    return False
                pokemon = user_trainer.team[target_index]
            else:
                pokemon = user_trainer.ActivePokemon

        else:
            if target_trainer is None:
                print("❌ No enemy trainer provided.")
                return False
            pokemon = target_trainer.ActivePokemon
        
        effect_type = idef.get("effect", {})

        if item_type == "healing":
            ok = self._apply_heal(pokemon, effect_type)
        elif item_type == "revive":
            ok = self._apply_revive(pokemon, effect_type)
        elif item_type == "buff":
            ok = self._apply_buff(pokemon, effect_type, in_battle=in_battle)
        elif item_type == "evolution":
            ok = self._apply_evolution(pokemon, item_key, user_trainer)
        elif item_type == "status_cure":
            ok = self._apply_status_cure(pokemon, effect_type)
        else:
            raise ValueError(f"❌ Unsupported item type: {item_type!r}.")
        
        if ok and not reusable:
            self.remove_items(item_key, 1)
            
        return ok
    
    
    def _apply_heal(self, pokemon, effect: Dict[str, Any]) -> bool:
        if pokemon is None:
            return False
        
        if not hasattr(pokemon, "health") or not hasattr(pokemon, "maximun_hp"):
            raise ValueError(f"❌ Target {pokemon} has_item no health fields.")
        
        if pokemon.health <= 0:
            print(f"⚠️ {pokemon.name} is fainted. Use a Revive pill to restore it.")
            return False

        amount = effect.get("amount", None)
        percent = effect.get("percent", None)
        
        healed = 0
        
        if amount is not None:
            healed = int(amount)
        if percent is not None:
            healed = int(max(1, pokemon.maximun_hp * float(percent)))
        
        old_health = pokemon.health
        pokemon.health = clamp(pokemon.health + max(0, healed), 0, pokemon.maximun_hp)
        gained = pokemon.health - old_health
        print(f"✨ {pokemon.name} healed {gained} HP ({old_health}->{pokemon.health}/{pokemon.maximun_hp}).")
        return True
    
    
    def _apply_revive(self, pokemon, effect: Dict[str, Any]) -> bool:
        if pokemon is None:
            return False
        if pokemon.health > 0:
            print(f"⚠️ {pokemon.name} is already alive.")
            return False

        revive_hp = str(effect.get("revive_hp", "half")).lower()
        if revive_hp == "full":
            pokemon.health  = pokemon.maximun_hp
        else:
            pokemon.health = max(1, pokemon.maximun_hp // 2)

        print(f"💫 {pokemon.name} has_item been revived to {pokemon.health}/{pokemon.maximun_hp} HP.")
        return True
    
    
    def _apply_buff(self, pokemon, effect: Dict[str, Any], in_battle: bool) -> bool:
        if not in_battle:
            print("❌ Buff items can only be used in battle.")
            return False
        
        stat = str(effect.get("stat", "")).strip()
        stages = int(effect.get("stages", 0))
        
        if not hasattr(pokemon, "_temp_buffs"):
            pokemon._temp_buffs = {}
            
        current = pokemon._temp_buffs.get(stat, 0)
        pokemon._temp_buffs[stat] = current + stages
        
        arrow = "↑" if stages > 0 else "↓"
        print(f"⚔️ {pokemon.name}'s {stat} {arrow} by {abs(stages)} stage(s). [now {pokemon._temp_buffs[stat]}]")
        return True
    
    
    def _apply_status_cure(self, pokemon, effect: Dict[str, Any]) -> bool:
        target_status = effect.get("status", None)  # None = cure any status
        current = getattr(pokemon, "status", None)
        if current is None:
            print(f"  {pokemon.name} has no status condition.")
            return False
        if target_status and current != target_status:
            print(f"  {pokemon.name} is not {target_status}.")
            return False
        pokemon.clear_status()
        print(f"  ✨ {pokemon.name}'s {current} was cured!")
        return True


    def _apply_evolution(self, pokemon, item_key: str, trainer=None) -> bool:
        # TODO: Refactor _apply_species to models.Pokemon
        from .experience import _try_species_lookup, _apply_species  # lazy import to avoid circular dependency

        evo_by_item: dict = getattr(pokemon, "evolution_by_item", None) or {}
        target_name = evo_by_item.get(item_key) or evo_by_item.get(item_key.lower())

        if not target_name:
            print(f"  {pokemon.name} can't evolve with this stone.")
            return False

        target_key = str(target_name).strip().lower()
        species_def = _try_species_lookup(target_key)
        if not species_def:
            print(f"  Evolution target '{target_name}' not found in Pokédex.")
            return False

        old_name = pokemon.name
        keep_level = int(getattr(pokemon, "current_level", None) or getattr(pokemon, "level", 1) or 1)
        keep_exp = int(getattr(pokemon, "xp", 0))
        _apply_species(pokemon, species_def, keep_level=keep_level, keep_exp=keep_exp)
        pokemon.evolution_by_item = {}
        print(f"  🌟 {old_name} evolved into {pokemon.name}!")
        if trainer is not None:
            trainer.register_caught(pokemon.name, keep_level)
        return True


    @staticmethod
    def get_effective_stat(pokemon, stat_name: str) -> int:
        
        base_val = int(getattr(pokemon, stat_name, 0))
        if base_val  <= 0:
            return 1
        stages = 0
        if hasattr(pokemon, "_temp_buffs"):
            stages = int(getattr(pokemon, "_temp_buffs", {}).get(stat_name, 0))
        
        mult = 1.0 + 0.10 * stages
        eff = int(max(1, round(base_val * mult)))
        return eff
    
    
    @staticmethod
    def clear_temp_buffs(pokemon) -> None:
        if hasattr(pokemon, "_temp_buffs"):
            try:
                delattr(pokemon, "_temp_buffs")
            except Exception:
                setattr(pokemon, "_temp_buffs", {})
                
    
    @staticmethod
    def clear_battle_state_trainers(trainers) -> None:
        for trainer in trainers:
            if trainer is None:
                continue
            team  = getattr(trainer, "team", [])
            for pokemon in team:
                Inventory.clear_temp_buffs(pokemon)