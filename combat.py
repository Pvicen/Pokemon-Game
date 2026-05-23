from __future__ import annotations

import collections
import os
import re
import random
from typing import Any, Deque, Dict, List, Optional, Tuple

from .models import Pokemon
from .trainers import Trainer
from .damage import calculate_damage, get_effectiveness, damage_without_element
from .inventory import Inventory
from .controllers import HumanController, IAcontroller
from .utils import determine_attack_order
from .experience import ExperienceManager


CLEAR_CMD = "cls" if os.name == "nt" else "clear"
os.system("")  # Enable ANSI escape codes on Windows

_R    = "\033[0m"
_BOLD = "\033[1m"
_ANSI_RE = re.compile(r'\033\[[0-9;]*m')

_TYPE_COLORS: Dict[str, str] = {
    "fire":     "\033[91m",
    "water":    "\033[94m",
    "grass":    "\033[92m",
    "electric": "\033[93m",
    "psychic":  "\033[95m",
    "ghost":    "\033[35m",
    "poison":   "\033[35m",
    "rock":     "\033[33m",
    "ground":   "\033[33m",
    "fighting": "\033[31m",
    "bug":      "\033[32m",
    "ice":      "\033[96m",
    "dragon":   "\033[34m",
    "normal":   "\033[37m",
}

_BOX_W = 54  # visible inner width between ║ borders


# ─────────────────────── ANSI / color helpers ───────────────────────

def _type_color(element_type: str) -> str:
    return _TYPE_COLORS.get((element_type or "").lower(), "\033[37m")


def _vlen(s: str) -> int:
    """Visible length of a string, ignoring ANSI escape sequences."""
    return len(_ANSI_RE.sub("", s))


def _pad(s: str, width: int) -> str:
    """Right-pad s to the given visible width, accounting for ANSI codes."""
    return s + " " * max(0, width - _vlen(s))


def _hp_bar(pokemon: Pokemon, length: int = 16) -> str:
    hp     = max(0, int(getattr(pokemon, "health", 0)))
    max_hp = max(1, int(getattr(pokemon, "maximun_hp", 1)))
    units  = max(0, min(length, int(hp * length / max_hp)))
    ratio  = hp / max_hp
    if ratio > 0.5:
        bar_color = "\033[92m"
    elif ratio > 0.25:
        bar_color = "\033[93m"
    else:
        bar_color = "\033[91m"
    bar = bar_color + "█" * units + "\033[90m" + "░" * (length - units) + _R
    return f"[{bar}] {hp}/{max_hp}"


# ─────────────────────── Battle screen ───────────────────────

def _draw_battle_screen(enemy: Pokemon, player: Pokemon, log_lines: list) -> None:
    """Clears terminal and draws the battle status box + last 3 log lines."""
    _clear_screen()

    def box_row(content: str) -> str:
        return f"  ║ {_pad(content, _BOX_W - 2)} ║"

    # Enemy — top left
    e_type   = (getattr(enemy, "element_type", "Normal") or "Normal").capitalize()
    e_lv     = getattr(enemy, "current_level", 1)
    e_tc     = _type_color(e_type)
    e_header = f"{_BOLD}{enemy.name}{_R}  Lv.{e_lv}  {e_tc}[{e_type}]{_R}"
    e_hp     = f"HP: {_hp_bar(enemy)}"

    # Player — bottom right, indented
    p_type   = (getattr(player, "element_type", "Normal") or "Normal").capitalize()
    p_lv     = getattr(player, "current_level", 1)
    p_tc     = _type_color(p_type)
    indent   = " " * 22
    p_header = f"{indent}{_BOLD}{player.name}{_R}  Lv.{p_lv}  {p_tc}[{p_type}]{_R}"
    p_hp     = f"{indent}HP: {_hp_bar(player)}"

    print(f"  ╔{'═' * _BOX_W}╗")
    print(box_row(e_header))
    print(box_row(e_hp))
    print(box_row(""))
    print(box_row(p_header))
    print(box_row(p_hp))
    print(f"  ╚{'═' * _BOX_W}╝")

    if log_lines:
        print()
        for entry in list(log_lines)[-3:]:
            for sub in str(entry).split("\n"):
                if sub.strip():
                    print(f"    {sub}")
    print()


# ─────────────────────── Internal helpers ───────────────────────

def _clear_screen() -> None:
    os.system(CLEAR_CMD)


def _clear_buffs_of(p: Pokemon) -> None:
    try:
        from .inventory import Inventory
        Inventory.clear_temp_buffs(p)
        return
    except Exception:
        pass
    if hasattr(p, "clear_battle_buffs"):
        p.clear_battle_buffs()
    else:
        try:
            delattr(p, "_temp_buffs")
        except Exception:
            setattr(p, "_temp_buffs", {})


