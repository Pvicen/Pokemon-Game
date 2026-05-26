from __future__ import annotations

from ..game.setup_game import get_dungeon_objects, get_dungeon_wild_marker_objects
from ..game.encounters import trigger_encounter, trigger_wild_encounter, trigger_wild_marker_encounter
from ..game.save_load import save_game
from ..game.ui_menus import open_bag_menu, open_pokedex, show_team_summary
from .player import PlayerState
from .events import check_collision

DUNGEON_WIDTH  = 60
DUNGEON_HEIGHT = 30
DUNGEON_START          = (3, 2)
DUNGEON_START_EAST     = (57, 26)
DUNGEON_EXIT_POS       = (3, 1)
DUNGEON_EXIT_EAST_POS  = (57, 27)
MAIN_MAP_RETURN_WEST   = (90, 26)
MAIN_MAP_RETURN_EAST   = (119, 47)

# ---------------------------------------------------------------------------
# Build dungeon grid
# ---------------------------------------------------------------------------
_G = [["#"] * DUNGEON_WIDTH for _ in range(DUNGEON_HEIGHT)]


def _carve(x1: int, y1: int, x2: int, y2: int) -> None:
    for y in range(max(0, y1), min(DUNGEON_HEIGHT, y2 + 1)):
        for x in range(max(0, x1), min(DUNGEON_WIDTH, x2 + 1)):
            _G[y][x] = "."


# All trainer/wild positions must land on carved tiles — verified by design:
# Geodude(8,5), Ryu(15,8): in top corridor
# Sara(25,14), Gastly(35,12): in middle sections
# Grunt(40,18), Deserter(20,22): in lower corridor
# Champion(45,26): in deep chamber
_carve(1, 1, 8,  4)    # Entry room — exit(3,1) and start(3,2)
_carve(5, 4, 25, 8)    # Top corridor — Geodude(8,5), Ryu(15,8)
_carve(20, 5, 22, 15)  # Vertical connector
_carve(15, 10, 32, 15) # Middle section — Sara(25,14)
_carve(30, 12, 45, 15) # Right section — Gastly(35,12)
_carve(38, 14, 42, 22) # Deep vertical — Grunt(40,18)
_carve(18, 18, 42, 22) # Lower corridor — Deserter(20,22)
_carve(38, 22, 52, 28) # Deep chamber — Champion(45,26)
_carve(52, 25, 58, 28) # East exit corridor — DUNGEON_EXIT_EAST_POS(57,27)

DUNGEON_GRID = _G

# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------
_RESET   = "\033[0m"
_BG      = "\033[40m"
_WALL    = "\033[90m"
_FLOOR   = "\033[100m"
_PLAYER  = "\033[1;93m"
_TRAINER = "\033[1;91m"
_WILD    = "\033[1;92m"
_EXIT    = "\033[1;96m"

_VP_W = 40
_VP_H = 20


