# Pokemon_Game — Agent Context

> Última actualización: 2026-05-26 — Fase P completada y verificada.

---

## 1. Project purpose

Juego de Pokémon por terminal (ASCII) en Python. Combate por turnos con sistema de PP, estados alterados y habilidades pasivas. Exploración por overworld 160×65 con 6 zonas, cueva bidireccional 60×30 y cueva end-game 40×20 en Pueblo Nuevo. Entrenadores NPC con diálogos y rematches, Pokémon salvajes con respawn, inventario completo, Pokédex con registro visto/capturado, y guardado por slots con nombre. El juego está organizado en capítulos: Capítulo 1 completado (Fase P), Capítulo 2 pendiente (Fase Q).

---

## 2. Current stable state

- El combate por turnos está completamente funcional: PP, Struggle, estados alterados, habilidades pasivas, efectividad de tipos, buffs, captura.
- El mapa ASCII está refactorizado en módulos: overworld 160×65, cueva 60×30, cueva PN 40×20.
- **Fase P completada y verificada en ejecución**: cueva end-game dungeon_pn con Nadia, Kyle y Champion Nexus. Al derrotar al Champion se guarda `chapter2_unlocked=true` y el jugador retorna al overworld.
- Saves son retrocompatibles con versiones anteriores de todas las fases.

---

## 3. Architecture rules

### Separación map/ vs game/

- `map/` se encarga exclusivamente de: tiles, render, movimiento del jugador, viewport, colisiones, triggers de transición entre mapas, loops de cada mapa.
- `game/` se encarga de: trainers, wild markers, objetos, encuentros, eventos narrativos, capítulos, setup de datos de juego.
- **NUNCA** meter datos de entrenadores, spawns, ni wild markers dentro de `map/`. Todo eso va en `game/setup_game.py`.

### Reglas generales

- No hacer `main.py` monolítico. La state machine de mapas es lo único que vive ahí.
- Funciones pequeñas y testeables. No mezclar responsabilidades.
- Antes de tocar cualquier sistema existente, revisar sus dependencias (save format, _cur_dict, defeated_dict).
- No romper saves ni el progreso existente. Siempre añadir campos nuevos con valores por defecto y backward-compat en los loaders.
- Preservar compatibilidad con los datos JSON actuales (pokemons.json, attacks.json, items.json).
- Todo el código en inglés. Comunicación con el usuario en español.

---

## 4. Important files and folders

