from .tiles    import OBSTACLE_GRID, MAP_WIDTH, MAP_HEIGHT, PLAYER_START_X, PLAYER_START_Y
from .player   import PlayerState
from .renderer import render
from .events   import check_collision
from ..game.setup_game import get_map_objects, get_wild_marker_objects, WILD_MARKERS, TRAINERS
from ..game.encounters import trigger_encounter, trigger_wild_encounter, trigger_wild_marker_encounter
from ..game.save_load import save_game
from ..game.ui_menus import open_bag_menu, open_pokedex, show_team_summary
from ..game.respawn import check_respawn, _player_avg_level

POKEMON_CENTER_POS   = (9, 11)
POKEMON_CENTER_2_POS = (129, 46)
WORLD2_PORTAL_POS    = (140, 55)  # Fase Q1: portal a Mundo 2 (sólo activo si chapter2_unlocked=True)


# Cave boundary triggers — span the full corridor width
# West: player crosses y=28 anywhere in cols 87-92 (west entrance corridor)
# East: player crosses x=118 anywhere in rows 46-48 (deepest chamber east wall)


def _heal_at_pokemon_center(player_trainer) -> None:
    print("\n  ╔══════════════════════════════╗")
    print("  ║      POKEMON  CENTER         ║")
    print("  ╚══════════════════════════════╝")

    already_healthy = all(
        p.health >= p.maximun_hp and getattr(p, "status", None) is None
        for p in player_trainer.team
    )
    if already_healthy:
        print("\n  Nurse Joy: \"Your Pokemon are already in perfect health!\"")
        input("  Press Enter to continue...")
        return

    print("\n  Nurse Joy: \"Welcome! We'll heal your Pokemon to full health!\"")
    input("  ...")
    for p in player_trainer.team:
        p.health = p.maximun_hp
        p.restore_all_pp()
        p.clear_status()
    player_trainer.active_index = 0
    print("\n  Nurse Joy: \"Your Pokemon are fully healed. Have a great trip!\"")
    input("  Press Enter to continue...")