def _cleanup_battle(trainer_a: Trainer, trainer_b: Trainer) -> None:
    try:
        from .inventory import Inventory
        Inventory.clear_battle_state_trainers((trainer_a, trainer_b))
        return
    except Exception:
        for t in (trainer_a, trainer_b):
            for p in getattr(t, "team", []):
                _clear_buffs_of(p)


# ─────────────────────── Action helpers ───────────────────────

def _choose_action(trainer, enemy_trainer, is_wild: bool = False) -> Dict[str, Any]:
    controller = getattr(trainer, "controller", None)

    if controller and hasattr(controller, "choose_action"):
        return controller.choose_action(trainer, enemy_trainer, is_wild=is_wild) or {"type": "skip"}

    if controller and hasattr(controller, "IA_turn"):
        return controller.IA_turn(trainer, enemy_trainer, is_wild=is_wild) or {"type": "skip"}

    actor   = trainer.ActivePokemon
    attacks = []
    if getattr(actor, "special_attacks", None):
        attacks.extend(actor.special_attacks)
    if getattr(actor, "normal_attacks", None):
        attacks.extend(actor.normal_attacks)
    if attacks:
        return {"type": "attack", "attack": attacks[0]}
    return {"type": "skip"}


def _apply_attack(attacker: Pokemon, defender: Pokemon, attack: Dict) -> Tuple[int, str]:
    if not attack or not isinstance(attack, dict):
        return 0, f"  {getattr(attacker, 'name', 'Pokemon')} failed to act."

    atk_name = str(attack.get("name", "Unknown"))
    atk_type = str(attack.get("type", "Normal")).capitalize()
    base_dmg = int(attack.get("damage", 0))

    if atk_type == "Normal":
        dmg, hit_msg = damage_without_element(attacker, defender, base_dmg)
        eff_msg = hit_msg
    else:
        dmg = int(calculate_damage(attacker, defender, base_dmg, attack_type=atk_type))
        _, eff_msg = get_effectiveness(attacker.element_type, defender.element_type)

    before = max(0, defender.health)
    defender.health = max(0, defender.health - max(0, dmg))
    after  = defender.health

    lines = [
        f"  ★ {attacker.name} used {atk_name}!",
        f"    → Damage: {before - after}  |  {eff_msg}",
        f"    → {defender.name} HP: {before} → {after}",
    ]
    return (before - after), "\n".join(lines)


def _handle_faint_and_switch(
    trainer: Trainer,
    enemy_trainer: Trainer,
    log: Optional[Deque] = None,
    redraw_fn=None,
) -> bool:
    active = trainer.ActivePokemon
    if active.is_alive():
        return True

    msg = f"  ☠️  {active.name} fainted!"
    if log is not None:
        log.append(msg)
    else:
        print(msg)

    _clear_buffs_of(active)

    controller = getattr(trainer, "controller", None)

    if controller and hasattr(controller, "ChooseSwitchPokemon"):
        if redraw_fn is not None:
            redraw_fn()
        idx = controller.ChooseSwitchPokemon(trainer)
        if idx is not None and trainer.SwitchPokemon(idx):
            switch_msg = f"  ↩️  {trainer.name} sends out {trainer.ActivePokemon.name}!"
            if log is not None:
                log.append(switch_msg)
            else:
                print(switch_msg)
            return True

    if controller and hasattr(controller, "BestSwitch"):
        try:
            idx = controller.BestSwitch(trainer, enemy_trainer.ActivePokemon)
            if idx is not None and trainer.SwitchPokemon(idx):
                switch_msg = f"  ↩️  {trainer.name} sends out {trainer.ActivePokemon.name}!"
                if log is not None:
                    log.append(switch_msg)
                else:
                    print(switch_msg)
                return True
        except Exception:
            pass

    for i, p in enumerate(trainer.team):
        if i != trainer.active_index and p.is_alive():
            if trainer.SwitchPokemon(i):
                switch_msg = f"  ↩️  {trainer.name} sends out {trainer.ActivePokemon.name}!"
                if log is not None:
                    log.append(switch_msg)
                else:
                    print(switch_msg)
                return True

    out_msg = f"  \U0001f3f3️  {trainer.name} has no Pokemon left!"
    if log is not None:
        log.append(out_msg)
    else:
        print(out_msg)
    return False


