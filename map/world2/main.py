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

_RESET   = "\033[0m"
_BG      = "\033[40m"
_WALL    = "\033[90m"
_FLOOR   = "\033[47m"
_PLAYER  = "\033[1;93m"
_EXIT    = "\033[1;96m"

_VP_W = WORLD2_MAP_WIDTH
_VP_H = WORLD2_MAP_HEIGHT


def _render_world2(player_pos: list) -> None:
    px, py = player_pos
    print("\033[2J\033[H", end="")
    border = "═" * (_VP_W + 2)
    print(f"  {_BG}╔{border}╗{_RESET}")

    for row in range(_VP_H):
        line = f"  {_BG}║ "
        for col in range(_VP_W):
            if [col, row] == player_pos:
                line += f"{_PLAYER}@{_RESET}{_BG}"
            elif (col, row) == WORLD2_RETURN_PORTAL:
                line += f"{_EXIT}▲{_RESET}{_BG}"
            elif WORLD2_OBSTACLE_GRID[row][col] == "#":
                line += f"{_WALL}#{_RESET}{_BG}"
            else:
                line += f"{_FLOOR} {_RESET}{_BG}"
        line += f" ║{_RESET}"
        print(line)

    print(f"  {_BG}╚{border}╝{_RESET}")
    print(f"  [WORLD 2 — STUB]  [{px},{py}]  WASD: move | E: bag | P: pokédex | T: team | Q: save & quit | ▲(2,2) return")


def run_world2_map(player_trainer, *, start_pos=None, defeated_dict=None,
                   cleared_markers_dict=None, slot_name: str = "default",
                   steps: int = 0, chapter2_unlocked: bool = True,
                   world2_completed: bool = False) -> str:
    import readchar

    if defeated_dict is None:
        defeated_dict = {"world2_main": []}
    if cleared_markers_dict is None:
        cleared_markers_dict = {"world2_main": []}

    sx = start_pos[0] if start_pos and start_pos[0] is not None else WORLD2_PLAYER_START[0]
    sy = start_pos[1] if start_pos and start_pos[1] is not None else WORLD2_PLAYER_START[1]
    player = PlayerState(start_x=sx, start_y=sy)

    while True:
        _render_world2(player.pos)

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
