from __future__ import annotations

from ..game.setup_game import get_dungeon_pn_objects, get_dungeon_pn_wild_marker_objects
from ..game.encounters import trigger_encounter, trigger_wild_encounter, trigger_wild_marker_encounter
from ..game.save_load import save_game
from ..game.ui_menus import open_bag_menu, open_pokedex, show_team_summary
from .player import PlayerState
from .events import check_collision
from .terminal import RESET, BG_DARK, VIEWPORT_W, VIEWPORT_H, render_frame

DUNGEON_PN_WIDTH  = 40
DUNGEON_PN_HEIGHT = 20
DUNGEON_PN_START  = (2, 2)
DUNGEON_PN_EXIT   = (2, 1)
OVERWORLD_RETURN_PN = (153, 61)

# ---------------------------------------------------------------------------
# Build dungeon_pn grid (40×20)
# ---------------------------------------------------------------------------
_G_PN = [["#"] * DUNGEON_PN_WIDTH for _ in range(DUNGEON_PN_HEIGHT)]


def _carve_pn(x1: int, y1: int, x2: int, y2: int) -> None:
    for y in range(max(0, y1), min(DUNGEON_PN_HEIGHT, y2 + 1)):
        for x in range(max(0, x1), min(DUNGEON_PN_WIDTH, x2 + 1)):
            _G_PN[y][x] = "."


# Entity positions verified on carved tiles:
# ▲ exit (2,1)  spawn (2,2)          → entry room
# Onix ! (8,3)  Nadia T (14,3)       → entry corridor
# Gengar ! (20,11)  Kyle T (25,10)   → middle room
# Champion Nexus T (35,16)           → champion chamber
_carve_pn(1,  1,  4,  3)   # Entry room
_carve_pn(4,  2,  18, 4)   # Entry corridor
_carve_pn(16, 2,  18, 12)  # Vertical shaft
_carve_pn(14, 10, 28, 13)  # Middle room
_carve_pn(26, 10, 28, 18)  # Deep vertical
_carve_pn(24, 16, 38, 18)  # Champion chamber

DUNGEON_PN_GRID = _G_PN

# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------
_RESET   = RESET
_BG      = BG_DARK
_WALL    = "\033[90m"
_FLOOR   = "\033[100m"
_PLAYER  = "\033[1;93m"
_TRAINER = "\033[1;91m"
_WILD    = "\033[1;92m"
_EXIT    = "\033[1;96m"

_VP_W = VIEWPORT_W
_VP_H = VIEWPORT_H