def _render(player_pos: list, objects: list) -> None:
    px, py = player_pos
    x0 = max(0, min(px - _VP_W // 2, DUNGEON_WIDTH  - _VP_W))
    y0 = max(0, min(py - _VP_H // 2, DUNGEON_HEIGHT - _VP_H))

    obj_map = {(o["x"], o["y"]): o for o in objects}

    print("\033[2J\033[H", end="")
    border = "═" * (_VP_W + 2)
    print(f"  {_BG}╔{border}╗{_RESET}")

    for row in range(y0, y0 + _VP_H):
        line = f"  {_BG}║ "
        for col in range(x0, x0 + _VP_W):
            if not (0 <= row < DUNGEON_HEIGHT and 0 <= col < DUNGEON_WIDTH):
                line += f"{_WALL}#{_RESET}{_BG}"
            elif [col, row] == player_pos:
                line += f"{_PLAYER}@{_RESET}{_BG}"
            elif (col, row) == DUNGEON_EXIT_POS:
                line += f"{_EXIT}▲{_RESET}{_BG}"
            elif (col, row) == DUNGEON_EXIT_EAST_POS:
                line += f"{_EXIT}▲{_RESET}{_BG}"
            elif (col, row) in obj_map:
                obj = obj_map[(col, row)]
                sym = f"{_WILD}!{_RESET}{_BG}" if obj.get("kind") == "wild" else f"{_TRAINER}T{_RESET}{_BG}"
                line += sym
            elif DUNGEON_GRID[row][col] == "#":
                line += f"{_WALL}#{_RESET}{_BG}"
            else:
                line += f"{_FLOOR} {_RESET}{_BG}"
        line += f" ║{_RESET}"
        print(line)

    print(f"  {_BG}╚{border}╝{_RESET}")
    print(f"  [{px},{py}]  WASD: move | E: bag | P: pokédex | Q: save & quit | ▲(3,1) exit W  ▲(57,27) exit E")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def run_dungeon(player_trainer, *, start_pos=None, defeated_dict=None,
                cleared_markers_dict=None, slot_name="default", steps: int = 0) -> str:
    import readchar

    if defeated_dict is None:
        defeated_dict = {"main": [], "dungeon": [], "dungeon_pn": []}
    if cleared_markers_dict is None:
        cleared_markers_dict = {"main": [], "dungeon": [], "dungeon_pn": []}

    sx = start_pos[0] if start_pos else DUNGEON_START[0]
    sy = start_pos[1] if start_pos else DUNGEON_START[1]
    player = PlayerState(start_x=sx, start_y=sy)

    defeated_dungeon = list(defeated_dict.get("dungeon",    []))
    main_side        = list(defeated_dict.get("main",       []))
    dungeon_pn_side  = list(defeated_dict.get("dungeon_pn", []))
    cleared_dungeon  = cleared_markers_dict.setdefault("dungeon",    [])
    cleared_main_ref = cleared_markers_dict.setdefault("main",       [])
    cleared_pn_ref   = cleared_markers_dict.setdefault("dungeon_pn", [])

    defeated_set = (
        {(e[0], e[1]) for e in defeated_dungeon} |
        {(e[0], e[1]) for e in cleared_dungeon}
    )

    all_objects = get_dungeon_objects() + get_dungeon_wild_marker_objects()
    objects = [o for o in all_objects if (o["x"], o["y"]) not in defeated_set]

    def _cur_dict():
        return {"main": main_side, "dungeon": defeated_dungeon, "dungeon_pn": dungeon_pn_side}

    while True:
        _render(player.pos, objects)

        key = readchar.readchar()
        if isinstance(key, bytes):
            key = key.decode("utf-8", errors="ignore")

        if key == "q":
            save_game(player_trainer, player.pos[0], player.pos[1], slot_name,
                      current_map="dungeon", defeated_dict=_cur_dict(),
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

        new_pos = player.get_new_position(key, DUNGEON_WIDTH, DUNGEON_HEIGHT)
        if new_pos is None:
            continue

        if DUNGEON_GRID[new_pos[1]][new_pos[0]] != "#":
            # Exit tiles — return to overworld
            if (new_pos[0], new_pos[1]) == DUNGEON_EXIT_POS:
                save_game(player_trainer, MAIN_MAP_RETURN_WEST[0], MAIN_MAP_RETURN_WEST[1], slot_name,
                          current_map="main", defeated_dict=_cur_dict(),
                          cleared_markers_dict=cleared_markers_dict, steps=steps)
                print("\n  You climb out of the cave (west)...")
                input("  Press Enter to return to the overworld...")
                return "exit_west"

            elif (new_pos[0], new_pos[1]) == DUNGEON_EXIT_EAST_POS:
                save_game(player_trainer, MAIN_MAP_RETURN_EAST[0], MAIN_MAP_RETURN_EAST[1], slot_name,
                          current_map="main", defeated_dict=_cur_dict(),
                          cleared_markers_dict=cleared_markers_dict, steps=steps)
                print("\n  You emerge from the east side of the cave...")
                input("  Press Enter to continue...")
                return "exit_east"

            else:
                hit = check_collision(new_pos, objects)
                if hit:
                    if hit.get("kind") == "wild":
                        encountered = trigger_wild_marker_encounter(hit, player_trainer)
                        if encountered:
                            objects.remove(hit)
                            cleared_dungeon.append((hit["x"], hit["y"]))
                    else:
                        encountered = trigger_encounter(hit, player_trainer)
                        if encountered:
                            objects.remove(hit)
                            defeated_dungeon.append((hit["x"], hit["y"]))
                    save_game(player_trainer, new_pos[0], new_pos[1], slot_name,
                              current_map="dungeon", defeated_dict=_cur_dict(),
                              cleared_markers_dict=cleared_markers_dict, steps=steps)
                else:
                    trigger_wild_encounter(new_pos[0], new_pos[1], player_trainer,
                                           zone_id="cueva_oscura")
                    save_game(player_trainer, new_pos[0], new_pos[1], slot_name,
                              current_map="dungeon", defeated_dict=_cur_dict(),
                              cleared_markers_dict=cleared_markers_dict, steps=steps)

            player.apply_move(new_pos)
