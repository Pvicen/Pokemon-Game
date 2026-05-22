TILE_WALL    = "#"
TILE_PLAYER  = "@"
TILE_TRAINER = "T"
TILE_EMPTY   = " "

MAP_W = 120
MAP_H = 50

PLAYER_START_X = 20
PLAYER_START_Y = 43


def _build_map():
    g = [[TILE_WALL] * MAP_W for _ in range(MAP_H)]

    def carve(x1, y1, x2, y2):
        for y in range(max(1, y1), min(MAP_H - 1, y2 + 1)):
            for x in range(max(1, x1), min(MAP_W - 1, x2 + 1)):
                g[y][x] = TILE_EMPTY

    def wall_box(x1, y1, x2, y2):
        """Hollow rectangular building (walls on perimeter, interior stays walkable)."""
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                if y in (y1, y2) or x in (x1, x2):
                    g[y][x] = TILE_WALL

    # ── PUEBLO RAÍZ (start, bottom-left) ─────────────── rows 28-48, cols 1-38
    carve(1, 28, 38, 48)
    wall_box(3, 30, 14, 36)     # Player's house
    wall_box(18, 30, 34, 36)    # Gym
    g[36][8]  = TILE_EMPTY      # House door
    g[36][26] = TILE_EMPTY      # Gym door

    # ── RUTA NORTE (vertical, connects both towns) ────── cols 39-42, rows 1-48
    carve(39, 1, 42, 48)

    # ── RUTA ESTE (horizontal connector) ─────────────── rows 22-27, cols 1-91
    carve(1, 22, 91, 27)

    # ── PUEBLO ALTO (second town, top-left) ──────────── rows 1-21, cols 1-38
    carve(1, 1, 38, 21)
    wall_box(3, 3, 16, 11)      # Pokemon Center
    wall_box(20, 3, 36, 11)     # Lab
    g[11][9]  = TILE_EMPTY      # Pokemon Center door
    g[11][28] = TILE_EMPTY      # Lab door

    # ── BOSQUE UMBRAL (forest, top-right) ─────────────── rows 1-21, cols 44-118
    carve(44, 1, 118, 21)
    # Dense tree pattern — most cells become walls
    for y in range(1, 22):
        for x in range(45, 118):
            if (x + y * 2) % 5 != 0:
                g[y][x] = TILE_WALL
    # Carve explicit navigable paths through the forest
    carve(44, 1, 47, 21)        # West entry path (from Ruta Norte)
    carve(60, 1, 63, 21)        # Forest path 1
    carve(44, 9, 118, 12)       # Horizontal connector through forest
    carve(78, 1, 81, 21)        # Forest path 2
    carve(95, 9, 97, 21)        # Forest path 3 (leads toward cave top)

    # ── CUEVA OSCURA (cave, bottom-right) ─────────────── rows 28-48, cols 87-118
    # Cave is all walls by default — corridors are carved below

    # Entrance from Ruta Este
    carve(87, 24, 92, 28)       # Entrance corridor (connects route to cave)

    # Main entrance shaft going south
    carve(88, 28, 91, 35)

    # Junction room A — bifurcation point (3 branches)
    carve(87, 35, 99, 38)

    # Branch LEFT: goes south then dead-end west corridor
    carve(87, 38, 90, 44)
    carve(87, 42, 97, 45)       # Dead-end (west)

    # Branch CENTER: goes south to main chamber
    carve(93, 38, 96, 42)
    carve(90, 42, 104, 46)      # Main chamber
    carve(99, 46, 102, 48)      # Dead-end south from main chamber

    # Branch RIGHT: east corridor to second chamber
    carve(99, 35, 114, 38)
    carve(107, 33, 117, 42)     # East chamber
    carve(113, 28, 116, 33)     # Dead-end north from east chamber

    # Secret path south from east chamber to deepest area
    carve(109, 42, 112, 48)
    carve(104, 46, 118, 48)     # Deepest chamber

    return "\n".join("".join(row) for row in g)


def _validate_map(grid):
    if not grid:
        raise ValueError("Map is empty")
    expected = len(grid[0])
    for i, row in enumerate(grid):
        if len(row) != expected:
            raise ValueError(f"Row {i} has {len(row)} cols, expected {expected}")


_MAP_STRING   = _build_map()
OBSTACLE_GRID = [list(row) for row in _MAP_STRING.split("\n")]
MAP_WIDTH     = len(OBSTACLE_GRID[0])
MAP_HEIGHT    = len(OBSTACLE_GRID)

_validate_map(OBSTACLE_GRID)
