# Pokemon Game — Contexto del Proyecto

## Descripción
Juego de Pokémon por terminal (ASCII) en Python. Combate por turnos, overworld 160×65 con 6 zonas, dungeon 60×30 con tránsito bidireccional, entrenadores NPC, Pokémon salvajes, inventario, guardado/cargado de partidas con nombre.

## Cómo ejecutar
```
python -m Pokemon_Game
```
Desde `c:\Users\moral\Documentos` (directorio padre de la carpeta `Pokemon_Game/`).

## Reglas de trabajo (OBLIGATORIAS)
- NO reescribir el proyecto desde cero
- NO modificar archivos sin explicar el plan primero
- Trabajar en pasos pequeños, código modular
- NO mezclar lógica en `main.py`
- Todo el código en inglés; comunicación con el usuario en **español**
- Entrenadores, Pokémon salvajes y spawns van en `game/` — NUNCA en `map/`
- `map/` solo maneja: terreno, render, movimiento del jugador, viewport, colisiones
- **Workflow obligatorio**: explicar problema → listar archivos → cambios exactos → esperar aprobación → editar → explicar cómo probar

## Arquitectura

```
Pokemon_Game/
├── main.py                  # Menú principal, state machine de mapas
├── combat.py                # Motor de combate por turnos (STRUGGLE, estados alterados, veneno al fin de ronda)
├── models.py                # Clase Pokemon (PP tracking + status: apply_status, clear_status, status, sleep_turns)
├── trainers.py              # Clase Trainer
├── inventory.py             # Clase Inventory (healing, revive, buff, evolution, status_cure; _apply_status_cure)
├── damage.py                # Cálculo de daño y efectividad de tipos
├── experience.py            # ExperienceManager, _apply_species(), _try_species_lookup()
├── utils.py                 # clamp(), determine_attack_order() — speed//2 si paralysis
├── abilities.py             # Habilidades pasivas: ABILITY_BY_SPECIES, fire_on_entry, fire_pre_damage, fire_on_hit_received
├── data_io/                 # Módulo de I/O de datos (con caché y normalización)
│   ├── __init__.py          # load_attacks(), load_pokemons(), load_items(), load_type_chart()
│   ├── loaders.py           # load_dataset(), read_json_cached()
│   ├── paths.py             # data_dir()
│   ├── errors.py            # DataIOError, DataValidationError, DataPathError
│   └── checks/
│       ├── pokemons.py      # validate_pokemons(), normalize_pokemons() — normaliza a lowercase
│       ├── attacks.py       # validate_attacks(), normalize_attacks() — pasa campos "pp" y "effect" al output
│       ├── items.py         # validate_items(), normalize_items() — soporta tipo "status_cure"
│       └── type_effectiveness.py
├── data/
│   ├── pokemons.json        # Stats base de cada Pokémon (73 especies)
│   ├── attacks.json         # Ataques por propietario — campo "pp" en todos + campo "effect" en ataques de estado
│   ├── items.json           # 26 ítems (healing, revive, buff, capture, evolution, status_cure)
│   └── type_effectiveness.json
├── controllers/
│   ├── __init__.py
│   ├── human.py             # HumanController — ChooseAttack() muestra PP: X/Y, filtra PP=0, auto-Struggle
│   └── ia.py                # IAcontroller — _Calculating_Damages() filtra PP=0, fallback Struggle
├── game/
│   ├── __init__.py
│   ├── setup_game.py        # Zone, WildMarker, TrainerSetup, ZONES, TRAINERS, DUNGEON_TRAINERS, DUNGEON_PN_TRAINERS
│   │                        # _build_pokemon(), create_trainer_instance(), get_zone_for_position()
│   │                        # get_dungeon_pn_objects(), get_dungeon_pn_wild_marker_objects()
│   ├── encounters.py        # trigger_encounter(), trigger_wild_encounter(), trigger_wild_marker_encounter()
│   │                        # clear_status() en Pokémon capturado (no entra al equipo con veneno/parálisis)
│   ├── save_load.py         # save_game(), load_game(), restore_player_trainer(), load_defeated_dict()
│   │                        # save incluye "pp", "status", "sleep_turns", "steps", "chapter2_unlocked"
│   │                        # defeated/cleared son tuplas [x, y, step]; backward-compat para saves viejos
│   ├── ui_menus.py          # open_bag_menu(), open_pokedex(), show_team_summary()
│   ├── ui_utils.py          # _hp_bar() — usado por ui_menus y show_team_summary
│   └── world.py             # (reservado para futura arquitectura multi-mundo)
├── map/
│   ├── __init__.py          # run_map(); _heal_at_pokemon_center() restaura HP+PP y cura todos los estados
│   │                        # _check_respawn(): wild markers cada 100 pasos, rematches cada 300 pasos
│   ├── tiles.py             # OBSTACLE_GRID, _build_map() — mapa 160×65
│   ├── dungeon.py           # DUNGEON_GRID, run_dungeon() — cueva 60×30, tránsito bidireccional
│   ├── dungeon_pn.py        # DUNGEON_PN_GRID, run_dungeon_pn() — cueva end-game 40×20, Champion Nexus
│   ├── player.py            # PlayerState (posición, movimiento)
│   ├── renderer.py          # render() — colores ANSI por zona
│   ├── events.py            # check_collision()
│   └── saves.py             # (reservado / auxiliar de guardado por mapa)
└── saves/                   # Partidas guardadas ({nombre}.json)
```

