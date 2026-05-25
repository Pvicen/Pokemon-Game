from __future__ import annotations

import random
from typing import Optional, Tuple

ABILITY_BY_SPECIES: dict = {
    "pikachu":   "Static",
    "raichu":    "Static",
    "magnemite": "Static",
    "magneton":  "Static",
    "geodude":   "Sturdy",
    "graveler":  "Sturdy",
    "golem":     "Sturdy",
    "onix":      "Sturdy",
    "gastly":    "Levitate",
    "haunter":   "Levitate",
    "gengar":    "Levitate",
    "koffing":   "Levitate",
    "weezing":   "Levitate",
    "growlithe": "Intimidate",
    "arcanine":  "Intimidate",
    "arbok":     "Intimidate",
}


def fire_on_entry(pokemon, opponent, log) -> None:
    """Fires when a Pokémon enters the field. Handles Intimidate."""
    ability = getattr(pokemon, "ability", None)
    if ability == "Intimidate":
        opponent.apply_stage_buff("normal_attacks", -1)
        opponent.apply_stage_buff("special_attacks", -1)
        msg = f"  \U0001f624  {pokemon.name}'s Intimidate lowered {opponent.name}'s attack!"
        if log is not None:
            log.append(msg)
        else:
            print(msg)


def fire_pre_damage(attacker, defender, dmg: int, attack_type: str) -> Tuple[int, Optional[str]]:
    """
    Fires before damage is applied. Returns (modified_dmg, Optional[message]).
    If returned dmg == 0 with a message, the caller must short-circuit (immunity).
    """
    ability = getattr(defender, "ability", None)

    if ability == "Levitate" and attack_type.lower() == "ground":
        return 0, f"  \U0001f300  {defender.name}'s Levitate made it immune to Ground moves!"

    if (
        ability == "Sturdy"
        and defender.health == defender.maximun_hp
        and dmg > 0
        and defender.health - dmg <= 0
    ):
        return defender.health - 1, f"  \U0001f6e1️  {defender.name} survived the hit with Sturdy!"

    return dmg, None


def fire_on_hit_received(attacker, defender, dmg_dealt: int) -> Optional[str]:
    """
    Fires after a hit lands. Returns an Optional message appended by the caller.
    """
    ability = getattr(defender, "ability", None)
    if not ability or dmg_dealt <= 0:
        return None

    if ability == "Static":
        # TODO (Deuda Técnica): Static actualmente se activa con cualquier ataque. En el futuro, requerirá un flag de "contacto" en attacks.json para no activarse con ataques a distancia.
        if getattr(attacker, "status", None) is None and random.random() < 0.30:
            if attacker.apply_status("paralysis"):
                return f"  ⚡  {defender.name}'s Static paralyzed {attacker.name}!"

    return None
