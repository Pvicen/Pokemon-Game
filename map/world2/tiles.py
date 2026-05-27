from __future__ import annotations

WORLD2_MAP_WIDTH  = 20
WORLD2_MAP_HEIGHT = 10

WORLD2_PLAYER_START  = (3, 3)
WORLD2_RETURN_PORTAL = (2, 2)


def _build_world2_stub_grid() -> list[list[str]]:
    g = [["#"] * WORLD2_MAP_WIDTH for _ in range(WORLD2_MAP_HEIGHT)]
    for y in range(1, WORLD2_MAP_HEIGHT - 1):
        for x in range(1, WORLD2_MAP_WIDTH - 1):
            g[y][x] = "."
    return g


WORLD2_OBSTACLE_GRID = _build_world2_stub_grid()
