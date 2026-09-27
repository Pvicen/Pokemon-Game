# Contratos entre Cajas

Formato exacto de los datos que cruzan de una Caja a otra (método C.C.D., `AGENTS.md`). Al
programar una Caja se le pasa a la IA este documento, no el código de las demás.

## §1. Datos (`data/` → `data_io/` → resto)

`data_io` valida y normaliza. Tras normalizar, **todas las claves van en minúsculas**
(`"eevee"`, `"waterstone"`); quien consulte debe usar `.lower()`.

`data/pokemons.json` — una entrada por especie:

```json
{"name": "Eevee", "element_type": "normal", "health": 55, "defense": 50,
 "special_defense": 65, "speed": 55, "base_attack": 55,
 "evolution": null, "evolution_level": null, "current_level": 1,
 "evolution_by_item": {"waterstone": "vaporeon", "firestone": "flareon"}}
```

`data/attacks.json` — ataques agrupados por especie propietaria (más `normal_attacks` de
reserva). `pp` es obligatorio; `effect` solo en ataques que causan estado:

```json
{"name": "Thunder Wave", "type": "Electric", "damage": 0, "pp": 20,
 "effect": {"kind": "status", "status": "paralysis", "chance": 100}}
```

Estados válidos: `"poison"`, `"paralysis"`, `"sleep"`. Una especie sin entrada en
`attacks.json` no puede combatir.

`data/items.json` — tipos `healing`, `revive`, `buff`, `capture`, `evolution`, `status_cure`:

```json
{"WaterStone": {"name": "Water Stone", "type": "evolution", "target": "ally",
                "effect": {"kind": "evolution"}, "battle_only": false, "reusable": false}}
```

## §2. Save v2 (`game/save_load.py` ↔ `main.py` y `map/`)

`SAVE_VERSION = 2`. Un fichero por partida en `saves/<nombre>.json`.

```json
{
  "slot_name": "mi_partida", "save_version": 2, "current_world": "world1",
  "difficulty": "normal", "chapter2_unlocked": true, "world2_completed": false,
  "steps": {"world1": 336, "world2": 37},
  "team": [{"name": "Charmeleon", "level": 5, "health": 68, "exp": 0,
            "pp": {"Ember": 20, "Scratch": 35}, "status": null, "sleep_turns": 0}],
  "bag": {"potion": 2, "pokeball": 5},
  "pokedex": [{"name": "Charmeleon", "caught": true, "level_caught": 5}],
  "worlds": {
    "world1": {"current_map": "main", "position": {"x": 139, "y": 54},
               "defeated_trainers":    {"main": [[10, 44, 120]], "dungeon": [], "dungeon_pn": []},
               "cleared_wild_markers": {"main": [[15, 32, 200]], "dungeon": [], "dungeon_pn": []}},
    "world2": {"current_map": "world2_main", "position": {"x": 15, "y": 8},
               "defeated_trainers": {"world2_main": []}, "cleared_wild_markers": {"world2_main": []}}
  }
}
```

Reglas:

- **Globales**: `team`, `bag`, `pokedex`, `difficulty`, `chapter2_unlocked`, `world2_completed`.
  **Por mundo** (`worlds.<id>`): mapa, posición, entrenadores vencidos y markers despejados.
  `WORLD_MAPS`: `world1` → `main`, `dungeon`, `dungeon_pn`; `world2` → `world2_main`.
- Entidades vencidas: `[x, y, step]`; `[x, y]` se lee como `step = 0`.
- `save_game(..., current_world=...)` lee el disco y hace merge: el mundo inactivo no se toca.
  `chapter2_unlocked` y `world2_completed` nunca vuelven a `false`.
- En el Mundo 1, `_cur_dict()` incluye siempre las tres claves de mapa.
- Compatibilidad hacia atrás: `_migrate_v1_to_v2` migra en memoria los saves sin
  `save_version >= 2`; sin `pp` → PP al máximo; sin `status`/`sleep_turns` → `null`/`0`; sin
  `difficulty` → `"normal"`; Pokédex como lista de nombres → objetos con `caught: false`.

## §3. Transiciones de mapa (`map/` → `main.py`)

| Función | Devuelve |
|---|---|
| `run_map()` | `"enter_dungeon"`, `"enter_dungeon_pn"`, `"travel_to_world2"`, `"quit"` |
| `run_dungeon()` | `"exit_west"`, `"exit_east"`, `"quit"` |
| `run_dungeon_pn()` | `"exit_pn"`, `"quit"` |
| `run_world2_map()` | `"travel_to_world1"`, `"quit"` |

Antes de devolver una transición, la Caja Mapa guarda en el save el mapa y la posición de
destino; `main.py` solo recarga y despacha. Un mundo nuevo (`world3`) añade su id a `WORLD_IDS`
y `WORLD_MAPS`, su motor en `map/world3/` y sus códigos aquí.
