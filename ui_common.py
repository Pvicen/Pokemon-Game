"""Shared interactive-UI primitives used across the whole project.

This is a *leaf* module: it imports nothing from inside the package (only the
standard library), so it can be imported at module top-level from anywhere —
including ``combat.py`` — without ever creating an import cycle.

It centralises three patterns that were duplicated all over the codebase:

* :func:`pause`            — the ``input("Press Enter...")`` "press a key to
  continue" prompt (Paquete 3 / R5).
* :func:`collect_attacks`  — gathering a Pokémon's special + normal moves into a
  single list (was duplicated in ``controllers/human.py`` and
  ``controllers/ia.py``) (Paquete 3 / R2).
* :func:`pick_pokemon`     — the "list a set of Pokémon and read a numeric
  choice" selection menu (was copy-pasted in every branch of
  ``game/ui_menus.py``) (Paquete 3 / R2 + R3).
"""
from __future__ import annotations

from typing import Callable, List, Optional, Sequence, Tuple


def pause(message: str = "  Press Enter to continue...") -> None:
    """Block until the player presses Enter.

    Centralises the dozens of ``input("Press Enter...")`` calls that were
    scattered across combat, encounters, maps and menus. The default message
    matches the most common prompt; callers pass their own text to preserve the
    exact wording where it differs.
    """
    input(message)


def collect_attacks(pokemon) -> List[dict]:
    """Return a Pokémon's moves as one list: special moves first, then normal.

    Mirrors the original inline logic from both controllers. Missing/empty move
    lists are tolerated (``getattr`` guards), so the result is always a list —
    possibly empty.
    """
    attacks: List[dict] = []
    if getattr(pokemon, "special_attacks", None):
        attacks.extend(list(pokemon.special_attacks))
    if getattr(pokemon, "normal_attacks", None):
        attacks.extend(list(pokemon.normal_attacks))
    return attacks


def pick_pokemon(
    candidates: Sequence[Tuple[int, object]],
    *,
    title: str,
    formatter: Callable[[int, object], str],
    prompt: str = "  Choose: ",
    loop: bool = False,
) -> Optional[int]:
    """Render a numbered Pokémon picker and return the chosen *team index*.

    Parameters
    ----------
    candidates:
        Pre-filtered list of ``(team_index, pokemon)`` pairs. The team index is
        what gets returned, so callers can pass a filtered subset (only fainted,
        only healable, ...) and still receive the correct index into the full
        team.
    title:
        Heading printed above the list (may start with ``"\\n"``).
    formatter:
        ``formatter(team_index, pokemon) -> str`` builds each row's text
        (without the ``"[n] "`` prefix), so each caller keeps its own columns.
    prompt:
        Text passed to :func:`input`.
    loop:
        When ``True`` (in-battle menus) an invalid entry re-prompts instead of
        cancelling; when ``False`` (out-of-battle menus) any invalid entry
        cancels and returns ``None`` — matching the previous behaviour of each
        call site.

    Returns
    -------
    The selected ``team_index``, or ``None`` if the player cancelled (``0``) or
    entered something invalid while ``loop`` is ``False``.
    """
    if not candidates:
        return None

    print(title)
    for display, (team_idx, pokemon) in enumerate(candidates, start=1):
        print(f"    [{display}] {formatter(team_idx, pokemon)}")
    print("    [0] Cancel")

    while True:
        choice = input(prompt).strip()
        if choice == "0":
            return None
        if not choice.isdigit():
            if loop:
                print("  ❌ Invalid input, please enter a number.")
                continue
            return None
        pick = int(choice) - 1
        if 0 <= pick < len(candidates):
            return candidates[pick][0]
        print("  ❌ Invalid.")
        if not loop:
            return None