```
Pokemon_Game/
├── main.py                  # Menú principal, state machine de mapas (while True sobre current_map)
├── combat.py                # Motor de combate por turnos — PP, Struggle, estados, veneno fin de ronda
├── models.py                # Clase Pokemon: PP tracking, apply_status/clear_status, ability hook
├── trainers.py              # Clase Trainer: pokedex_seen, register_seen(), register_caught()
├── inventory.py             # Clase Inventory: healing, revive, buff, evolution, status_cure
├── damage.py                # Cálculo de daño, efectividad de tipos, buffs de estadísticas
├── experience.py            # ExperienceManager, _apply_species(), evolución por nivel
├── abilities.py             # ABILITY_BY_SPECIES — hooks: fire_on_entry, fire_pre_damage, fire_on_hit_received
├── utils.py                 # clamp(), determine_attack_order() — speed//2 si paralysis
├── data_io/
│   ├── __init__.py          # load_attacks(), load_pokemons(), load_items(), load_type_chart()
│   ├── loaders.py           # load_dataset(), read_json_cached()
│   ├── paths.py             # data_dir()
│   ├── errors.py            # DataIOError, DataValidationError, DataPathError
│   └── checks/
│       ├── pokemons.py      # validate + normalize — indexado lowercase, campo base_attack
│       ├── attacks.py       # validate + normalize — campos pp y effect
│       ├── items.py         # validate + normalize — tipo status_cure
│       └── type_effectiveness.py
├── data/
│   ├── pokemons.json        # Stats base de 73 especies
│   ├── attacks.json         # Ataques por propietario — campo "pp" obligatorio, "effect" en ataques de estado
│   ├── items.json           # 26 ítems: healing, revive, buff, capture, evolution, status_cure
│   └── type_effectiveness.json
├── controllers/
│   ├── human.py             # HumanController — muestra PP: X/Y, filtra PP=0, auto-Struggle
│   └── ia.py                # IAcontroller — filtra PP=0, fallback Struggle
├── game/
│   ├── setup_game.py        # Zone, WildMarker, TrainerSetup — ZONES, TRAINERS, DUNGEON_TRAINERS,
│   │                        # DUNGEON_PN_TRAINERS, DUNGEON_PN_WILD_MARKERS
│   │                        # get_map_objects(), get_dungeon_objects(), get_dungeon_pn_objects(), etc.
│   ├── encounters.py        # trigger_encounter(), trigger_wild_encounter(), trigger_wild_marker_encounter()
│   ├── save_load.py         # save_game(), load_game(), restore_player_trainer(),
│   │                        # load_defeated_dict(), load_cleared_markers()
│   ├── ui_menus.py          # open_bag_menu(), open_pokedex(), show_team_summary()
│   ├── ui_utils.py          # _hp_bar()
│   └── world.py             # (reservado para arquitectura multi-mundo — Fase Q)
├── map/
│   ├── __init__.py          # run_map(), _check_respawn(), _player_avg_level(), _heal_at_pokemon_center()
│   ├── tiles.py             # OBSTACLE_GRID, _build_map() — overworld 160×65
│   ├── dungeon.py           # DUNGEON_GRID, run_dungeon() — cueva 60×30, tránsito bidireccional
│   ├── dungeon_pn.py        # DUNGEON_PN_GRID, run_dungeon_pn() — cueva end-game 40×20 (Fase P)
│   ├── player.py            # PlayerState: posición, movimiento, get_new_position(), apply_move()
│   ├── renderer.py          # render() — colores ANSI por zona, viewport 40×20
│   └── events.py            # check_collision()
├── saves/                   # Partidas guardadas ({nombre}.json) — NO subir a git
├── requirements.txt         # readchar>=2.0.0, pytest>=7.0.0
├── pyproject.toml           # Build system (setuptools)
└── setup.cfg                # Package metadata: name=pokemon-game, version=0.1.0
```

---

## 5. Completed phases

| Fase | Descripción | Estado |
|------|-------------|--------|
| 1–14 | Base: modelos, combate, IA, daño, XP, inventario, mapa, captura, wild markers | ✅ |
| A | Colores ANSI en el mapa por zona | ✅ |
| B | UI de combate estilo clásico (barras HP con color, log de batalla) | ✅ |
| C | Balance de stats starters + ataques normales de fallback | ✅ |
| Bug Fix 1 | `trigger_encounter()` retorna `False` si el jugador pierde | ✅ |
| Bug Fix 2 | Pokéballs agregadas a reward_pool de trainers por zona | ✅ |
| D | Submapa independiente: Cueva Oscura 60×30, renderer oscuro | ✅ |
| E | Overworld 160×65: Ruta del Mar + Pueblo Nuevo + PC2 | ✅ |
| F | Pokédex en juego (tecla P) — lista todos los Pokémon, ★ capturados | ✅ |
| G | Evolución por ítems (Fire/Water/Thunder/Leaf/Moon Stone) | ✅ |
| H | UI/UX: HP bars en selector, tecla T equipo, bolsa por categorías | ✅ |
| I | Sistema de PP: usos limitados, Struggle, restauración en PC | ✅ |
| J | Estados alterados: Veneno, Parálisis, Sueño + ítems curativos | ✅ |
| K | Habilidades pasivas: Static, Intimidate, Sturdy, Levitate | ✅ |
| L | Pokédex extendida: ◆ visto / ★ capturado + nivel de captura | ✅ |
| M | Refactor save: `cleared_wild_markers` separado de `defeated_trainers` | ✅ |
| N | Respawn de wild markers — cooldown individual 100 pasos | ✅ |
| O | Rematches de trainers — cooldown individual 300 pasos, equipo escalado | ✅ |
| **P** | **Cueva end-game Pueblo Nuevo + Champion Nexus + chapter2_unlocked** | ✅ |

### Fase P — Detalle de dungeon_pn