---

## Estado actual — Fases completadas

| Fase | Descripción | Estado |
|------|------------|--------|
| 1–8 | Base: modelos, combate, IA, daño, XP, inventario, mapa | ✅ |
| 9A | Saves con nombre (múltiples slots, `saves/`) | ✅ |
| 9B | Selección de 2 starters con stats/ataques | ✅ |
| 10 | Inventario jugador (2 Potions + 1 X-Defense; guarda/carga) | ✅ |
| 11A | Diálogo de entrenadores antes de batalla | ✅ |
| 11B | Recompensas aleatorias al ganar (reward_pool) | ✅ |
| 11C | NPCs amistosos (diálogo + regalo, sin batalla) | ✅ |
| 11.5 | Reward pools ponderados + encuentros salvajes reducidos (1–3%) | ✅ |
| 12 | Centro Pokémon real (x=9, y=11 en Pueblo Alto) | ✅ |
| 13 | Captura de Pokémon salvajes (Pokéballs, fórmula HP, equipo max 6) | ✅ |
| Feature A | Menú de bolsa fuera de batalla (tecla `E`) | ✅ |
| Feature B | Selector de Pokémon objetivo al usar ítems en batalla | ✅ |
| 14 | Pokémon visibles en el mapa como marcadores `!` | ✅ |
| A | Colores ANSI en el mapa por zona | ✅ |
| B | UI de combate estilo clásico (caja ╔══╗, barra HP con color, log) | ✅ |
| C | Balance de stats starters + ataques normales de fallback | ✅ |
| Bug Fix 1 | `trigger_encounter()` retorna `False` si el jugador pierde | ✅ |
| Bug Fix 2 | Pokéballs agregadas a `reward_pool` de trainers por zona | ✅ |
| F | Pokédex en juego (tecla `P`) — lista todos los Pokémon, ★ capturados | ✅ |
| D | Submapa independiente: Cueva Oscura (60×30, renderer oscuro, entidades propias) | ✅ |
| **E** | **Overworld expandido 160×65: Ruta del Mar + Paso Costero + Pueblo Nuevo + PC2** | ✅ |
| **Tránsito** | **Cueva bidireccional: entrada/salida Oeste y Este independientes** | ✅ |
| **H** | **UI/UX: HP bars en selector, tecla T equipo, bolsa por categorías** | ✅ |
| **G** | **Evolución por ítems (Fire/Water/Thunder/Leaf/Moon Stone)** | ✅ |
| **I** | **Sistema de PP: usos limitados por ataque, Struggle, restauración en PC** | ✅ |
| **L** | **Pokédex extendida: ◆ visto / ★ capturado + nivel de captura** | ✅ |
| **M** | **Refactor save: `cleared_wild_markers` separado de `defeated_trainers`** | ✅ |
| **J** | **Estados alterados: Veneno, Parálisis, Sueño + ítems curativos** | ✅ |
| **K** | **Habilidades pasivas por especie (abilities.py, hooks fire_on_entry/pre_damage/on_hit en combat.py)** | ✅ |
| **N** | **Respawn de wild markers (100 pasos, cooldown individual, `_check_respawn()` in-loop)** | ✅ |
| **O** | **Rematches de trainers (300 pasos, equipo escalado con `dataclasses.replace()`)** | ✅ |
| **P** | **Cueva dungeon_pn (40×20) + Champion Nexus → `chapter2_unlocked=True` + retorno (153,61)** | ✅ |

