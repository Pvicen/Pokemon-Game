import random

from ..models import Pokemon
from ..damage import get_effectiveness, damage_without_element, calculate_damage
from ..trainers import Trainer

class IAcontroller():


    @staticmethod
    def _all_attacks_of(pokemon):

        all_attacks = []

        if getattr(pokemon, "special_attacks", None):
            all_attacks.extend(list(pokemon.special_attacks))

        if getattr(pokemon, "normal_attacks", None):
            all_attacks.extend(list(pokemon.normal_attacks))

        return (all_attacks if all_attacks else None)


    @staticmethod
    def _status_attacks_of(pokemon):
        """Pure status moves with PP left (Toxic / Thunder Wave / Sleep Powder).

        Restricted to 0-damage moves so the IA only reaches for these when it
        wouldn't otherwise pick them by raw damage — damaging moves that also
        inflict status (Poison Sting/Fang) keep their normal damage path.
        """
        out = []
        for atk in (IAcontroller._all_attacks_of(pokemon) or []):
            if not isinstance(atk, dict):
                continue
            effect = atk.get("effect")
            if not (isinstance(effect, dict) and effect.get("kind") == "status"):
                continue
            if int(atk.get("damage", 0)) != 0:
                continue
            if pokemon.get_pp(atk.get("name", "")) <= 0:
                continue
            out.append(atk)
        return out
    
    
    @staticmethod
    def ChooseAction(trainer, enemy_trainer):
        actor = trainer.ActivePokemon
        target = enemy_trainer.ActivePokemon
        
        if not actor.is_alive():
            idx = IAcontroller.BestSwitch(trainer, target)
            return {"type": "switch", "index": idx} if idx is not None else {"type": "skip"}
        
        current_score = IAcontroller._current_position_score(actor, target)
        best_idx = IAcontroller.BestSwitch(trainer, target)
        best_switch_score = None
        if best_idx is not None:
            best_switch_score = IAcontroller._current_position_score(trainer.team[best_idx], target)
            
        if best_switch_score is not None and best_switch_score >= 2.0 * current_score:
            return {"type": "switch", "index": best_idx}

        # ── Q1: tactical status move ──
        # If the target has no status yet, roll the difficulty-scaled chance to
        # land a pure status move (Toxic / Thunder Wave / Sleep Powder).
        if getattr(target, "status", None) is None:
            status_atks = IAcontroller._status_attacks_of(actor)
            if status_atks:
                try:
                    from ..game.difficulty import ai_status_chance
                    chance = ai_status_chance()
                except Exception:
                    chance = 0.0
                if random.random() < chance:
                    return {"type": "attack", "attack": random.choice(status_atks)}

        best_dmg, best_atk = IAcontroller._Calculating_Damages(actor, target)
        if best_atk:
            return {"type": "attack", "attack": best_atk}
        if best_idx is not None:
            return {"type": "switch", "index": best_idx}
        return {"type": "skip"}
        
    
    @staticmethod
    def _Calculating_Damages(actor, target):
        
        attacks = IAcontroller._all_attacks_of(actor)
        
        if not attacks:
            return 0, None
        
        best_dmg = 0
        best_atk = None
        for atk in attacks:
            if not isinstance(atk, dict) or not all(k in atk for k in ("name", "type", "damage")):
                continue
            if actor.get_pp(atk.get("name", "")) <= 0:
                continue

            atk_type = str(atk["type"]).capitalize()
            dmg = atk["damage"]

            if atk_type == "Normal":
                estimated_damage = max(1, int(dmg - target.defense * 0.4))
            else:
                estimated_damage = int(calculate_damage(actor, target, dmg, attack_type=atk_type))
            if estimated_damage > best_dmg:
                best_dmg = estimated_damage
                best_atk = atk

        if best_atk is None:
            return 50, {"name": "Struggle", "type": "Normal", "damage": 50}

        return best_dmg, best_atk
    
    
    @staticmethod
    def _Score_Switch_candidate(ally, enemy):
        
        # Calculate how effective the ally's type is against the enemy's type
        offensive_mult, _ = get_effectiveness(ally.element_type, enemy.element_type)
        # Calculate how much damage the enemy can do to the ally
        defense_mult, _ = get_effectiveness(enemy.element_type, ally.element_type)
        #Calculate  the best damage the ally can do to the enemy
        best_off_damage, _ = IAcontroller._Calculating_Damages(ally, enemy)
        
        hp_ratio = ally.health / ally.maximun_hp if ally.maximun_hp > 0 else 0.0
        speed_bonus = 1.10 if getattr(ally, "speed", 0) > getattr(enemy, "speed", 0) else 1.00
    
        score = (1.2 * offensive_mult) + (best_off_damage / 100)
        if defense_mult >= 2.0:score *= 0.70
        elif defense_mult <= 0.5:score *= 1.10
        score *= (0.5 + hp_ratio * 0.5) * speed_bonus
        
        enemy_ratio = enemy.health / enemy.maximun_hp if enemy.maximun_hp > 0 else 0.0
        if enemy_ratio < 0.30:
            ally_power = (0.5 * hp_ratio) +(0.2 if getattr(ally, "speed", 0) > getattr(enemy, "speed", 0) else 0.0)
            
            score = max(0.0, score - 0.25 * ally_power)

        return score
    
    
    @staticmethod
    def BestSwitch(trainer, enemy_pokemon):

        best_index = None
        best_score = float("-inf")
        
        for i, pokemon in enumerate(trainer.team):
            if i == trainer.active_index or not pokemon.is_alive():
                continue
            
            score = IAcontroller._Score_Switch_candidate(pokemon, enemy_pokemon)
            if score > best_score:
                best_score = score
                best_index = i
            
        return best_index if best_index is not None else None
    
    
    @staticmethod
    def _current_position_score(active, enemy):
        
        offense_mult, _ = get_effectiveness(active.element_type, enemy.element_type)
        defense_mult, _ = get_effectiveness(enemy.element_type, active.element_type)
        best_off_damage, _ = IAcontroller._Calculating_Damages(active, enemy)
        
        hp_ratio = active.health / active.maximun_hp if active.maximun_hp > 0 else 0.0
        speed_bonus = 1.10 if getattr(active, "speed", 0) > getattr(enemy, "speed", 0) else 1.00
        
        score = (1.2 * offense_mult) + (best_off_damage / 100)
        if defense_mult >= 2.0:score *= 0.70
        elif defense_mult <= 0.5:score *= 1.10
        score *= (0.5 + hp_ratio * 0.5) * speed_bonus
        
        return max(score, 0.0)
    
    @staticmethod
    def BestMove(actor, target):
        _, best_atk = IAcontroller._Calculating_Damages(actor, target)
        return best_atk
    
    
    @staticmethod
    def IA_turn(trainer, enemy_trainer, is_wild: bool = False):
        return IAcontroller.ChooseAction(trainer, enemy_trainer)