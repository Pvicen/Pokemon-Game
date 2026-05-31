"""Shared terminal / ANSI helpers for flicker-free rendering.

Renderers build a full frame as a list of lines and emit it with a single
atomic write, repositioning the cursor to *home* (`\\033[H`) instead of clearing
the whole screen each frame. Combined with clear-to-end-of-line (`\\033[K`) per
line and clear-to-end-of-screen (`\\033[J`) at the bottom, the previous frame is
overwritten in place with no blank flash.

This module also consolidates the ANSI constants that were duplicated across the
five renderers (Propuesta R4 del informe de auditoría).
"""
from __future__ import annotations

import atexit
import os
import sys

# Enable ANSI escape codes on Windows (no-op on other systems)
os.system("")

_cursor_restore_registered = False

# ── Core ANSI control codes ──
RESET       = "\033[0m"
HOME        = "\033[H"          # move cursor to top-left WITHOUT clearing
FULL_CLEAR  = "\033[2J\033[H"   # erase everything + home (use ONCE, e.g. on entry)
CLEAR_EOL   = "\033[K"          # erase from cursor to end of line
CLEAR_DOWN  = "\033[J"          # erase from cursor to end of screen
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"

# ── Shared viewport size (was VIEWPORT_W/H and _VP_W/H in 4 files) ──
VIEWPORT_W = 40
VIEWPORT_H = 20

# ── Shared background (was _BG / _BG_VOID = "\033[40m" in 3 files) ──
BG_DARK = "\033[40m"


def home() -> None:
    """Move the cursor to the top-left without erasing."""
    sys.stdout.write(HOME)
    sys.stdout.flush()


def hide_cursor() -> None:
    """Hide the cursor and guarantee it is shown again when the process exits
    (normal exit, quit, or Ctrl+C), so we never leave the terminal cursorless."""
    global _cursor_restore_registered
    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.flush()
    if not _cursor_restore_registered:
        atexit.register(show_cursor)
        _cursor_restore_registered = True


def show_cursor() -> None:
    sys.stdout.write(SHOW_CURSOR)
    sys.stdout.flush()


def clear_once() -> None:
    """Full-screen clear. Call ONCE when entering a screen, never per frame."""
    sys.stdout.write(FULL_CLEAR)
    sys.stdout.flush()


def render_frame(lines: list[str]) -> None:
    """Draw a frame without flicker.

    Repositions the cursor to home (no erase), writes every line padded with a
    clear-to-end-of-line so shorter lines don't leave residue, and finishes with
    a clear-to-end-of-screen to wipe leftover rows from a previous taller frame.
    The whole frame is emitted in a single atomic write to avoid tearing.
    No trailing newline after the last line, to avoid scrolling the viewport.
    """
    body = (CLEAR_EOL + "\n").join(lines)
    sys.stdout.write(HOME + body + CLEAR_EOL + CLEAR_DOWN)
    sys.stdout.flush()