---

## Roadmap pendiente

| Fase | Descripción | Riesgo | Depende de |
|------|-------------|--------|------------|
| **Q** | Capítulo 2 / Mundo Nuevo (save multi-mundo, `current_world`) | Muy Alto | P ✓, M ✓ |

El plan detallado de cada fase está en `C:\Users\moral\.claude\plans\lively-enchanting-spring.md`.

---

## Arquitectura de mapas

`main.py` coordina un `while True` con variable `current_map`:
- `run_map()` → retorna `"enter_dungeon"` | `"enter_dungeon_pn"` | `"quit"`
- `run_dungeon()` → retorna `"exit_west"` | `"exit_east"` | `"quit"`
- `run_dungeon_pn()` → retorna `"exit_pn"` | `"quit"`
- Al cambiar de mapa, `main.py` recarga el save para obtener posición y `defeated_dict` autoritativos.
- `cleared_markers_dict` NO se recarga del disco en cada transición — se pasa por referencia en RAM.

### Transiciones de mapa

| Evento | Qué pasa |
|--------|----------|
| Pisa cols 87-92, y=28 (Ruta Este→cueva) | Guarda spawn `(3,2)`, `current_map="dungeon"`, retorna `"enter_dungeon"` |
| Pisa x=118, rows 46-48 (Pueblo Nuevo→cueva) | Guarda spawn `(57,26)`, `current_map="dungeon"`, retorna `"enter_dungeon"` |
| Pisa ▲ en dungeon `(3,1)` | Guarda pos `(90,26)`, `current_map="main"`, retorna `"exit_west"` |
| Pisa ▲ en dungeon `(57,27)` | Guarda pos `(119,47)`, `current_map="main"`, retorna `"exit_east"` |
| Pisa cols 152-155, y=62 (Pueblo Nuevo→cueva PN) | Guarda spawn `(2,2)`, `current_map="dungeon_pn"`, retorna `"enter_dungeon_pn"` |
| Pisa ▲ en dungeon_pn `(2,1)` | Guarda pos `(153,61)`, `current_map="main"`, retorna `"exit_pn"` |
| Derrota Champion Nexus en dungeon_pn `(35,16)` | Guarda `chapter2_unlocked=True`, pos `(153,61)`, `current_map="main"`, retorna `"exit_pn"` |

**IMPORTANTE:** `main.py` no necesita cambios — lee el `current_map` y `position` del save después de cada transición. El spawn en el dungeon viaja en el save.

### Dungeon — layout (60×30)

Viewport 40×20. Dos entradas/salidas independientes.

| Sección | Carve | Entidades |
|---------|-------|-----------|
| Entry room | `(1,1)-(8,4)` | ▲ oeste `(3,1)`, spawn oeste `(3,2)` |
| Top corridor | `(5,4)-(25,8)` | Geodude `!` (8,5), Ryu `T` (15,8) |
| Vertical connector | `(20,5)-(22,15)` | — |
| Middle section | `(15,10)-(32,15)` | Sara `T` (25,14) |
| Right section | `(30,12)-(45,15)` | Gastly `!` (35,12) |
| Deep vertical | `(38,14)-(42,22)` | Grunt `T` (40,18) |
| Lower corridor | `(18,18)-(42,22)` | Deserter NPC (20,22) |
| Deep chamber | `(38,22)-(52,28)` | Champion `T` (45,26) |
| East exit corridor | `(52,25)-(58,28)` | ▲ este `(57,27)`, spawn este `(57,26)` |

### Constantes clave (dungeon.py)

```python
DUNGEON_START          = (3, 2)     # spawn al entrar por el oeste
DUNGEON_START_EAST     = (57, 26)   # spawn al entrar por el este
DUNGEON_EXIT_POS       = (3, 1)     # salida oeste ▲
DUNGEON_EXIT_EAST_POS  = (57, 27)   # salida este ▲
MAIN_MAP_RETURN_WEST   = (90, 26)   # retorno overworld salida oeste
MAIN_MAP_RETURN_EAST   = (119, 47)  # retorno overworld salida este
```

### Dungeon PN — layout (40×20, Fase P)

Viewport 40×20 (tamaño exacto del mapa — sin scroll). Cueva end-game con Champion Nexus.

