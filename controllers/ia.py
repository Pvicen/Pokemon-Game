from ..models import Pokemon
from ..damage import get_effectiveness, damage_without_element, calculate_damage

class IAcontroller():
    
    def CalculatingDamages(actor, target, atk):

        if not isinstance(atk, dict) or not all( k in atk for k in ("name", "type", "damage")):
            return -1, 1.0
        
        atk_type = str(atk["type"]).capitalize()
        dmg = atk["damage"]
        
        if atk_type == "Normal":
            estimated_damage = max(1, dmg - target.defense * 0.4)
            mult = 1.0
        else:
            mult, _ = get_effectiveness(actor.element_type, target.element_type)
            estimated_damage = calculate_damage(actor, target, dmg, attack_type= atk_type)
        
        return mult, estimated_damage
    
    def BestMove(actor, target):
        
        all_attakcs = []
        
        if getattr(actor, "special_attacks", None):
            all_attakcs.extend(list(actor.special_attacks))
            
        if getattr(actor, "normal_attacks", None):
            all_attakcs.extend(list(actor.normal_attacks))
        
        if not all_attakcs:
            return None
    
        best =  None
        best_estimated = -1
        best_mult = 1.0
        
        
        for atk in all_attakcs:
            mult, estimated_damage = IAcontroller.CalculatingDamages(actor, target, atk)
            if estimated_damage > best_estimated or (estimated_damage == best_estimated and mult > best_mult):
                best = atk
                best_estimated = estimated_damage
                best_mult = mult
            
        return best

    def IA_turn(actor, target):
        
        attack = IAcontroller.BestMove(actor, target)

        if not attack:
            print(f"🤖 {actor.name} don`t have avaliable attacks")
            return

        name = attack["name"]
        base_dmg = int(attack["damage"])
        type = str(attack["type"]).capitalize()

        print(f"\n🤖 {actor.name} attacked with {name} (type: {type}, damage: {base_dmg})")

        if type == "Normal":
            dmg, msg = damage_without_element(actor, target, base_dmg)
            print(msg)
        else:
            dmg, eff_msg = get_effectiveness(actor.element_type, target.element_type)
            print(eff_msg)
            dmg = calculate_damage(actor, target, base_dmg, attack_type=type)
            
        target.health -= dmg
        target.is_alive()
        