def _take_turn(
    attacker_trainer: Trainer,
    defender_trainer: Trainer,
    xp_manager: Optional[ExperienceManager] = None,
    is_wild: bool = False,
    log: Optional[Deque] = None,
    redraw_fn=None,
) -> bool | str:
    actor  = attacker_trainer.ActivePokemon
    target = defender_trainer.ActivePokemon

    if not actor.is_alive():
        if not _handle_faint_and_switch(attacker_trainer, defender_trainer, log=log, redraw_fn=redraw_fn):
            return False
        actor = attacker_trainer.ActivePokemon

    action = _choose_action(attacker_trainer, defender_trainer, is_wild=is_wild)
    atype  = action.get("type", "skip")

    if atype == "attack":
        attack = action.get("attack")
        dmg, msg = _apply_attack(actor, target, attack)
        if log is not None:
            log.append(msg)
        else:
            print(msg)
        if not target.is_alive():
            try:
                if xp_manager is not None:
                    xp_manager.on_ko(attacker=actor, defender=target)
            except Exception:
                pass
            return _handle_faint_and_switch(defender_trainer, attacker_trainer, log=log, redraw_fn=redraw_fn)
        return True

    elif atype == "switch":
        index = action.get("index")
        if index is None:
            return True
        outgoing = attacker_trainer.ActivePokemon
        ok = attacker_trainer.SwitchPokemon(int(index))
        if ok:
            _clear_buffs_of(outgoing)
            switch_msg = f"  ↩️  {attacker_trainer.name} switched to {attacker_trainer.ActivePokemon.name}!"
            if log is not None:
                log.append(switch_msg)
            else:
                print(switch_msg)
        return True

    elif atype == "item":
        item_key     = action.get("item")
        target_index = action.get("target_index")
        if item_key is None:
            return True
        ok = attacker_trainer.UseItems(item_key, enemy_trainer=defender_trainer, in_battle=True, target_index=target_index)
        item_msg = (
            f"  ✨ {attacker_trainer.name} used {item_key}."
            if ok else
            f"  ❌ {attacker_trainer.name} failed to use {item_key}."
        )
        if log is not None:
            log.append(item_msg)
        else:
            print(item_msg)
        return True

    elif atype == "capture":
        if not is_wild:
            no_capture_msg = "  ❌ You can only throw Pokeballs in wild battles!"
            if log is not None:
                log.append(no_capture_msg)
            else:
                print(no_capture_msg)
            return True

        if len(attacker_trainer.team) >= 6:
            full_msg = "  ⚠️  Your team is full!"
            if log is not None:
                log.append(full_msg)
            else:
                print(full_msg)
            return True

        ball_key = action.get("ball")
        bag      = getattr(attacker_trainer, "bag", None)
        if not ball_key or bag is None or not bag.has_item(ball_key):
            no_ball_msg = "  ❌ You don't have that Pokeball."
            if log is not None:
                log.append(no_ball_msg)
            else:
                print(no_ball_msg)
            return True

        idef             = bag.get_definitions(ball_key) or {}
        catch_rate_mult  = float(idef.get("effect", {}).get("catch_rate_mult", 1.0))
        ball_name        = idef.get("name", ball_key)

        bag.remove_items(ball_key, 1)

        wild_pokemon = defender_trainer.ActivePokemon
        hp_ratio     = wild_pokemon.health / max(1, wild_pokemon.maximun_hp)
        base_rate    = 1.0 - (hp_ratio * 0.75)
        catch_rate   = min(0.95, base_rate * catch_rate_mult)

        throw_msg = f"  \U0001f3af {attacker_trainer.name} threw a {ball_name}!"
        if random.random() < catch_rate:
            attacker_trainer.team.append(wild_pokemon)
            catch_msg = f"  \U0001f389 Gotcha! {wild_pokemon.name} was caught!"
            if log is not None:
                log.append(throw_msg + "\n" + catch_msg)
            else:
                print(throw_msg)
                print(catch_msg)
            return "captured"
        else:
            break_msg = f"  \U0001f4a8 Oh no! {wild_pokemon.name} broke free!"
            if log is not None:
                log.append(throw_msg + "\n" + break_msg)
            else:
                print(throw_msg)
                print(break_msg)
            return True

    elif atype == "flee":
        setattr(attacker_trainer, "_fled", True)
        flee_msg = f"  \U0001f3c3 {attacker_trainer.name} fled the battle!"
        if log is not None:
            log.append(flee_msg)
        else:
            print(flee_msg)
        return False

    return True


# ─────────────────────── Main combat loop ───────────────────────