| Sección | Carve | Entidades |
|---------|-------|-----------|
| Entry room | `(1,1)-(4,3)` | ▲ salida `(2,1)`, spawn `(2,2)` |
| Entry corridor | `(4,2)-(18,4)` | Onix `!` (8,3), Nadia `T` (14,3) |
| Vertical shaft | `(16,2)-(18,12)` | — |
| Middle room | `(14,10)-(28,13)` | Gengar `!` (20,11), Kyle `T` (25,10) |
| Deep vertical | `(26,10)-(28,18)` | — |
| Champion chamber | `(24,16)-(38,18)` | Champion Nexus `T` (35,16) |

Champion Nexus: Gengar Lv27, Rhydon Lv26, Alakazam Lv27, Arcanine Lv26.

### Constantes clave (dungeon_pn.py)

```python
DUNGEON_PN_WIDTH    = 40
DUNGEON_PN_HEIGHT   = 20
DUNGEON_PN_START    = (2, 2)    # spawn al entrar desde overworld
DUNGEON_PN_EXIT     = (2, 1)    # salida ▲
OVERWORLD_RETURN_PN = (153, 61) # retorno overworld
```

### Constantes clave (map/__init__.py)

```python
POKEMON_CENTER_POS   = (9, 11)    # PC1 — Pueblo Alto
POKEMON_CENTER_2_POS = (129, 46)  # PC2 — Pueblo Nuevo (tile interior; puerta física en y=47)
# Triggers de cueva (boundary-crossing):
# Oeste: 87 <= x <= 92 and y == 28
# Este:  x == 118 and 46 <= y <= 48
# Cueva PN: 152 <= x <= 155 and y == 62
```

---

## Zonas del overworld (160×65)

| Zona | Coordenadas | Dificultad | Encuentro salvaje |
|------|-------------|------------|-------------------|
| Pueblo Raiz | rows 28-48, cols 1-38 | Fácil (Lv 1-5) | 1% |
| Pueblo Alto | rows 1-21, cols 1-38 | Medio-bajo (Lv 5-10) | 1% |
| Bosque Umbral | rows 1-21, cols 44-118 | Medio-alto (Lv 8-14) | 2% |
| Cueva Oscura | rows 24-48, cols 87-118 | Difícil (Lv 12-18) | 3% |
| Ruta del Mar | rows 1-34, cols 119-158 | Difícil (Lv 12-18) | 2% |
| Pueblo Nuevo | rows 35-63, cols 119-158 | — | 0% |
| Cueva (dungeon) | todo `dungeon.py` | Difícil (Lv 12-18) | 3% (zone_id="cueva_oscura") |

**Prioridad de detección** (`get_zone_for_position`): pueblo_nuevo → ruta_del_mar → cueva_oscura → bosque_umbral → pueblo_alto → pueblo_raiz. El chequeo `x >= 119` debe ir ANTES de `x >= 87`.

---

## Centros Pokémon

| Centro | Posición overworld | Puerta física | Zona |
|--------|--------------------|---------------|------|
| PC1 | `(9, 11)` | `g[11][9]` | Pueblo Alto |
| PC2 | `(129, 46)` | `g[47][129]` | Pueblo Nuevo |

Edificio PC2: `wall_box(121, 37, 137, 47)`. Curan HP al máximo, reviven desmayados y **restauran todos los PP al máximo**.

---

## Pokémon visibles en mapa (wild markers)

### Overworld
| Pokémon | Nivel | Posición | Zona |
|---------|-------|----------|------|
| Meowth | 3 | (15, 32) | Pueblo Raiz |
| Mankey | 4 | (30, 36) | Pueblo Raiz |
| Magnemite | 7 | (12, 8) | Pueblo Alto |
| Horsea | 7 | (25, 14) | Pueblo Alto |
| Bellsprout | 10 | (52, 18) | Bosque Umbral |
| Venonat | 11 | (75, 8) | Bosque Umbral |
| Staryu | 14 | (130, 8) | Ruta del Mar |
| Tentacool | 13 | (145, 18) | Ruta del Mar |
| Eevee | 12 | (135, 50) | Pueblo Nuevo |

### Dungeon (coordenadas locales)
| Pokémon | Nivel | Posición |
|---------|-------|----------|
| Geodude | 13 | (8, 5) |
| Gastly | 14 | (35, 12) |

---

## NPCs amistosos

