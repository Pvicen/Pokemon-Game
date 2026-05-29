from __future__ import annotations

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
# ---------------------------------------------------------------------------
_RESET   = "\033[0m"
_BG_VOID = "\033[40m"   # fondo neutro fuera de zonas (corredores/transiciones)

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
_FG_NPC    = "\033[1;93m"    # amarillo brillante — NPC amistoso

# Viewport
_VP_W = 40
_VP_H = 20


def render_world2(player_pos: list, objects: list | None = None) -> None:
    px, py = player_pos
    obj_map = {(o["x"], o["y"]): o for o in (objects or [])}
    x0 = max(0, min(px - _VP_W // 2, WORLD2_MAP_WIDTH  - _VP_W))
    y0 = max(0, min(py - _VP_H // 2, WORLD2_MAP_HEIGHT - _VP_H))

    print("\033[2J\033[H", end="")
    border = "═" * (_VP_W + 2)
    print(f"  {_BG_VOID}╔{border}╗{_RESET}")

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
                line += f"{bg}{_FG_NPC}N{_RESET}"
            elif WORLD2_OBSTACLE_GRID[row][col] == "#":
                line += f"{bg}{_FG_WALL}#{_RESET}"
            else:
                line += f"{bg} {_RESET}"
        line += f"{_BG_VOID} ║{_RESET}"
        print(line)

    print(f"  {_BG_VOID}╚{border}╝{_RESET}")

    current_zone = get_zone_for_world2(px, py)
    zone_label = ZONE_NAMES.get(current_zone, "Sendero") if current_zone else "Sendero"
    print(f"  [WORLD 2 — {zone_label}]  [{px},{py}]  "
          f"WASD | E: bag | P: pokédex | T: team | Q: save | + centro | N npc | ▲ portal")
