from .tiles    import OBSTACLE_GRID, MAP_WIDTH, MAP_HEIGHT, PLAYER_START_X, PLAYER_START_Y
from .player   import PlayerState
from .renderer import render
from .events   import check_collision
from ..game.setup_game import get_map_objects, get_wild_marker_objects
from ..game.encounters import trigger_encounter, trigger_wild_encounter, trigger_wild_marker_encounter
from ..game.save_load import save_game
from ..game.ui_menus import open_bag_menu, open_pokedex

POKEMON_CENTER_POS = (9, 11)


def _heal_at_pokemon_center(player_trainer) -> None:
    print("\n  ╔══════════════════════════════╗")
    print("  ║      POKEMON  CENTER         ║")
    print("  ╚══════════════════════════════╝")

    already_healthy = all(p.health >= p.maximun_hp for p in player_trainer.team)
    if already_healthy:
        print("\n  Nurse Joy: \"Your Pokemon are already in perfect health!\"")
        input("  Press Enter to continue...")
        return

    print("\n  Nurse Joy: \"Welcome! We'll heal your Pokemon to full health!\"")
    input("  ...")
    for p in player_trainer.team:
        p.health = p.maximun_hp
    player_trainer.active_index = 0
    print("\n  Nurse Joy: \"Your Pokemon are fully healed. Have a great trip!\"")
    input("  Press Enter to continue...")


def run_map(player_trainer, *, start_pos=None, defeated_dict=None, slot_name="default") -> str:
    import readchar

    if defeated_dict is None:
        defeated_dict = {"main": [], "dungeon": []}

    sx = start_pos[0] if start_pos else PLAYER_START_X
    sy = start_pos[1] if start_pos else PLAYER_START_Y
    player = PlayerState(start_x=sx, start_y=sy)

    defeated_main = list(defeated_dict.get("main", []))
    defeated_set  = {(x, y) for x, y in defeated_main}
    dungeon_side  = list(defeated_dict.get("dungeon", []))

    all_objects = get_map_objects() + get_wild_marker_objects()
    objects = [o for o in all_objects if (o["x"], o["y"]) not in defeated_set]

    def _cur_dict():
        return {"main": defeated_main, "dungeon": dungeon_side}

    while True:
        render(OBSTACLE_GRID, player.pos, objects)

        key = readchar.readchar()
        if isinstance(key, bytes):
            key = key.decode("utf-8", errors="ignore")

        if key == "q":
            save_game(player_trainer, player.pos[0], player.pos[1], slot_name,
                      current_map="main", defeated_dict=_cur_dict())
            print("\n  Progress saved. See you!")
            return "quit"

        if key in ("e", "E"):
            open_bag_menu(player_trainer)
            continue

        if key in ("p", "P"):
            open_pokedex(player_trainer)
            continue

        new_pos = player.get_new_position(key, MAP_WIDTH, MAP_HEIGHT)
        if new_pos is None:
            continue

        if OBSTACLE_GRID[new_pos[1]][new_pos[0]] != "#":
            # Cave entrance — transition to dungeon
            if new_pos[0] >= 87 and new_pos[1] >= 28:
                save_game(player_trainer, 3, 2, slot_name,
                          current_map="dungeon", defeated_dict=_cur_dict())
                return "enter_dungeon"

            elif (new_pos[0], new_pos[1]) == POKEMON_CENTER_POS:
                _heal_at_pokemon_center(player_trainer)
                save_game(player_trainer, new_pos[0], new_pos[1], slot_name,
                          current_map="main", defeated_dict=_cur_dict())

            else:
                hit = check_collision(new_pos, objects)
                if hit:
                    if hit.get("kind") == "wild":
                        encountered = trigger_wild_marker_encounter(hit, player_trainer)
                    else:
                        encountered = trigger_encounter(hit, player_trainer)
                    if encountered:
                        objects.remove(hit)
                        defeated_main.append((hit["x"], hit["y"]))
                    save_game(player_trainer, new_pos[0], new_pos[1], slot_name,
                              current_map="main", defeated_dict=_cur_dict())
                else:
                    trigger_wild_encounter(new_pos[0], new_pos[1], player_trainer)
                    save_game(player_trainer, new_pos[0], new_pos[1], slot_name,
                              current_map="main", defeated_dict=_cur_dict())

            player.apply_move(new_pos)
