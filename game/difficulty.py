"""Global difficulty state for the game session (Paquete 2 · P1.B).

A single source of truth, set ONCE when a game is created or loaded (in
``main.py``), and read by combat / experience / save_load. This avoids
threading a ``difficulty`` argument through the whole
``main → run_* → trigger_* → pokemon_combat → _take_turn`` call chain.

Design (asymmetric, the genre standard):
- ``enemy_damage``  scales ONLY the damage the IA-controlled side inflicts on
  the player. The player's own damage is never penalised.
- ``xp``            scales the XP pool awarded to the winning team.
- ``ai_status_chance`` is the probability that the IA tries to land a pure
  status move (Toxic / Thunder Wave / Sleep Powder) when the target has no
  status yet (Propuesta Q1 — combate táctico).
"""
from __future__ import annotations

DIFFICULTY_PRESETS = {
    "easy":   {"enemy_damage": 0.75, "xp": 1.25, "ai_status_chance": 0.10},
    "normal": {"enemy_damage": 1.00, "xp": 1.00, "ai_status_chance": 0.20},
    "hard":   {"enemy_damage": 1.30, "xp": 0.85, "ai_status_chance": 0.45},
}

DEFAULT_DIFFICULTY = "normal"

_LABELS = {"easy": "Easy", "normal": "Normal", "hard": "Hard"}

_current = DEFAULT_DIFFICULTY


def set_difficulty(name: str | None) -> str:
    """Set the active difficulty. Unknown/None values fall back to normal."""
    global _current
    key = str(name or "").strip().lower()
    _current = key if key in DIFFICULTY_PRESETS else DEFAULT_DIFFICULTY
    return _current


def current() -> str:
    return _current


def _preset() -> dict:
    return DIFFICULTY_PRESETS.get(_current, DIFFICULTY_PRESETS[DEFAULT_DIFFICULTY])


def enemy_damage_multiplier() -> float:
    return float(_preset()["enemy_damage"])


def xp_multiplier() -> float:
    return float(_preset()["xp"])


def ai_status_chance() -> float:
    return float(_preset()["ai_status_chance"])


def label(name: str | None = None) -> str:
    """Human-readable label for menus / messages."""
    key = str(name if name is not None else _current).strip().lower()
    return _LABELS.get(key, "Normal")
