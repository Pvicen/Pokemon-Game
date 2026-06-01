"""Unified respawn / rematch logic shared by every world (Paquete 3 · R1).

Both World 1 (`map/__init__.py`) and World 2 (`map/world2/main.py`) used to carry
near-identical `_check_respawn` functions. This module centralises them:

- Wild markers respawn after ``MARKER_RESPAWN_STEPS`` (100) steps.
- Trainers re-challenge after ``TRAINER_REMATCH_STEPS`` (300) steps with a
  level-scaled team.

The ``is_boss`` filter is generalised here: friendly NPCs (``is_friendly``) and
bosses (``is_boss``) are never re-added, so the Echo Guardian and one-shot NPCs
never reappear. This also fixes a latent World 1 bug where a friendly NPC's entry
was popped from ``defeated`` after 300 steps (it could reappear on the next save
reload) — now only rematcheable trainers are ever removed from ``defeated``.

This module has NO project imports (only ``dataclasses``); it receives the marker
and trainer setup lists as arguments, so it never creates a game↔map cycle.
"""
from __future__ import annotations

import dataclasses

MARKER_RESPAWN_STEPS = 100
TRAINER_REMATCH_STEPS = 300


def _player_avg_level(player_trainer) -> int:
    if not player_trainer.team:
        return 5
    levels = [int(getattr(p, "current_level", getattr(p, "level", 1)))
              for p in player_trainer.team]
    return max(1, round(sum(levels) / len(levels)))


def check_respawn(steps, player_trainer, cleared_list, defeated_list, objects,
                  wild_markers, trainers) -> None:
    """Respawn wild markers and rematch trainers in place.

    Args:
        steps:          current step counter for this world.
        player_trainer: the player (for level scaling).
        cleared_list:   mutable list of cleared wild markers ``[(x, y, step), ...]``.
        defeated_list:  mutable list of defeated trainers ``[(x, y, step), ...]``.
        objects:        mutable list of on-map entities to append respawns to.
        wild_markers:   iterable of WildMarker setups for this world.
        trainers:       iterable of TrainerSetup for this world.
    """
    # ── Wild marker respawn — individual 100-step cooldown ──
    marker_by_pos = {(m.position[0], m.position[1]): m for m in wild_markers}
    to_restore = [
        (e[0], e[1]) for e in cleared_list
        if steps - (e[2] if len(e) > 2 else 0) >= MARKER_RESPAWN_STEPS
    ]
    for pos in to_restore:
        cleared_list[:] = [e for e in cleared_list if (e[0], e[1]) != pos]
        marker = marker_by_pos.get(pos)
        if marker is not None:
            objects.append({"x": pos[0], "y": pos[1], "kind": "wild",
                            "name": marker.name, "level": marker.level})

    # ── Trainer rematches — individual 300-step cooldown ──
    # Only regular trainers rematch: friendly NPCs and bosses are one-shot.
    rematch_positions = {
        (t.position[0], t.position[1]): t for t in trainers
        if not getattr(t, "is_friendly", False) and not getattr(t, "is_boss", False)
    }
    to_rematch = [
        (e[0], e[1]) for e in defeated_list
        if (e[0], e[1]) in rematch_positions
        and steps - (e[2] if len(e) > 2 else 0) >= TRAINER_REMATCH_STEPS
    ]
    if to_rematch:
        avg = _player_avg_level(player_trainer)
        for pos in to_rematch:
            defeated_list[:] = [e for e in defeated_list if (e[0], e[1]) != pos]
            t = rematch_positions[pos]
            scaled_team = [(name, max(orig_lv + 2, avg)) for name, orig_lv in t.team]
            scaled_setup = dataclasses.replace(t, team=scaled_team)
            objects.append({"x": pos[0], "y": pos[1], "kind": "trainer", "setup": scaled_setup})
