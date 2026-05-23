import os

from .tiles import TILE_WALL

VIEWPORT_W = 40
VIEWPORT_H = 20

# Enable ANSI escape codes on Windows (no-op on other systems)
os.system("")

_R = "\033[0m"  # reset


def _color(x: int, y: int, tile: str) -> str:
    """Returns the tile string with ANSI color codes applied.
    Colors are applied AFTER viewport clipping so len() calculations
    on raw chars are never affected by invisible escape sequences."""
    if tile == "##":
        return f"\033[90m##\033[0m"          # dark gray walls
    if tile == " @":
        return f"{_zone_fg(x, y)}\033[93m @\033[0m"   # bright yellow player
    if tile == " T":
        return f"{_zone_fg(x, y)}\033[96m T\033[0m"   # cyan trainer
    if tile == " !":
        return f"{_zone_fg(x, y)}\033[95m !\033[0m"   # magenta wild pokemon
    # Empty floor — background tint by zone
    return f"{_zone_bg(x, y)}  \033[0m"


def _zone_bg(x: int, y: int) -> str:
    if x >= 87 and y >= 24:           return "\033[100m"   # Cueva Oscura: dark gray
    if x >= 44 and y <= 27:           return "\033[40m"    # Bosque Umbral: black bg
    if y <= 27:                       return "\033[44m"    # Pueblo Alto: blue bg
    return "\033[42m"                                      # Pueblo Raiz: green bg


def _zone_fg(x: int, y: int) -> str:
    if x >= 87 and y >= 24:           return "\033[100m"
    if x >= 44 and y <= 27:           return "\033[40m"
    if y <= 27:                       return "\033[44m"
    return "\033[42m"


def render(obstacle_grid, player_pos, objects):
    """Draws a VIEWPORT_W x VIEWPORT_H window of the map centered on the player."""
    os.system("cls")

    map_w = len(obstacle_grid[0])
    map_h = len(obstacle_grid)

    cam_x = max(0, min(player_pos[0] - VIEWPORT_W // 2, map_w - VIEWPORT_W))
    cam_y = max(0, min(player_pos[1] - VIEWPORT_H // 2, map_h - VIEWPORT_H))

    object_map = {(o["x"], o["y"]): o for o in objects}

    print(" " + "_" * VIEWPORT_W * 2 + " ")

    for row in range(VIEWPORT_H):
        y = cam_y + row
        print("|", end="")
        for col in range(VIEWPORT_W):
            x = cam_x + col
            # Determine raw tile type (no ANSI yet — viewport clipping uses raw chars)
            if obstacle_grid[y][x] == TILE_WALL:
                raw = "##"
            elif player_pos[0] == x and player_pos[1] == y:
                raw = " @"
            elif (x, y) in object_map:
                raw = " !" if object_map[(x, y)].get("kind") == "wild" else " T"
            else:
                raw = "  "
            # Apply ANSI color AFTER determining the tile (safe for viewport math)
            print(_color(x, y, raw), end="")
        print("|")

    print(" " + "_" * VIEWPORT_W * 2 + " ")
    px, py = player_pos
    print(f"  Pos ({px:3d},{py:3d})  Cam ({cam_x:3d},{cam_y:3d})  |  WASD mover  Q salir  E bolsa")