### Overworld
| NPC | Posición | Zona |
|-----|----------|------|
| Elder Roy | (20, 38) | Pueblo Raiz |
| Nurse Clara | (35, 22) | Pueblo Alto |
| Lost Traveler | (65, 7) | Bosque Umbral |
| Sailor Marco | (128, 54) | Pueblo Nuevo |
| Swimmer Lucia | (143, 54) | Pueblo Nuevo |
| Old Fisherman | (152, 57) | Pueblo Nuevo (friendly, da recompensa) |

### Dungeon
| NPC | Posición |
|-----|----------|
| Deserter | (20, 22) |

---

## Estructura de save (actual)

```json
{
  "slot_name": "mi_partida",
  "current_map": "main",
  "steps": 450,
  "chapter2_unlocked": false,
  "position": {"x": 20, "y": 43},
  "team": [
    {
      "name": "Charmeleon",
      "level": 5,
      "health": 68,
      "exp": 0,
      "pp": {"Ember": 20, "Flamethrower": 15, "Scratch": 35},
      "status": null,
      "sleep_turns": 0
    }
  ],
  "bag": {"potion": 2, "xdefense": 1, "pokeball": 5},
  "defeated_trainers": {
    "main":       [[10, 44, 120], [28, 43, 350]],
    "dungeon":    [[15, 8, 0]],
    "dungeon_pn": []
  },
  "cleared_wild_markers": {
    "main":       [[15, 32, 200]],
    "dungeon":    [],
    "dungeon_pn": []
  },
  "pokedex": [
    {"name": "Charmeleon", "caught": true,  "level_caught": 5},
    {"name": "Squirtle",   "caught": true,  "level_caught": 5},
    {"name": "Zubat",      "caught": false, "level_caught": null}
  ]
}
```

> Entradas de `defeated_trainers` y `cleared_wild_markers` son tuplas de 3 elementos `[x, y, step]` — el tercer elemento es el valor de `steps` en el momento del evento, usado para calcular cooldown de respawn/rematch.
> `defeated_trainers` — entrenadores derrotados (respawnean a los 300 pasos con equipo escalado). `cleared_wild_markers` — markers tocados (respawnean a los 100 pasos).
> `chapter2_unlocked: true` se activa al derrotar al Champion Nexus en dungeon_pn.
> `load_defeated_dict()` migra saves viejos (lista plana → `{"main": [...], "dungeon": [], "dungeon_pn": []}`). `load_cleared_markers()` devuelve listas vacías para saves anteriores a Fase M.
> Saves sin campo `"pp"` son backward-compatible: `restore_player_trainer()` inicializa PP a máximo automáticamente.
> Saves sin campos `"status"` / `"sleep_turns"` / `"steps"` / `"chapter2_unlocked"` son backward-compatible con defaults seguros.
> **Migración Pokédex:** saves con `"pokedex": ["Pikachu", ...]` (lista de strings) se migran automáticamente en `restore_player_trainer()` a lista de dicts con `caught: false`.

**Pokémon en save:** `name, level, health, exp, pp, status, sleep_turns`. Al restaurar, `restore_player_trainer()` llama `_build_pokemon(name, level, pokemon_db, attacks_db)` que reconstruye desde `pokemons.json` normalizado, luego aplica los PP y el estado guardados encima.

---

## Sistema de PP (Fase I — implementado)

- **`data/attacks.json`**: todos los ataques tienen campo `"pp"` (valores canónicos Gen 1)
- **`data_io/checks/attacks.py`**: `_validate_attack_obj()` pasa el campo `"pp"` al output normalizado
- **`models.py`**: `Pokemon.__init__` inicializa `_pp_max` y `_pp_current` desde los dicts de ataque
  - `get_pp(name)` → retorna 0 si el ataque es desconocido (a prueba de KeyError)
  - `use_pp(name)` → decrementa 1, mínimo 0
  - `restore_all_pp()` → restaura todos a `_pp_max`
  - `has_any_pp()` → `True` si algún ataque tiene PP > 0
- **`combat.py`**: `STRUGGLE = {"name": "Struggle", "type": "Normal", "damage": 50}`, decrementado en `_apply_attack()` (Struggle no consume PP)
- **`controllers/human.py`**: `ChooseAttack()` muestra `PP: X/Y`, filtra ataques con PP=0, auto-retorna Struggle si todos en 0
- **`controllers/ia.py`**: `_Calculating_Damages()` salta ataques con PP=0, fallback Struggle si todos agotados
- **`game/save_load.py`**: serializa `_pp_current` en save, restaura en carga con backward-compat
- **`map/__init__.py`**: `_heal_at_pokemon_center()` llama `p.restore_all_pp()` y `p.clear_status()` junto a HP