def run_map(player_trainer, *, start_pos=None, defeated_dict=None,
            cleared_markers_dict=None, slot_name="default", steps: int = 0,
            chapter2_unlocked: bool = False) -> str:
    import readchar

    if defeated_dict is None:
        defeated_dict = {"main": [], "dungeon": [], "dungeon_pn": []}
    if cleared_markers_dict is None:
        cleared_markers_dict = {"main": [], "dungeon": [], "dungeon_pn": []}

    # New games pass position (None, None) — a truthy tuple — so guard against
    # None coords, not just a falsy start_pos, before falling back to the spawn.
    sx = start_pos[0] if start_pos and start_pos[0] is not None else PLAYER_START_X
    sy = start_pos[1] if start_pos and start_pos[1] is not None else PLAYER_START_Y
    player = PlayerState(start_x=sx, start_y=sy)

    defeated_main   = list(defeated_dict.get("main",       []))
    dungeon_side    = list(defeated_dict.get("dungeon",    []))
    dungeon_pn_side = list(defeated_dict.get("dungeon_pn", []))
    cleared_main    = cleared_markers_dict.setdefault("main",       [])
    dungeon_mkrs    = cleared_markers_dict.setdefault("dungeon",    [])
    cleared_pn_mkrs = cleared_markers_dict.setdefault("dungeon_pn", [])

    defeated_set = (
        {(e[0], e[1]) for e in defeated_main} |
        {(e[0], e[1]) for e in cleared_main}
    )

    all_objects = get_map_objects() + get_wild_marker_objects()
    objects = [o for o in all_objects if (o["x"], o["y"]) not in defeated_set]

    def _cur_dict():
        return {"main": defeated_main, "dungeon": dungeon_side, "dungeon_pn": dungeon_pn_side}

    while True:
        render(OBSTACLE_GRID, player.pos, objects)

        key = readchar.readchar()
        if isinstance(key, bytes):
            key = key.decode("utf-8", errors="ignore")

        if key == "q":
            save_game(player_trainer, player.pos[0], player.pos[1], slot_name,
                      current_map="main", defeated_dict=_cur_dict(),
                      cleared_markers_dict=cleared_markers_dict, steps=steps)
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

        new_pos = player.get_new_position(key, MAP_WIDTH, MAP_HEIGHT)
        if new_pos is None:
            continue

        if OBSTACLE_GRID[new_pos[1]][new_pos[0]] != "#":
            # West cave entry: crossing south into cave (y=28, cols 87-92)
            if 87 <= new_pos[0] <= 92 and new_pos[1] == 28:
                save_game(player_trainer, 3, 2, slot_name,
                          current_map="dungeon", defeated_dict=_cur_dict(),
                          cleared_markers_dict=cleared_markers_dict, steps=steps)
                return "enter_dungeon"

            # East cave entry: crossing west into cave (x=118, rows 46-48)
            elif new_pos[0] == 118 and 46 <= new_pos[1] <= 48:
                save_game(player_trainer, 57, 26, slot_name,
                          current_map="dungeon", defeated_dict=_cur_dict(),
                          cleared_markers_dict=cleared_markers_dict, steps=steps)
                return "enter_dungeon"

            # Pueblo Nuevo end-game cave entry: crossing north into cave (y=62, cols 152-155)
            elif 152 <= new_pos[0] <= 155 and new_pos[1] == 62:
                save_game(player_trainer, 2, 2, slot_name,
                          current_map="dungeon_pn", defeated_dict=_cur_dict(),
                          cleared_markers_dict=cleared_markers_dict, steps=steps)
                return "enter_dungeon_pn"

            # Fase Q1: portal a Mundo 2, sólo si chapter2_unlocked
            elif (new_pos[0], new_pos[1]) == WORLD2_PORTAL_POS and chapter2_unlocked:
                save_game(player_trainer, new_pos[0], new_pos[1], slot_name,
                          current_map="main", defeated_dict=_cur_dict(),
                          cleared_markers_dict=cleared_markers_dict, steps=steps,
                          chapter2_unlocked=True)
                print("\n  A strange portal hums beneath your feet...")
                input("  Press Enter to step through into the new world...")
                return "travel_to_world2"

            elif (new_pos[0], new_pos[1]) == POKEMON_CENTER_2_POS:
                _heal_at_pokemon_center(player_trainer)
                save_game(player_trainer, new_pos[0], new_pos[1], slot_name,
                          current_map="main", defeated_dict=_cur_dict(),
                          cleared_markers_dict=cleared_markers_dict, steps=steps)

            elif (new_pos[0], new_pos[1]) == POKEMON_CENTER_POS:
                _heal_at_pokemon_center(player_trainer)
                save_game(player_trainer, new_pos[0], new_pos[1], slot_name,
                          current_map="main", defeated_dict=_cur_dict(),
                          cleared_markers_dict=cleared_markers_dict, steps=steps)

            else:
                hit = check_collision(new_pos, objects)
                if hit:
                    if hit.get("kind") == "wild":
                        encountered = trigger_wild_marker_encounter(hit, player_trainer)
                        if encountered:
                            objects.remove(hit)
                            cleared_main.append((hit["x"], hit["y"], steps))
                    else:
                        encountered = trigger_encounter(hit, player_trainer)
                        if encountered:
                            objects.remove(hit)
                            defeated_main.append((hit["x"], hit["y"], steps))
                    save_game(player_trainer, new_pos[0], new_pos[1], slot_name,
                              current_map="main", defeated_dict=_cur_dict(),
                              cleared_markers_dict=cleared_markers_dict, steps=steps)
                else:
                    trigger_wild_encounter(new_pos[0], new_pos[1], player_trainer)
                    save_game(player_trainer, new_pos[0], new_pos[1], slot_name,
                              current_map="main", defeated_dict=_cur_dict(),
                              cleared_markers_dict=cleared_markers_dict, steps=steps)

            player.apply_move(new_pos)
            steps += 1
            check_respawn(steps, player_trainer, cleared_main, defeated_main,
                          objects, WILD_MARKERS, TRAINERS)
