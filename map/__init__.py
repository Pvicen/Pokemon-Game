from .tiles    import OBSTACLE_GRID, MAP_WIDTH, MAP_HEIGHT, PLAYER_START_X, PLAYER_START_Y
from .player   import PlayerState
from .renderer import render
from .events   import check_collision
from ..game.setup_game import get_map_objects
from ..game.encounters import trigger_encounter, trigger_wild_encounter
from ..game.save_load import save_game

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


def run_map(player_trainer, *, start_pos=None, defeated_positions=None, slot_name="default"):
    import readchar

    sx = start_pos[0] if start_pos else PLAYER_START_X
    sy = start_pos[1] if start_pos else PLAYER_START_Y
    player  = PlayerState(start_x=sx, start_y=sy)

    defeated = list(defeated_positions) if defeated_positions else []
    defeated_set = {(x, y) for x, y in defeated}
    all_objects = get_map_objects()
    objects = [o for o in all_objects if (o["x"], o["y"]) not in defeated_set]

    end_game = False

    while not end_game:
        render(OBSTACLE_GRID, player.pos, objects)

        key = readchar.readchar()
        if isinstance(key, bytes):
            key = key.decode("utf-8", errors="ignore")

        if key == "q":
            save_game(player_trainer, player.pos[0], player.pos[1], defeated, slot_name)
            print("\n  Progress saved. See you!")
            end_game = True
            continue

        new_pos = player.get_new_position(key, MAP_WIDTH, MAP_HEIGHT)
        if new_pos is None:
            continue

        if OBSTACLE_GRID[new_pos[1]][new_pos[0]] != "#":
            if (new_pos[0], new_pos[1]) == POKEMON_CENTER_POS:
                _heal_at_pokemon_center(player_trainer)
                save_game(player_trainer, new_pos[0], new_pos[1], defeated, slot_name)
            else:
                hit = check_collision(new_pos, objects)
                if hit:
                    encountered = trigger_encounter(hit, player_trainer)
                    if encountered:
                        objects.remove(hit)
                        defeated.append((hit["x"], hit["y"]))
                    save_game(player_trainer, new_pos[0], new_pos[1], defeated, slot_name)
                else:
                    trigger_wild_encounter(new_pos[0], new_pos[1], player_trainer)
                    save_game(player_trainer, new_pos[0], new_pos[1], defeated, slot_name)
            player.apply_move(new_pos)