def pokemon_combat(
    trainer_a: Trainer,
    trainer_b: Trainer,
    *,
    pause_between_turns: bool = False,
    clear_between_turns: bool = False,
    wild: bool = False,
) -> Optional[str]:
    """Run a full battle. trainer_a = player, trainer_b = enemy (NPC or wild)."""

    for _t in (trainer_a, trainer_b):
        if hasattr(_t, "_fled"):
            _t._fled = False

    log: Deque[str] = collections.deque(maxlen=5)

    def redraw() -> None:
        _draw_battle_screen(trainer_b.ActivePokemon, trainer_a.ActivePokemon, list(log))

    xp = ExperienceManager()
    xp.start_battle()

    redraw()
    print("  ⚔️  BATTLE START!")
    input("  Press Enter to begin...")

    round_n = 1
    while True:
        # ── Check battle over before acting ──
        if not trainer_a.HasAvaliablePokemon():
            redraw()
            print(f"  \U0001f3c6 {trainer_b.name} wins!")
            try:
                for line in xp.finalize(trainer_b, trainer_a):
                    print(f"  {line}")
            finally:
                _cleanup_battle(trainer_a, trainer_b)
            return trainer_b.name

        if not trainer_b.HasAvaliablePokemon():
            redraw()
            print(f"  \U0001f3c6 {trainer_a.name} wins!")
            try:
                for line in xp.finalize(trainer_a, trainer_b):
                    print(f"  {line}")
            finally:
                _cleanup_battle(trainer_a, trainer_b)
            return trainer_a.name

        try:
            xp.on_turn_begin([trainer_a.ActivePokemon, trainer_b.ActivePokemon])
        except Exception:
            pass

        a_first, _ = determine_attack_order(trainer_a.ActivePokemon, trainer_b.ActivePokemon)
        first_trainer  = trainer_a if a_first is trainer_a.ActivePokemon else trainer_b
        second_trainer = trainer_b if first_trainer is trainer_a else trainer_a
        first_is_player = (first_trainer is trainer_a)

        # ── FIRST TRAINER ACTS ──
        if first_is_player:
            redraw()  # show state + log before player picks action
        result = _take_turn(
            first_trainer, second_trainer,
            xp_manager=xp,
            is_wild=(wild and first_is_player),
            log=log,
            redraw_fn=redraw,
        )

        if result == "captured":
            redraw()
            input("  Press Enter to continue...")
            _cleanup_battle(trainer_a, trainer_b)
            return "captured"

        if not result:
            redraw()
            fled = getattr(first_trainer, "_fled", False) or getattr(second_trainer, "_fled", False)
            if not fled:
                winner_tr = (
                    second_trainer
                    if not first_trainer.HasAvaliablePokemon() or getattr(first_trainer, "_fled", False)
                    else first_trainer
                )
                loser_tr = first_trainer if winner_tr is second_trainer else second_trainer
                print(f"  \U0001f3c6 {winner_tr.name} wins!")
                try:
                    for line in xp.finalize(winner_tr, loser_tr):
                        print(f"  {line}")
                except Exception:
                    pass
            input("  Press Enter to continue...")
            _cleanup_battle(trainer_a, trainer_b)
            return None if fled else winner_tr.name

        if not second_trainer.HasAvaliablePokemon():
            redraw()
            print(f"  \U0001f3c6 {first_trainer.name} wins!")
            try:
                for line in xp.finalize(first_trainer, second_trainer):
                    print(f"  {line}")
            except Exception:
                pass
            input("  Press Enter to continue...")
            _cleanup_battle(trainer_a, trainer_b)
            return first_trainer.name

        # ── SECOND TRAINER ACTS ──
        if not first_is_player:
            # Enemy went first — redraw before player picks action so player sees what enemy did
            redraw()
        result2 = _take_turn(
            second_trainer, first_trainer,
            xp_manager=xp,
            is_wild=(wild and not first_is_player),
            log=log,
            redraw_fn=redraw,
        )

        if result2 == "captured":
            redraw()
            input("  Press Enter to continue...")
            _cleanup_battle(trainer_a, trainer_b)
            return "captured"

        if not result2:
            redraw()
            fled = getattr(first_trainer, "_fled", False) or getattr(second_trainer, "_fled", False)
            if not fled:
                winner_tr = (
                    first_trainer
                    if not second_trainer.HasAvaliablePokemon() or getattr(second_trainer, "_fled", False)
                    else second_trainer
                )
                loser_tr = second_trainer if winner_tr is first_trainer else first_trainer
                print(f"  \U0001f3c6 {winner_tr.name} wins!")
                try:
                    for line in xp.finalize(winner_tr, loser_tr):
                        print(f"  {line}")
                except Exception:
                    pass
            input("  Press Enter to continue...")
            _cleanup_battle(trainer_a, trainer_b)
            return None if fled else winner_tr.name

        # ── End of round: show result and wait for player ──
        redraw()
        input("  Press Enter to continue...")

        round_n += 1