- **Entrada desde overworld**: columnas 152–155, y=62 (Pueblo Nuevo, extremo norte)
- **Tamaño**: 40×20 — el viewport cubre toda la cueva (sin scroll)
- **Spawn de entrada**: `DUNGEON_PN_START = (2, 2)`
- **Salida ▲**: `DUNGEON_PN_EXIT = (2, 1)` — única salida, retorna al overworld en `(153, 61)`
- **Layout** (6 carves): entry room → entry corridor → vertical shaft → middle room → deep vertical → champion chamber
- **Trainers**:
  | Entrenador | Posición | Equipo |
  |---|---|---|
  | Battle Girl Nadia | (14, 3) | Machoke Lv20, Graveler Lv21 |
  | Veteran Kyle | (25, 10) | Haunter Lv22, Rhydon Lv23, Magneton Lv22 |
  | Champion Nexus | (35, 16) | Gengar Lv27, Rhydon Lv26, Alakazam Lv27, Arcanine Lv26 |
- **Wild markers**:
  | Pokémon | Nivel | Posición |
  |---|---|---|
  | Onix | 20 | (8, 3) |
  | Gengar | 22 | (20, 11) |
- **Cinemática post-victoria**: `_champion_cinematic()` — texto + pausa al derrotar a Champion Nexus
- **Save tras Champion Nexus**: doble guardado — primero normal (en dungeon_pn), luego final con `chapter2_unlocked=True` y `current_map="main"`, posición `OVERWORLD_RETURN_PN = (153, 61)`
- **Retorno**: `return "exit_pn"` — `main.py` recarga el save y entra al loop de `run_map()`
- **Progreso de las 3 cuevas persiste**: `_cur_dict()` en las 3 funciones `run_*()` incluye las claves `"main"`, `"dungeon"` y `"dungeon_pn"` — ningún save borra el progreso de las otras cuevas

---

## 6. Known bugs / technical debt

### Bug activo — `EvolvedPokemon.combined_attack()`

- **Archivo**: `models.py`, línea ~199
- **Síntoma**: `self.base_attack` es referenciado pero `EvolvedPokemon.__init__` no recibe ni asigna ese atributo. Si se llama `combined_attack()`, puede fallar con `AttributeError` dependiendo de si `Pokemon.__init__` lo inicializa a 0 o no.
- **Estado**: código legado (nunca se llama en el flujo actual del juego). No bloquea ninguna fase.
- **Acción recomendada**: eliminar `EvolvedPokemon` de `models.py` si no se usa, o arreglarlo si se reactiva.

### Deuda técnica

- `defeated_dict` en `main.py` se recarga desde disco en cada transición de mapa (I/O redundante). `cleared_markers_dict` ya usa el patrón correcto (mutación en RAM por referencia). Ver TODO en `main.py` línea ~137.
- Static actualmente se activa con cualquier ataque; debería requerir flag de "contacto" en `attacks.json`.
- Dungeon wild markers (Geodude, Gastly en `dungeon.py`) no tienen respawn — la Fase N solo aplica al overworld.

---

## 7. Save/progress rules

### Formato actual del save

```json
{
  "slot_name": "mi_partida",
  "current_map": "main",
  "steps": 45,
  "chapter2_unlocked": false,
  "position": {"x": 20, "y": 43},
  "team": [
    {
      "name": "Charmeleon", "level": 5, "health": 68, "exp": 0,
      "pp": {"Ember": 20, "Flamethrower": 15, "Scratch": 35},
      "status": null, "sleep_turns": 0
    }
  ],
  "bag": {"potion": 2, "xdefense": 1, "pokeball": 5},
  "defeated_trainers": {
    "main":       [[10, 44, 14]],
    "dungeon":    [[15, 8, 0]],
    "dungeon_pn": []
  },
  "cleared_wild_markers": {
    "main":       [[15, 32, 41]],
    "dungeon":    [],
    "dungeon_pn": []
  },
  "pokedex": [
    {"name": "Charmeleon", "caught": true,  "level_caught": 5},
    {"name": "Zubat",      "caught": false, "level_caught": null}
  ]
}
```

### Reglas críticas

