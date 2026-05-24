from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import Pokemon

_R = "\033[0m"


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
