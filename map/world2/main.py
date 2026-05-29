from __future__ import annotations

import dataclasses

from ...game.save_load import save_game
from ...game.setup_game import (
    get_world2_objects, get_world2_wild_marker_objects,
    WORLD2_TRAINERS, WORLD2_WILD_MARKERS,
)
from ...game.encounters import (
    trigger_encounter, trigger_wild_encounter, trigger_wild_marker_encounter,
)
from ...game.ui_menus import open_bag_menu, open_pokedex, show_team_summary
from .. import _heal_at_pokemon_center, _player_avg_level
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
    """Validates start_pos against the 120×50 map. Falls back to spawn if invalid.

    Why: pre-Q2 saves may carry a position (e.g. (3,3)) that lands on a wall in the
    new map. Without this guard the player would spawn stuck inside a wall.
    """
    if start_pos and start_pos[0] is not None and start_pos[1] is not None:
        sx, sy = int(start_pos[0]), int(start_pos[1])
        if 0 <= sx < WORLD2_MAP_WIDTH and 0 <= sy < WORLD2_MAP_HEIGHT \
                and WORLD2_OBSTACLE_GRID[sy][sx] != "#":
            return sx, sy
    return WORLD2_PLAYER_START


def _check_respawn_world2(steps, player_trainer, cleared_w2, defeated_w2, objects) -> None:
    """Réplica del patrón de _check_respawn (World 1): wild markers a los 100 pasos,
    rematches de entrenadores a los 300, equipo escalado con dataclasses.replace().

    Diferencia con World 1: el rematch se filtra a posiciones de WORLD2_TRAINERS. Así
    el jefe (is_boss) y los NPCs (is_friendly) nunca reaparecen — son one-shot. Sin este
    filtro, el Echo Guardian volvería a aparecer tras 300 pasos al recargar el save.
    """
    # Wild markers — cooldown individual de 100 pasos
    to_restore = [
        (e[0], e[1]) for e in cleared_w2
        if steps - (e[2] if len(e) > 2 else 0) >= 100
    ]
    for pos in to_restore:
        cleared_w2[:] = [e for e in cleared_w2 if (e[0], e[1]) != pos]
        for marker in WORLD2_WILD_MARKERS:
            if (marker.position[0], marker.position[1]) == pos:
                objects.append({"x": pos[0], "y": pos[1], "kind": "wild",
                                "name": marker.name, "level": marker.level})
                break

    # Trainer rematches — cooldown individual de 300 pasos (solo entrenadores regulares)
    rematch_positions = {
        (t.position[0], t.position[1]): t for t in WORLD2_TRAINERS
        if not t.is_friendly and not t.is_boss
    }
    to_rematch = [
        (e[0], e[1]) for e in defeated_w2
        if (e[0], e[1]) in rematch_positions
        and steps - (e[2] if len(e) > 2 else 0) >= 300
    ]
    if to_rematch:
        avg = _player_avg_level(player_trainer)
        for pos in to_rematch:
            defeated_w2[:] = [e for e in defeated_w2 if (e[0], e[1]) != pos]
            t = rematch_positions[pos]
            scaled_team = [(name, max(orig_lv + 2, avg)) for name, orig_lv in t.team]
            scaled_setup = dataclasses.replace(t, team=scaled_team)
            objects.append({"x": pos[0], "y": pos[1], "kind": "trainer", "setup": scaled_setup})


def _chapter2_complete_cinematic(player_trainer) -> None:
    print("\n" + "═" * 52)
    print("  The Echo Guardian kneels, and the temple falls silent.")
    print("  Light pours from the ancient stones, washing over the chamber.")
    lead = player_trainer.team[0] if player_trainer.team else None
    if lead is not None:
        print(f"\n  {lead.name} stands beside you, victorious.")
    print("\n  The echoes of a thousand champions whisper your name.")
    print("  You have conquered the new world — Chapter 2 is complete.")
    print("\n  ...Yet the world remains open. Explore, train, and grow stronger.")
    print("═" * 52)
    input("  Press Enter to continue...")


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

    # Entidades ya derrotadas/tocadas no se vuelven a colocar (one-shot + respawn por pasos)
    defeated_world2 = list(defeated_dict.get("world2_main", []))
    cleared_world2 = cleared_markers_dict.setdefault("world2_main", [])
    done_set = ({(e[0], e[1]) for e in defeated_world2} |
                {(e[0], e[1]) for e in cleared_world2})
    all_objects = get_world2_objects() + get_world2_wild_marker_objects()
    objects = [o for o in all_objects if (o["x"], o["y"]) not in done_set]

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
                    if hit.get("kind") == "wild":
                        encountered = trigger_wild_marker_encounter(hit, player_trainer)
                        if encountered:
                            objects.remove(hit)
                            cleared_world2.append((hit["x"], hit["y"], steps))
                    else:
                        setup = hit.get("setup")
                        encountered = trigger_encounter(hit, player_trainer)
                        if encountered:
                            objects.remove(hit)
                            defeated_world2.append((hit["x"], hit["y"], steps))
                            if setup is not None and getattr(setup, "is_boss", False):
                                world2_completed = True
                                _chapter2_complete_cinematic(player_trainer)
                    _save(new_pos[0], new_pos[1])
                else:
                    # Encuentros salvajes por zona (Q4: zonas llenas → ahora sí dispara)
                    trigger_wild_encounter(new_pos[0], new_pos[1], player_trainer,
                                           world_id="world2")
                    _save(new_pos[0], new_pos[1])

            player.apply_move(new_pos)
            steps += 1
            _check_respawn_world2(steps, player_trainer, cleared_world2,
                                  defeated_world2, objects)