- Listas de entidades: `[x, y, step_derrota]`. Backward-compat: `[x, y]` trata `step=0`.
- `_cur_dict()` dentro de cada `run_*()` **debe incluir siempre las 3 claves**: `"main"`, `"dungeon"`, `"dungeon_pn"`. Si falta una clave, ese save borrará el progreso de esa cueva.
- `chapter2_unlocked` se escribe `True` solo al derrotar a Champion Nexus y nunca se sobreescribe a `False`.
- `save_game()` acepta `chapter2_unlocked` como kwarg con default `False`. Al recargar, `load_game()` lee el valor actual del JSON — así no se pierde aunque se guarde desde otro mapa.
- Transición de mapa: `main.py` siempre recarga el save con `load_game()` tras cada `run_*()` para obtener `current_map` y `position` autoritativos.
- `cleared_markers_dict` pasa por referencia — sus mutaciones son visibles inmediatamente en `main.py` sin recargar disco.
- `defeated_dict` se recarga desde disco (deuda técnica pendiente).

### Backward-compat de saves viejos

- Sin campo `"pp"` → PP inicializado al máximo.
- Sin campo `"status"` / `"sleep_turns"` → `None` / `0`.
- Sin campo `"chapter2_unlocked"` → `False`.
- Sin claves `"dungeon_pn"` en defeated/cleared dicts → `[]`.
- `"defeated_trainers"` como lista plana (saves muy viejos) → migrada automáticamente.
- `"pokedex"` como lista de strings → migrada a lista de dicts con `caught: false`.

---

## 8. Next phase

### Fase Q — Capítulo 2 / Mundo Nuevo

**Estado: NO implementada. No iniciar hasta aprobación explícita del usuario.**

| Subfase | Descripción |
|---------|-------------|
| Q1 | Desbloqueo técnico y transición al Mundo Nuevo — leer `chapter2_unlocked`, trigger de entrada, `current_world` en save |
| Q2 | Mapa base del Mundo Nuevo — nuevo archivo de tiles, grid, renderer |
| Q3 | NPCs narrativos básicos — diálogos de introducción al nuevo mundo |
| Q4 | Trainers, wild markers, eventos y recompensas del Mundo Nuevo |

**Prerequisito**: `chapter2_unlocked=True` en el save (escrito por Fase P al derrotar a Champion Nexus).

---

## 9. How to run

### Opción A — Con instalación editable (recomendada)

```powershell
# Desde la raíz del proyecto: c:\...\Pokemon-Game\
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
python -m Pokemon_Game
```

### Opción B — Sin instalar, desde el directorio padre

```powershell
# Entrar al directorio PADRE de Pokemon-Game:
cd "c:\Users\Usuario\OneDrive\Documentos"
python -m Pokemon-Game
# Nota: el guion en el nombre de la carpeta puede causar problemas.
# Si falla, usar la Opción A (pip install -e .).
```

### Probar transición de Fase P manualmente

1. Crear partida nueva o cargar una existente.
2. Navegar al extremo norte de Pueblo Nuevo (cols 152–155, y≈62).
3. Al entrar en la cueva, verificar que aparece el mapa 40×20 con Nadia `T`, Kyle `T`, Champion Nexus `T` y los markers `!` de Onix y Gengar.
4. Derrotar a Champion Nexus → ver cinemática → verificar retorno al overworld en `(153,61)`.
5. Guardar manualmente (Q) y recargar → verificar que `chapter2_unlocked: true` está en el JSON de la partida.

---

## 10. Development workflow for future agents

### Antes de tocar cualquier archivo

1. Leer `AGENTS.md` y `CLAUDE.md` para entender el estado actual.
2. Hacer `git log --oneline -10` para ver las últimas fases.
3. Leer los archivos relevantes para la tarea (no editar de memoria).

### Workflow obligatorio por fase

1. **Explicar**: describir el problema, listar exactamente qué archivos se tocarán y qué cambios se harán.
2. **Esperar aprobación** del usuario antes de editar.
3. **Implementar** un paso pequeño a la vez — nunca agrupar varios cambios sin checkpoint.
4. **Explicar cómo probar** el cambio recién hecho.
5. **Esperar confirmación** de que el test pasó antes de avanzar al siguiente paso.

### Reglas de save format

