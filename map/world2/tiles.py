from __future__ import annotations

WORLD2_MAP_WIDTH  = 120
WORLD2_MAP_HEIGHT = 50

WORLD2_PLAYER_START  = (15, 8)
WORLD2_RETURN_PORTAL = (14, 8)
WORLD2_PC_POS        = (22, 8)   # Centro Pokémon (Aldea Aurora, plaza central)

# Zone bounding rectangles: (x_min, y_min, x_max, y_max), inclusive
ZONE_AURORA = (1,  1,  30, 15)
ZONE_BOSQUE = (31, 1,  70, 25)
ZONE_MESETA = (1,  26, 50, 49)
ZONE_LAGO   = (51, 26, 90, 49)
ZONE_TEMPLO = (91, 1, 119, 49)

ZONE_NAMES = {
    "aurora": "Aldea Aurora",
    "bosque": "Bosque Milenario",
    "meseta": "Meseta Ventosa",
    "lago":   "Lago Cristal",
    "templo": "Templo Eco",
}


def _carve(grid: list[list[str]], x1: int, y1: int, x2: int, y2: int) -> None:
    for y in range(max(0, y1), min(WORLD2_MAP_HEIGHT, y2 + 1)):
        for x in range(max(0, x1), min(WORLD2_MAP_WIDTH, x2 + 1)):
            grid[y][x] = "."


def _build_world2_map() -> list[list[str]]:
    g = [["#"] * WORLD2_MAP_WIDTH for _ in range(WORLD2_MAP_HEIGHT)]

    # ----- Zonas (interior con borde de 1 tile para definir el contorno) -----
    _carve(g,  2,  2, 29, 14)   # Aldea Aurora      — village interior
    _carve(g, 10,  4, 19, 11)   # Aldea Aurora      — central plaza 10×8 (futuro PC, Q3)
    _carve(g, 32,  2, 69, 24)   # Bosque Milenario
    _carve(g,  2, 27, 49, 48)   # Meseta Ventosa
    _carve(g, 52, 27, 89, 48)   # Lago Cristal
    _carve(g, 92,  2, 118, 48)  # Templo Eco

    # ----- Corredores que conectan zonas (atraviesan paredes de borde y voids) -----
    _carve(g, 28,  7, 33,  9)   # [1] Aldea  ↔ Bosque  (horizontal, junto al spawn)
    _carve(g, 13, 14, 17, 27)   # [2] Aldea  ↔ Meseta  (vertical, atraviesa void cols 1-30 rows 16-25)
    _carve(g, 69, 11, 92, 13)   # [3] Bosque ↔ Templo  (horizontal, atraviesa void cols 71-90 rows 1-25)
    _carve(g, 38, 23, 42, 28)   # [4] Bosque ↔ Meseta  (vertical, lado oeste)
    _carve(g, 58, 23, 62, 28)   # [5] Bosque ↔ Lago    (vertical, lado este)
    _carve(g, 48, 36, 53, 38)   # [6] Meseta ↔ Lago    (horizontal)
    _carve(g, 88, 36, 93, 38)   # [7] Lago   ↔ Templo  (horizontal)

    return g


WORLD2_OBSTACLE_GRID = _build_world2_map()


def _in_rect(x: int, y: int, rect: tuple[int, int, int, int]) -> bool:
    x1, y1, x2, y2 = rect
    return x1 <= x <= x2 and y1 <= y <= y2


def get_zone_for_world2(x: int, y: int) -> str | None:
    """Returns the zone id at (x, y), or None if outside all zones (corridor/void)."""
    if _in_rect(x, y, ZONE_AURORA): return "aurora"
    if _in_rect(x, y, ZONE_BOSQUE): return "bosque"
    if _in_rect(x, y, ZONE_MESETA): return "meseta"
    if _in_rect(x, y, ZONE_LAGO):   return "lago"
    if _in_rect(x, y, ZONE_TEMPLO): return "templo"
    return None
