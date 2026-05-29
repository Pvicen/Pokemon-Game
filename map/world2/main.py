from __future__ import annotations

from ...game.save_load import save_game
from ...game.ui_menus import open_bag_menu, open_pokedex, show_team_summary
from ..player import PlayerState
from .tiles import (
    WORLD2_OBSTACLE_GRID,
    WORLD2_MAP_WIDTH,
    WORLD2_MAP_HEIGHT,
    WORLD2_PLAYER_START,
    WORLD2_RETURN_PORTAL,
)
from .renderer import render_world2


def _safe_start(start_pos) -> tuple[int, int]:
    """Validates start_pos against the new 120×50 map. Falls back to spawn if invalid.

    Why: pre-Q2 saves may carry a position (e.g. (3,3)) that lands on a wall in the
    new map. Without this guard the player would spawn stuck inside a wall.
    """
    if start_pos and start_pos[0] is not None and start_pos[1] is not None:
        sx, sy = int(start_pos[0]), int(start_pos[1])
        if 0 <= sx < WORLD2_MAP_WIDTH and 0 <= sy < WORLD2_MAP_HEIGHT \
                and WORLD2_OBSTACLE_GRID[sy][sx] != "#":
            return sx, sy
    return WORLD2_PLAYER_START


def run_world2_map(player_trainer, *, start_pos=None, defeated_dict=None,
                   cleared_markers_dict=None, slot_name: str = "default",
                   steps: int = 0, chapter2_unlocked: bool = True,
                   world2_completed: bool = False) -> str:
    import readchar

    if defeated_dict is None:
        defeated_dict = {"world2_main": []}
    if cleared_markers_dict is None:
        cleared_markers_dict = {"world2_main": []}

    sx, sy = _safe_start(start_pos)
    player = PlayerState(start_x=sx, start_y=sy)

    while True:
        render_world2(player.pos)

        key = readchar.readchar()
        if isinstance(key, bytes):
            key = key.decode("utf-8", errors="ignore")

        if key == "q":
            save_game(player_trainer, player.pos[0], player.pos[1], slot_name,
                      current_map="world2_main", defeated_dict=defeated_dict,
                      cleared_markers_dict=cleared_markers_dict, steps=steps,
                      chapter2_unlocked=chapter2_unlocked,
                      world2_completed=world2_completed,
                      current_world="world2")
            print("\n  Progress saved. See you!")
            return "quit"

        if key in ("e", "E"):
            open_bag_menu(player_trainer)
            continue
        if key in ("p", "P"):
            open_pokedex(player_trainer)
            continue
        if key in ("t", "T"):
            show_team_summary(player_trainer)
            continue

        new_pos = player.get_new_position(key, WORLD2_MAP_WIDTH, WORLD2_MAP_HEIGHT)
        if new_pos is None:
            continue

        if WORLD2_OBSTACLE_GRID[new_pos[1]][new_pos[0]] != "#":
            if (new_pos[0], new_pos[1]) == WORLD2_RETURN_PORTAL:
                save_game(player_trainer, new_pos[0], new_pos[1], slot_name,
                          current_map="world2_main", defeated_dict=defeated_dict,
                          cleared_markers_dict=cleared_markers_dict, steps=steps,
                          chapter2_unlocked=chapter2_unlocked,
                          world2_completed=world2_completed,
                          current_world="world2")
                print("\n  The portal hums and the air shimmers...")
                input("  Press Enter to return to your home world...")
                return "travel_to_world1"

            player.apply_move(new_pos)
            steps += 1
            save_game(player_trainer, player.pos[0], player.pos[1], slot_name,
                      current_map="world2_main", defeated_dict=defeated_dict,
                      cleared_markers_dict=cleared_markers_dict, steps=steps,
                      chapter2_unlocked=chapter2_unlocked,
                      world2_completed=world2_completed,
                      current_world="world2")