- Al añadir un campo nuevo al save, siempre añadirlo con valor por defecto en `save_game()` y manejar su ausencia en `load_game()` / `restore_player_trainer()`.
- Nunca cambiar el formato de listas `[x, y, step]` sin mantener backward-compat con `[x, y]`.
- Siempre incluir las 3 claves de mapa en `_cur_dict()`.

### Al terminar una fase importante

- Actualizar la tabla de fases en este `AGENTS.md`.
- Actualizar `README.md` si cambió el estado general o el comando de ejecución.
- Hacer commit con mensaje descriptivo: `feat: Fase X — descripción breve`.

---

## Appendix — Arquitectura de mapas

### State machine (main.py)

```
while True:
    current_map == "main"      → run_map()       → "enter_dungeon" | "enter_dungeon_pn" | "quit"
    current_map == "dungeon"   → run_dungeon()   → "exit_west" | "exit_east" | "quit"
    current_map == "dungeon_pn"→ run_dungeon_pn()→ "exit_pn" | "quit"
```

Tras cada retorno (excepto "quit"), `main.py` recarga el save del disco para obtener `current_map` y `position` autoritativos.

### Transiciones de mapa

| Evento | Qué se guarda | Retorno de run_*() |
|--------|--------------|-------------------|
| Pisa cols 87-92, y=28 → cueva oeste | spawn `(3,2)`, `current_map="dungeon"` | `"enter_dungeon"` |
| Pisa x=118, rows 46-48 → cueva este | spawn `(57,26)`, `current_map="dungeon"` | `"enter_dungeon"` |
| Pisa ▲ en dungeon `(3,1)` → overworld | pos `(90,26)`, `current_map="main"` | `"exit_west"` |
| Pisa ▲ en dungeon `(57,27)` → overworld | pos `(119,47)`, `current_map="main"` | `"exit_east"` |
| Pisa cols 152-155, y=62 → cueva PN | spawn `(2,2)`, `current_map="dungeon_pn"` | `"enter_dungeon_pn"` |
| Pisa ▲ en dungeon_pn `(2,1)` → overworld | pos `(153,61)`, `current_map="main"` | `"exit_pn"` |
| Derrota Champion Nexus | pos `(153,61)`, `current_map="main"`, `chapter2_unlocked=True` | `"exit_pn"` |

### Constantes clave

```python
# map/__init__.py
POKEMON_CENTER_POS   = (9, 11)     # PC1 — Pueblo Alto
POKEMON_CENTER_2_POS = (129, 46)   # PC2 — Pueblo Nuevo

# map/dungeon.py
DUNGEON_START          = (3, 2)    # spawn al entrar por el oeste
DUNGEON_START_EAST     = (57, 26)  # spawn al entrar por el este
DUNGEON_EXIT_POS       = (3, 1)    # salida oeste ▲
DUNGEON_EXIT_EAST_POS  = (57, 27)  # salida este ▲
MAIN_MAP_RETURN_WEST   = (90, 26)
MAIN_MAP_RETURN_EAST   = (119, 47)

# map/dungeon_pn.py
DUNGEON_PN_START       = (2, 2)    # spawn al entrar desde Pueblo Nuevo
DUNGEON_PN_EXIT        = (2, 1)    # salida ▲
OVERWORLD_RETURN_PN    = (153, 61) # posición de retorno al overworld
```

### Zonas del overworld (160×65)

| Zona | Coordenadas | Dificultad |
|------|-------------|------------|
| Pueblo Raiz | rows 28-48, cols 1-38 | Fácil (Lv 1-5) |
| Pueblo Alto | rows 1-21, cols 1-38 | Medio-bajo (Lv 5-10) |
| Bosque Umbral | rows 1-21, cols 44-118 | Medio-alto (Lv 8-14) |
| Cueva Oscura | rows 24-48, cols 87-118 | Difícil (Lv 12-18) |
| Ruta del Mar | rows 1-34, cols 119-158 | Difícil (Lv 12-18) |
| Pueblo Nuevo | rows 35-63, cols 119-158 | — (0% salvajes) |

Prioridad en `get_zone_for_position()`: pueblo_nuevo → ruta_del_mar → cueva_oscura → bosque_umbral → pueblo_alto → pueblo_raiz.
