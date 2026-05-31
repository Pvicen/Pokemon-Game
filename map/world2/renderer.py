from __future__ import annotations

from ..terminal import RESET, BG_DARK, VIEWPORT_W, VIEWPORT_H, render_frame
from .tiles import (
    WORLD2_OBSTACLE_GRID,
    WORLD2_MAP_WIDTH,
    WORLD2_MAP_HEIGHT,
    WORLD2_RETURN_PORTAL,
    WORLD2_PC_POS,
    ZONE_NAMES,
    get_zone_for_world2,
)

# ---------------------------------------------------------------------------
# ANSI palette — independiente del renderer del Mundo 1
# (reset y fondo neutro consolidados en map/terminal.py — Propuesta R4)
# ---------------------------------------------------------------------------
_RESET   = RESET
_BG_VOID = BG_DARK        # fondo neutro fuera de zonas (corredores/transiciones)

_BG_AURORA = "\033[106m"  # cyan brillante  — Aldea Aurora
_BG_BOSQUE = "\033[42m"   # verde oscuro    — Bosque Milenario
_BG_MESETA = "\033[43m"   # amarillo/marrón — Meseta Ventosa
_BG_LAGO   = "\033[44m"   # azul oscuro     — Lago Cristal
_BG_TEMPLO = "\033[100m"  # gris oscuro     — Templo Eco

_BG_BY_ZONE = {
    "aurora": _BG_AURORA,
    "bosque": _BG_BOSQUE,
    "meseta": _BG_MESETA,
    "lago":   _BG_LAGO,
    "templo": _BG_TEMPLO,
}

_FG_WALL   = "\033[30m"      # negro — buena legibilidad sobre los 5 fondos
_FG_PLAYER = "\033[1;97m"    # blanco brillante
_FG_PORTAL = "\033[1;91m"    # rojo brillante
_FG_PC     = "\033[1;92m"    # verde brillante — Centro Pokémon (contrasta con fondo cyan)
_FG_NPC    = "\033[1;93m"    # amarillo brillante — NPC amistoso / entrenador
_FG_WILD   = "\033[1;95m"    # magenta brillante — wild marker
_FG_BOSS   = "\033[1;96m"    # cyan brillante — jefe final (Echo Guardian)

# Viewport
_VP_W = VIEWPORT_W
_VP_H = VIEWPORT_H


def render_world2(player_pos: list, objects: list | None = None) -> None:
    px, py = player_pos
    obj_map = {(o["x"], o["y"]): o for o in (objects or [])}
    x0 = max(0, min(px - _VP_W // 2, WORLD2_MAP_WIDTH  - _VP_W))
    y0 = max(0, min(py - _VP_H // 2, WORLD2_MAP_HEIGHT - _VP_H))

    border = "═" * (_VP_W + 2)
    lines = [f"  {_BG_VOID}╔{border}╗{_RESET}"]

    for row in range(y0, y0 + _VP_H):
        line = f"  {_BG_VOID}║ "
        for col in range(x0, x0 + _VP_W):
            if not (0 <= row < WORLD2_MAP_HEIGHT and 0 <= col < WORLD2_MAP_WIDTH):
                line += f"{_BG_VOID}{_FG_WALL}#{_RESET}"
                continue
            zone = get_zone_for_world2(col, row)
            bg = _BG_BY_ZONE.get(zone, _BG_VOID)
            if [col, row] == player_pos:
                line += f"{bg}{_FG_PLAYER}@{_RESET}"
            elif (col, row) == WORLD2_RETURN_PORTAL:
                line += f"{bg}{_FG_PORTAL}▲{_RESET}"
            elif (col, row) == WORLD2_PC_POS:
                line += f"{bg}{_FG_PC}+{_RESET}"
            elif (col, row) in obj_map:
                o = obj_map[(col, row)]
                if o.get("kind") == "wild":
                    line += f"{bg}{_FG_WILD}!{_RESET}"
                elif o.get("setup") is not None and getattr(o["setup"], "is_boss", False):
                    line += f"{bg}{_FG_BOSS}★{_RESET}"
                else:
                    line += f"{bg}{_FG_NPC}N{_RESET}"
            elif WORLD2_OBSTACLE_GRID[row][col] == "#":
                line += f"{bg}{_FG_WALL}#{_RESET}"
            else:
                line += f"{bg} {_RESET}"
        line += f"{_BG_VOID} ║{_RESET}"
        lines.append(line)

    lines.append(f"  {_BG_VOID}╚{border}╝{_RESET}")

    current_zone = get_zone_for_world2(px, py)
    zone_label = ZONE_NAMES.get(current_zone, "Sendero") if current_zone else "Sendero"
    lines.append(f"  [WORLD 2 — {zone_label}]  [{px},{py}]  "
                 f"WASD | E | P | T | Q | + centro | N npc/entren. | ! salvaje | ★ jefe | ▲ portal")
    render_frame(lines)
