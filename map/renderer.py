import os

from .tiles import TILE_WALL

VIEWPORT_W = 40
VIEWPORT_H = 20


def render(obstacle_grid, player_pos, objects):
    """Draws a VIEWPORT_W x VIEWPORT_H window of the map centered on the player."""
    os.system("cls")

    map_w = len(obstacle_grid[0])
    map_h = len(obstacle_grid)

    # Camera centered on player, clamped so it never goes out of map bounds
    cam_x = max(0, min(player_pos[0] - VIEWPORT_W // 2, map_w - VIEWPORT_W))
    cam_y = max(0, min(player_pos[1] - VIEWPORT_H // 2, map_h - VIEWPORT_H))

    object_map = {(o["x"], o["y"]): o for o in objects}

    print(" " + "_" * VIEWPORT_W * 2 + " ")

    for row in range(VIEWPORT_H):
        y = cam_y + row
        print("|", end="")
        for col in range(VIEWPORT_W):
            x = cam_x + col
            if obstacle_grid[y][x] == TILE_WALL:
                char = "##"
            elif player_pos[0] == x and player_pos[1] == y:
                char = " @"
            elif (x, y) in object_map:
                char = " !" if object_map[(x, y)].get("kind") == "wild" else " T"
            else:
                char = "  "
            print(char, end="")
        print("|")

    print(" " + "_" * VIEWPORT_W * 2 + " ")
    px, py = player_pos
    print(f"  Pos ({px:3d},{py:3d})  Cam ({cam_x:3d},{cam_y:3d})  |  WASD mover  Q salir")