def _render_pn(player_pos: list, objects: list) -> None:
    px, py = player_pos
    x0 = max(0, min(px - _VP_W // 2, DUNGEON_PN_WIDTH  - _VP_W))
    y0 = max(0, min(py - _VP_H // 2, DUNGEON_PN_HEIGHT - _VP_H))

    obj_map = {(o["x"], o["y"]): o for o in objects}

    border = "═" * (_VP_W + 2)
    lines = [f"  {_BG}╔{border}╗{_RESET}"]

    for row in range(y0, y0 + _VP_H):
        line = f"  {_BG}║ "
        for col in range(x0, x0 + _VP_W):
            if not (0 <= row < DUNGEON_PN_HEIGHT and 0 <= col < DUNGEON_PN_WIDTH):
                line += f"{_WALL}#{_RESET}{_BG}"
            elif [col, row] == player_pos:
                line += f"{_PLAYER}@{_RESET}{_BG}"
            elif (col, row) == DUNGEON_PN_EXIT:
                line += f"{_EXIT}▲{_RESET}{_BG}"
            elif (col, row) in obj_map:
                obj = obj_map[(col, row)]
                sym = f"{_WILD}!{_RESET}{_BG}" if obj.get("kind") == "wild" else f"{_TRAINER}T{_RESET}{_BG}"
                line += sym
            elif DUNGEON_PN_GRID[row][col] == "#":
                line += f"{_WALL}#{_RESET}{_BG}"
            else:
                line += f"{_FLOOR} {_RESET}{_BG}"
        line += f" ║{_RESET}"
        lines.append(line)

    lines.append(f"  {_BG}╚{border}╝{_RESET}")
    lines.append(f"  [{px},{py}]  WASD: move | E: bag | P: pokédex | T: team | Q: save & quit | ▲(2,1) exit")
    render_frame(lines)


# ---------------------------------------------------------------------------
# Champion cinematic
# ---------------------------------------------------------------------------

def _champion_cinematic(player_trainer) -> None:
    print("\n" + "═" * 46)
    print("  The cave shakes as Champion Nexus falls...")
    print("  A deep silence fills the chamber.")
    lead = player_trainer.team[0]
    print(f"\n  {lead.name} lets out a triumphant cry!")
    print("\n  The legend of this cave has been rewritten.")
    print("  A new horizon stirs beyond the darkness...")
    print("═" * 46)
    input("  Press Enter to continue...")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def run_dungeon_pn(player_trainer, *, start_pos=None, defeated_dict=None,
                   cleared_markers_dict=None, slot_name="default", steps: int = 0) -> str:
    import readchar

    if defeated_dict is None:
        defeated_dict = {"main": [], "dungeon": [], "dungeon_pn": []}
    if cleared_markers_dict is None:
        cleared_markers_dict = {"main": [], "dungeon": [], "dungeon_pn": []}

    sx = start_pos[0] if start_pos else DUNGEON_PN_START[0]
    sy = start_pos[1] if start_pos else DUNGEON_PN_START[1]
    player = PlayerState(start_x=sx, start_y=sy)

    defeated_dungeon_pn  = list(defeated_dict.get("dungeon_pn", []))
    main_side            = list(defeated_dict.get("main",       []))
    dungeon_side         = list(defeated_dict.get("dungeon",    []))
    cleared_pn           = cleared_markers_dict.setdefault("dungeon_pn", [])
    cleared_main_ref     = cleared_markers_dict.setdefault("main",       [])
    cleared_dungeon_ref  = cleared_markers_dict.setdefault("dungeon",    [])

    defeated_set = (
        {(e[0], e[1]) for e in defeated_dungeon_pn} |
        {(e[0], e[1]) for e in cleared_pn}
    )

    all_objects = get_dungeon_pn_objects() + get_dungeon_pn_wild_marker_objects()
    objects = [o for o in all_objects if (o["x"], o["y"]) not in defeated_set]

    def _cur_dict():
        return {"main": main_side, "dungeon": dungeon_side, "dungeon_pn": defeated_dungeon_pn}

    while True:
        _render_pn(player.pos, objects)

        key = readchar.readchar()
        if isinstance(key, bytes):
            key = key.decode("utf-8", errors="ignore")

        if key == "q":
            save_game(player_trainer, player.pos[0], player.pos[1], slot_name,
                      current_map="dungeon_pn", defeated_dict=_cur_dict(),
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

        new_pos = player.get_new_position(key, DUNGEON_PN_WIDTH, DUNGEON_PN_HEIGHT)
        if new_pos is None:
            continue

        if DUNGEON_PN_GRID[new_pos[1]][new_pos[0]] != "#":
            if (new_pos[0], new_pos[1]) == DUNGEON_PN_EXIT:
                save_game(player_trainer, OVERWORLD_RETURN_PN[0], OVERWORLD_RETURN_PN[1], slot_name,
                          current_map="main", defeated_dict=_cur_dict(),
                          cleared_markers_dict=cleared_markers_dict, steps=steps)
                print("\n  You emerge from the depths of the cave...")
                input("  Press Enter to return to Pueblo Nuevo...")
                return "exit_pn"

            else:
                hit = check_collision(new_pos, objects)
                if hit:
                    if hit.get("kind") == "wild":
                        encountered = trigger_wild_marker_encounter(hit, player_trainer)
                        if encountered:
                            objects.remove(hit)
                            cleared_pn.append((hit["x"], hit["y"]))
                    else:
                        encountered = trigger_encounter(hit, player_trainer)
                        if encountered:
                            objects.remove(hit)
                            defeated_dungeon_pn.append((hit["x"], hit["y"], steps))
                            if hit.get("setup") and hit["setup"].name == "Champion Nexus":
                                save_game(player_trainer, new_pos[0], new_pos[1], slot_name,
                                          current_map="dungeon_pn", defeated_dict=_cur_dict(),
                                          cleared_markers_dict=cleared_markers_dict, steps=steps)
                                _champion_cinematic(player_trainer)
                                save_game(player_trainer,
                                          OVERWORLD_RETURN_PN[0], OVERWORLD_RETURN_PN[1], slot_name,
                                          current_map="main", defeated_dict=_cur_dict(),
                                          cleared_markers_dict=cleared_markers_dict, steps=steps,
                                          chapter2_unlocked=True)
                                print("\n  You emerge victorious from the depths...")
                                input("  Press Enter to return to Pueblo Nuevo...")
                                return "exit_pn"
                    save_game(player_trainer, new_pos[0], new_pos[1], slot_name,
                              current_map="dungeon_pn", defeated_dict=_cur_dict(),
                              cleared_markers_dict=cleared_markers_dict, steps=steps)
                else:
                    trigger_wild_encounter(new_pos[0], new_pos[1], player_trainer,
                                           zone_id="cueva_oscura")
                    save_game(player_trainer, new_pos[0], new_pos[1], slot_name,
                              current_map="dungeon_pn", defeated_dict=_cur_dict(),
                              cleared_markers_dict=cleared_markers_dict, steps=steps)

            player.apply_move(new_pos)