---

## Pokédex extendida (Fase L — implementado)

- **`trainers.py`**: `pokedex_seen: list[dict]`. Métodos `register_seen(name)` y `register_caught(name, level)` en `Trainer`.
  - `register_seen`: añade `{"name": ..., "caught": False, "level_caught": None}` si no existe
  - `register_caught`: actualiza o crea entrada con `caught: True, level_caught: level`
- **`game/encounters.py`**:
  - Wild markers y wild encounters: `register_seen` antes de la batalla, `register_caught` si captura exitosa
  - NPC trainers: `register_seen` para todos los Pokémon del equipo rival antes del combate
- **`game/setup_game.py`**: `create_player_trainer()` llama `register_caught` para cada starter
- **`inventory.py`**: `_apply_evolution(pokemon, item_key, trainer=None)` llama `trainer.register_caught(pokemon.name, level)` tras evolución exitosa con piedra
- **`game/save_load.py`**: migración backward-compat en `restore_player_trainer()` + truco del equipo
- **`game/ui_menus.py`**: `open_pokedex()` usa `dex_lookup` con keys en **lowercase** (crítico: `pokemon_db.keys()` es lowercase, `p.name` es capitalizado — mismatch se resuelve con `.lower()`)
  - Lista: `★` capturado, `◆` visto, ` ` desconocido
  - Detalle: muestra "Caught at Lv.X" o "Seen (not yet caught)"
  - Header: `N★ caught  M◆ seen / total`

---

## Normalización de datos (data_io)

`load_pokemons()` aplica `normalize_pokemons()` que:
- Indexa por nombre en **lowercase** (`"eevee"`, `"squirtle"`)
- Normaliza todos los campos a lowercase y tipos correctos
- `Evolution_by_item` → `evolution_by_item` con keys y values en lowercase:
  `{"waterstone": "vaporeon", "firestone": "flareon", "thunderstone": "jolteon"}`

`load_attacks()` aplica `normalize_attacks()` — indexado por `by_owner[nombre_lowercase]`. Pasa campo `"pp"` al output.

`load_items()` aplica `normalize_items()` — indexado por key en **lowercase** (`"waterstone"`, `"pokeball"`, `"antidote"`). Todas las keys internas al usar ítems deben ser lowercase.

**CRÍTICO:** `evolution_by_item` keys son lowercase (`"waterstone"`), pero el `item_key` que llega a `inventory.py` puede ser PascalCase. `_apply_evolution()` hace lookup con fallback: `evo_by_item.get(item_key) or evo_by_item.get(item_key.lower())`.

---

## Sistema de datos — schemas clave

### attacks.json (por propietario)
```json
{"name": "Thunderbolt", "type": "Electric", "damage": 90, "pp": 15}
```
El campo `"pp"` es obligatorio en todos los ataques. Fallback en código: `.get("pp", 20)`.

### pokemons.json (normalizado)
```json
{
  "name": "Eevee", "element_type": "normal", "health": 55,
  "defense": 50, "special_defense": 65, "speed": 55, "base_attack": 55,
  "evolution": null, "evolution_level": null, "current_level": 1,
  "evolution_by_item": {"waterstone": "vaporeon", "firestone": "flareon", "thunderstone": "jolteon"}
}
```

### items.json
```json
{
  "WaterStone": {"name": "Water Stone", "type": "evolution", "target": "ally",
                 "effect": {"kind": "evolution"}, "battle_only": false, "reusable": false}
}
```

---

## Captura de Pokémon

- Opción `[4] Throw Pokéball` solo en batallas salvajes (`wild=True`)
- Fórmula: `base_rate = 1.0 - (hp_ratio * 0.75)`, `catch_rate = min(0.95, base_rate * mult)`
- Pokéball consumida **antes** de calcular éxito
- Equipo máximo: 6 Pokémon
- Multiplicadores: `pokeball` ×1.0, `greatball` ×1.5, `ultraball` ×2.0

---

## Keys del juego

