from __future__ import annotations

from ...game.save_load import save_game
from ...game.setup_game import get_world2_objects
from ...game.encounters import trigger_encounter, trigger_wild_encounter
from ...game.ui_menus import open_bag_menu, open_pokedex, show_team_summary
from .. import _heal_at_pokemon_center
from ..player import PlayerState
from ..events import check_collision
from .tiles import (
    WORLD2_OBSTACLE_GRID,
    WORLD2_MAP_WIDTH,
    WORLD2_MAP_HEIGHT,
    WORLD2_PLAYER_START,
    WORLD2_RETURN_PORTAL,
    WORLD2_PC_POS,
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

    # NPCs ya visitados desaparecen (one-shot, igual que los friendly del World 1)
    defeated_world2 = list(defeated_dict.get("world2_main", []))
    defeated_set = {(e[0], e[1]) for e in defeated_world2}
    objects = [o for o in get_world2_objects() if (o["x"], o["y"]) not in defeated_set]

    def _cur_dict():
        return {"world2_main": defeated_world2}

    def _save(px: int, py: int) -> None:
        save_game(player_trainer, px, py, slot_name,
                  current_map="world2_main", defeated_dict=_cur_dict(),
                  cleared_markers_dict=cleared_markers_dict, steps=steps,
                  chapter2_unlocked=chapter2_unlocked,
                  world2_completed=world2_completed,
                  current_world="world2")

    while True:
        render_world2(player.pos, objects)

        key = readchar.readchar()
        if isinstance(key, bytes):
            key = key.decode("utf-8", errors="ignore")

        if key == "q":
            _save(player.pos[0], player.pos[1])
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
                _save(new_pos[0], new_pos[1])
                print("\n  The portal hums and the air shimmers...")
                input("  Press Enter to return to your home world...")
                return "travel_to_world1"

            elif (new_pos[0], new_pos[1]) == WORLD2_PC_POS:
                _heal_at_pokemon_center(player_trainer)
                _save(new_pos[0], new_pos[1])

            else:
                hit = check_collision(new_pos, objects)
                if hit:
                    # Q3: todos los NPCs de World 2 son amistosos (diálogo + regalo, one-shot)
                    encountered = trigger_encounter(hit, player_trainer)
                    if encountered:
                        objects.remove(hit)
                        defeated_world2.append((hit["x"], hit["y"], steps))
                    _save(new_pos[0], new_pos[1])
                else:
                    # Q3 scaffolding: las zonas aún no tienen wild_pokemons → inerte hasta Q4
                    trigger_wild_encounter(new_pos[0], new_pos[1], player_trainer,
                                           world_id="world2")
                    _save(new_pos[0], new_pos[1])

            player.apply_move(new_pos)
            steps += 1