| Tecla | Acción |
|-------|--------|
| `W/A/S/D` | Mover |
| `E` | Bolsa (usar ítems, cambiar Pokémon activo) |
| `P` | Pokédex |
| `T` | Ver equipo rápido con barras HP |
| `Q` | Guardar y salir |

---

## Ítems disponibles (keys en código — todos lowercase)

**Healing:** `potion`, `superpotion`, `maxpotion`
**Revive:** `revive`, `maxrevive`
**Buff:** `xattack`, `xspecialattack`, `xdefense`, `xspecialdefense`, `toughhelmet`
**Capture:** `pokeball`, `greatball`, `ultraball`
**Evolution:** `firestone`, `waterstone`, `leafstone`, `thunderstone`, `moonstone`
**Status cure:** `antidote` (veneno), `parlyzheal` (parálisis), `awakening` (sueño), `fullheal` (cualquier estado)

---

## Estados alterados (Fase J — implementado)

### Modelo de datos (`models.py`)
- `self.status: Optional[str] = None` — `"poison"` | `"paralysis"` | `"sleep"` | `None`
- `self.sleep_turns: int = 0` — turnos restantes dormido (asignado al aplicar sueño)
- `apply_status(status) -> bool` — aplica estado si no hay uno activo; asigna `sleep_turns = randint(1,3)` para sueño; devuelve `False` si ya hay estado
- `clear_status() -> None` — limpia `status` y `sleep_turns` a None/0

### Flujo de combate (`combat.py`)
- **Pantalla de batalla**: muestra `[PSN]` (morado), `[PAR]` (amarillo), `[SLP]` (azul) junto a la barra HP
- **Orden de turno** (`utils.py`): Pokémon paralizado usa `speed // 2` para determinar quién va primero
- **Check pre-ataque** (en `_take_turn()`, dentro de la rama `"attack"`):
  - Sueño: `sleep_turns -= 1`. Si llega a 0 → despierta y ejecuta el ataque. Si > 0 → skip con mensaje
  - Parálisis: 25% de probabilidad de skip. El jugador SÍ puede usar ítems o cambiar aunque esté dormido/paralizado
- **Aplicación de estados** (`_apply_attack()`): si el ataque tiene `"effect": {"kind": "status", "status": "...", "chance": N}`, al final del ataque se tira dado; si pasa y el defensor no tiene estado activo → `defender.apply_status()`
- **Veneno al fin de ronda** (`pokemon_combat()`): después de que ambos trainers actuaron, para cada Pokémon activo con `status == "poison"`: `take_damage(max(1, maximun_hp // 8))`. **CRÍTICO:** si el Pokémon queda a 0 HP, se llama `_handle_faint_and_switch()` inmediatamente; si no hay sustituto, se declara victoria y se termina el combate sin arrancar otro turno

### Ataques de estado en `data/attacks.json`
| Ataque | Tipo | Dmg | PP | Efecto | Propietarios |
|--------|------|-----|----|--------|--------------|
| Thunder Wave | Electric | 0 | 20 | 100% parálisis | Magnemite, Magneton |
| Toxic | Poison | 0 | 10 | 100% veneno | Venonat, Koffing, Weezing |
| Sleep Powder | Grass | 0 | 15 | 75% sueño | Bellsprout |
| Poison Sting | Poison | 15 | 35 | 30% veneno | Ekans |
| Poison Fang | Poison | 50 | 15 | 30% veneno | Arbok |

> **IMPORTANTE:** `data_io/checks/attacks.py` → `_validate_attack_obj()` ahora pasa el campo `"effect"` al output normalizado. La IA nunca elige ataques de 0 daño (Phase J simplificación aceptada; mejorará en Fase K).

### Ítems curativos de estado en `data/items.json`
```json
"antidote"   → cura veneno
"parlyzheal" → cura parálisis
"awakening"  → cura sueño
"fullheal"   → cura cualquier estado (effect sin campo "status")
```
`inventory.py._apply_status_cure()` — cura el estado si coincide con el `"status"` del efecto (o cualquiera si no hay campo "status")

### Normalización de ítems (`data_io/checks/items.py`)
- `_ALLOWED_ITEM_TYPES` incluye `"status_cure"`
- `_ALLOWED_EFFECT_KINDS` incluye `"cure_status"`
- `_validate_status_cure_effect()` valida el campo `"status"` opcional

### PC y captura
- `_heal_at_pokemon_center()`: llama `p.clear_status()` para todos los Pokémon; `already_healthy` también exige `status == None`
- `trigger_wild_marker_encounter()` y `trigger_wild_encounter()`: al capturar, llaman `wild_pokemon.clear_status()` antes de añadir al equipo

### Save backward-compat
- Saves sin `"status"` → restauran a `None` (sin estado)
- Saves sin `"sleep_turns"` → restauran a `0`

---

## Habilidades pasivas (Fase K — implementado)

- **`abilities.py`**: `ABILITY_BY_SPECIES` dict (nombre especie → nombre habilidad). Funciones de hook:
  - `fire_on_entry(pokemon, opponent, log)` — se ejecuta al entrar al combate (ej. Intimidate baja ataque rival)
  - `fire_pre_damage(attacker, defender, attack, log)` — antes de calcular daño (ej. modificar potencia)
  - `fire_on_hit_received(pokemon, damage, attacker, log)` — al recibir daño (ej. Static paraliza al atacante)
- **`combat.py`**: importa y llama los tres hooks en los puntos correspondientes del flujo de combate
- **`game/setup_game.py`**: importa `ABILITY_BY_SPECIES` para asignar habilidad al construir cada Pokémon
- La IA no elige ataques de estado (simplificación Fase J; mejorable en el futuro)

---

## Respawn y Rematches (Fases N+O — implementado)

Ambos implementados en `_check_respawn()` dentro de `map/__init__.py`, llamado en cada paso del jugador.

### Respawn wild markers (Fase N)
- Cooldown individual de **100 pasos** por marker
- Cada entrada en `cleared_wild_markers["main"]` guarda `(x, y, step_cleared)`
- Al iterar, si `steps - step_cleared >= 100` → eliminar de `cleared_main` y re-añadir a `objects`

### Rematches trainers (Fase O)
- Cooldown individual de **300 pasos** por entrenador
- Cada entrada en `defeated_trainers["main"]` guarda `(x, y, step_defeated)`
- Al rematchar, el equipo se escala con `dataclasses.replace(trainer_setup, team=scaled_team)`
- `scaled_team`: cada Pokémon sube al máximo de `(nivel_original + 2, nivel_promedio_equipo_jugador)`
- Sólo re-añade entrenadores hostiles (`not t.is_friendly`)

---

## Dungeon PN (Fase P — implementado)

Archivo: `map/dungeon_pn.py`. Cueva end-game de 40×20 accesible desde Pueblo Nuevo.

### Entidades
| Entidad | Tipo | Posición | Pokémon |
|---------|------|----------|---------|
| Onix | wild marker | (8, 3) | Onix |
| Battle Girl Nadia | trainer | (14, 3) | — |
| Gengar | wild marker | (20, 11) | Gengar |
| Kyle | trainer | (25, 10) | — |
| Champion Nexus | trainer (boss) | (35, 16) | Gengar Lv27, Rhydon Lv26, Alakazam Lv27, Arcanine Lv26 |

### Flujo post-victoria Champion Nexus
1. Guarda save con posición actual en `dungeon_pn`
2. Muestra cinemática `_champion_cinematic()`
3. Guarda save con `chapter2_unlocked=True`, posición `(153,61)`, `current_map="main"`
4. Retorna `"exit_pn"` al state machine de `main.py`

### Wild markers y respawn
- Los wild markers de dungeon_pn usan `cleared_markers_dict["dungeon_pn"]`
- Los trainers de dungeon_pn usan `defeated_dict["dungeon_pn"]`
- Actualmente no hay respawn/rematch implementado en dungeon_pn (solo en main overworld)

---

## Bugs conocidos / Deuda técnica

- **Deuda técnica:** `defeated_dict` en `main.py` se recarga desde disco en cada transición de mapa (I/O redundante). `cleared_markers_dict` usa el patrón correcto (mutación en RAM por referencia). Pendiente refactorizar `defeated_dict` para igualar.
- **Respawn/rematch en dungeon y dungeon_pn:** `_check_respawn()` solo opera sobre `main`. Dungeon y dungeon_pn no tienen respawn/rematch (no crítico por ahora).
- La IA nunca elige ataques de estado (0 daño); simplificación aceptada en Fase J.
- El PC cura TODO el equipo (comportamiento estándar).
- `experience.py._apply_species()` no actualiza `evolution_by_item` tras evolución por nivel (no es problema porque los Pokémon con stone evolutions no tienen level evolutions).
