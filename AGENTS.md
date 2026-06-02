# Pokemon_Game — Agent Context

> Última actualización: 2026-06-02 — **Paquete 3 COMPLETO** (R1+B4 ya estaban; ahora R5/R2/R3 cerrados: `pause()`, helpers de selección, refactor del menú de bolsa + confirmación de piedra evolutiva). **Proyecto sellado — pausa momentánea del desarrollo.** Capítulos 1–2 y Paquetes 1–3 completos y verificados.

---

## 1. Project purpose

Juego de Pokémon por terminal (ASCII) en Python. Combate por turnos con sistema de PP, estados alterados y habilidades pasivas. Exploración por overworld 160×65 con 6 zonas, cueva bidireccional 60×30 y cueva end-game 40×20 en Pueblo Nuevo. Entrenadores NPC con diálogos y rematches, Pokémon salvajes con respawn, inventario completo, Pokédex con registro visto/capturado, y guardado por slots con nombre. El juego está organizado en capítulos: **Capítulo 1 (Fase P) y Capítulo 2 (Fase Q) completados**. El Capítulo 2 añade un segundo mundo (overworld 120×50) con save multi-mundo v2, portal bidireccional y jefe final Echo Guardian.

---

## 2. Current stable state

- El combate por turnos está completamente funcional: PP, Struggle, estados alterados, habilidades pasivas, efectividad de tipos, buffs, captura.
- El mapa ASCII está refactorizado en módulos: overworld 160×65, cueva 60×30, cueva PN 40×20, **Mundo 2 120×50** (`map/world2/`).
- **Fase P completada**: cueva end-game dungeon_pn con Champion Nexus → `chapter2_unlocked=true`.
- **Fase Q (Q1–Q4) completada y verificada**: arquitectura multi-mundo (save v2), portal World1↔World2, overworld del Mundo 2 con 5 zonas, 5 NPCs, 8 entrenadores, 8 wild markers, encuentros salvajes, rematches, y jefe final Echo Guardian → `world2_completed=true`.
- **Paquetes 1–2 completados**: renderizado anti-flicker (`map/terminal.py` — redibujado in-place, sin `cls` por frame), y **sistema de dificultad** (easy/normal/hard) con daño enemigo asimétrico, XP escalada e IA que lanza ataques de estado. Campo global `difficulty` en el save.
- **Paquete 3 completado**: R1 (respawn centralizado en `game/respawn.py`) + B4 (validación estricta de especies + limpieza de datos) + **R5/R2/R3** (módulo `ui_common.py` con `pause()`, `collect_attacks()`, `pick_pokemon()`; refactor de las 3 ramas del menú de bolsa + confirmación estricta `[y/N]` antes de consumir piedra evolutiva). Verificado con compileall + smoke test headless.
- Saves son retrocompatibles: la migración v1→v2 es automática y no destructiva; los saves sin `difficulty` cargan como `"normal"`.

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
├── ui_common.py             # Paquete 3 (R5/R2/R3): pause(), collect_attacks(), pick_pokemon() — helpers UI (leaf, sin imports internos)
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
│   ├── pokemons.json        # Stats base de 67 especies (solo 32 tienen ataques en attacks.json)
│   ├── attacks.json         # Ataques por propietario — campo "pp" obligatorio, "effect" en ataques de estado
│   ├── items.json           # 26 ítems: healing, revive, buff, capture, evolution, status_cure
│   └── type_effectiveness.json
├── controllers/
│   ├── human.py             # HumanController — muestra PP: X/Y, filtra PP=0, auto-Struggle
│   └── ia.py                # IAcontroller — filtra PP=0, fallback Struggle; Q1: _status_attacks_of()
│                            #   y rama de ataque de estado por probabilidad de dificultad
├── game/
│   ├── setup_game.py        # Zone, WildMarker, TrainerSetup(is_boss) — ZONES, TRAINERS, DUNGEON_TRAINERS,
│   │                        # DUNGEON_PN_TRAINERS; Fase Q: ZONES_WORLD_2, WORLD2_FRIENDLY_NPCS,
│   │                        # WORLD2_TRAINERS, WORLD2_BOSS, WORLD2_WILD_MARKERS,
│   │                        # get_world2_objects(), get_world2_wild_marker_objects()
│   │                        # get_zone_for_position(x,y,world_id), get_zone_by_id(id,world_id)
│   │                        # B4: _build_pokemon() lanza UnknownSpeciesError/SpeciesWithoutAttacksError
│   ├── encounters.py        # trigger_encounter(), trigger_wild_encounter(...,world_id), trigger_wild_marker_encounter()
│   ├── save_load.py         # save_game(...,current_world), load_game(), restore_player_trainer(),
│   │                        # load_defeated_dict(sd,world_id), load_cleared_markers(sd,world_id),
│   │                        # _migrate_v1_to_v2(), load_world_state() — schema v2
│   ├── ui_menus.py          # open_bag_menu(), open_pokedex(), show_team_summary()
│   ├── ui_utils.py          # _hp_bar()
│   ├── difficulty.py        # Paquete 2: presets easy/normal/hard + getters (estado global de sesión)
│   ├── respawn.py           # Paquete 3 (R1): check_respawn() unificado W1/W2 + _player_avg_level()
│   └── world.py             # (reservado)
├── map/
│   ├── __init__.py          # run_map(...,chapter2_unlocked); llama game.respawn.check_respawn();
│   │                        # _heal_at_pokemon_center(); WORLD2_PORTAL_POS=(140,55) → "travel_to_world2";
│   │                        # guard de spawn (None,None) en partida nueva → PLAYER_START
│   ├── terminal.py          # Paquete 1: anti-flicker + ANSI compartido (render_frame, clear_once, hide_cursor)
│   ├── tiles.py             # OBSTACLE_GRID, _build_map() — overworld 160×65
│   ├── dungeon.py           # DUNGEON_GRID, run_dungeon() — cueva 60×30, tránsito bidireccional
│   ├── dungeon_pn.py        # DUNGEON_PN_GRID, run_dungeon_pn() — cueva end-game 40×20 (Fase P)
│   ├── player.py            # PlayerState: posición, movimiento, get_new_position(), apply_move()
│   ├── renderer.py          # render() — colores ANSI por zona (Mundo 1; NO tocar para World 2)
│   ├── events.py            # check_collision()
│   └── world2/              # Fase Q — Mundo 2 (motor independiente)
│       ├── tiles.py         # WORLD2_OBSTACLE_GRID 120×50, 5 zonas, WORLD2_PC_POS=(22,8)
│       ├── renderer.py      # render_world2(pos, objects) — paleta propia; ! wild, N npc, ★ jefe
│       └── main.py          # run_world2_map(), _chapter2_complete_cinematic() (respawn vía game.respawn)
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
| **Q1** | **Arquitectura multi-mundo: save v2, `current_world`, migración v1→v2, portal World1↔World2** | ✅ |
| **Q2** | **Overworld Mundo 2 (120×50): 5 zonas + renderer independiente (`map/world2/`)** | ✅ |
| **Q3** | **5 NPCs narrativos + Centro Pokémon + `world_id` en encuentros** | ✅ |
| **Q4** | **8 entrenadores + 8 wild markers + salvajes + jefe Echo Guardian + rematches** | ✅ |
| **Pkg 1** | **Anti-flicker (`map/terminal.py`, redibujado in-place) + consolidación ANSI (R4) + fixes daño B1/B3 + limpieza código muerto (EvolvedPokemon)** | ✅ |
| **Pkg 2** | **Sistema de Dificultad easy/normal/hard (daño enemigo asimétrico + XP) + IA táctica Q1 (ataques de estado) + fix spawn partida nueva** | ✅ |
| **Pkg 3 (R1+B4)** | **Respawn centralizado (`game/respawn.py`, unifica W1/W2) + validación estricta de especies (B4) + limpieza de 16 refs NOATK/inexistentes (Champion Nexus ahora con 4 Pokémon)** | ✅ |
| **Pkg 3 (R5/R2/R3)** | **`ui_common.py`: `pause()` (centraliza ~30 `input("Press Enter…")`), `collect_attacks()`/`pick_pokemon()` (deduplican human/ia/ui_menus); refactor de las 3 ramas de `_use_item_out_of_battle` + confirmación estricta `[y/N]` antes de gastar piedra evolutiva** | ✅ |

### Paquete 3 — Refactor estructural y QoL (COMPLETO: R1 + B4 + R5/R2/R3)

- **R1 — `game/respawn.py`**: `check_respawn(steps, player_trainer, cleared_list, defeated_list, objects, wild_markers, trainers)` unifica los antiguos `_check_respawn` (World 1) y `_check_respawn_world2`. Markers 100 pasos, rematches 300; filtro `is_boss`/`is_friendly` generalizado. Sin imports del proyecto (recibe listas como args) → sin ciclos. `_player_avg_level()` migrado aquí.
- **B4 — validación estricta**: `_build_pokemon()` lanza `UnknownSpeciesError` (inexistente) o `SpeciesWithoutAttacksError` (NOATK), ambas `InvalidSpeciesError(ValueError)`. `restore_player_trainer()` tolera saves legacy (omite con aviso).
- **Limpieza de datos**: Eevee→Pikachu, Staryu/Tentacool→Poliwag/Psyduck, Gengar→Haunter, Alakazam→Abra, Arcanine→Charizard, Machoke→Primeape, Gastly→Haunter, Onix→Graveler, Charmander→Charmeleon. Corrige equipos silenciosamente reducidos (Champion Nexus peleaba solo con Rhydon).
- **R5 — `pause(message="  Press Enter to continue...")`** en `ui_common.py`: centraliza ~30 `input("Press Enter…")` (combat, encounters, ui_menus, human, map/__init__, dungeon, dungeon_pn, world2/main, main). Cada llamada pasa su texto original; los `input()` que capturan opciones NO se tocaron.
- **R2 — `collect_attacks(pokemon)` y `pick_pokemon(candidates, *, title, formatter, prompt, loop=False)`** en `ui_common.py`: deduplican la recogida de ataques (`human.ChooseAttack`, `ia._all_attacks_of`) y la selección de Pokémon (`ui_menus`, `human._pick_fainted`). `ui_common.py` es un módulo *leaf* (solo stdlib) → importable desde `combat.py` sin reabrir el ciclo `combat↔map`.
- **R3 — menú de bolsa**: `_use_item_out_of_battle()` colapsa sus 3 ramas casi idénticas (revive/evolution/healing) en un único flujo vía `pick_pokemon()`. **Confirmación estricta** `Use <Stone> on <Pokémon>? [y/N]` (default No) antes de consumir una **piedra evolutiva** (ítem irreversible). Verificado: NO cancela sin gastar; YES evoluciona y consume.

### Paquete 2 — Sistema de Dificultad e IA táctica

- **`game/difficulty.py`**: estado global de sesión (set una vez en `main.py` al crear/cargar). Presets: `easy` (daño ×0.75, XP ×1.25, IA estado 10%), `normal` (×1.00/×1.00/20%), `hard` (×1.30/×0.85/45%). Getters: `enemy_damage_multiplier()`, `xp_multiplier()`, `ai_status_chance()`.
- **Daño asimétrico** (`combat.py`): `_apply_attack(..., damage_multiplier)` se escala solo cuando el atacante es `IAcontroller` (en `_take_turn`). El jugador nunca recibe penalización a su propio daño. Import lazy para evitar el ciclo combat↔game.
- **XP** (`experience.py`): pool ×`xp_multiplier()` en `finalize_and_award` (helper con fallback 1.0).
- **IA Q1** (`controllers/ia.py`): `_status_attacks_of()` recoge ataques de estado puros (daño 0); `ChooseAction` los lanza con probabilidad `ai_status_chance()` si el rival no tiene estado.
- **Persistencia** (`save_load.py`): campo global `"difficulty"` con merge no-destructivo; default `"normal"` en migración v1→v2 y saves antiguos.
- **Menú** (`main.py`): `_ask_difficulty()` `[1] Fácil [2] Normal [3] Difícil` solo en partida nueva.

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

### Fase Q — Detalle del Mundo 2 / Capítulo 2

- **Acceso**: portal en Pueblo Nuevo `(140,55)` con `chapter2_unlocked=True` → `run_world2_map()`. Spawn en `(15,8)` (Aldea Aurora). Retorno por ▲ `(14,8)`.
- **Mapa**: 120×50, viewport 40×20 con scroll. 5 zonas conectadas por 7 corredores: Aldea Aurora (cyan, safe zone con PC en `(22,8)`), Bosque Milenario (verde), Meseta Ventosa (amarillo), Lago Cristal (azul), Templo Eco (gris).
- **Save v2**: `current_world` despacha el state machine. `steps` independiente por mundo. `world2_completed=True` al vencer al jefe.
- **5 NPCs** (`WORLD2_FRIENDLY_NPCS`, one-shot): Sage Lyra, Lost Researcher, Builder Aren, Fisher Old Tom, Pilgrim Eli.
- **8 entrenadores** (`WORLD2_TRAINERS`, Lv29-34, rematch a 300 pasos con equipo escalado).
- **8 wild markers** (`WORLD2_WILD_MARKERS`, Lv31-34: Arbok, Rhydon, Primeape, Greninja, Wartortle, Haunter, Magneton, Charizard).
- **Encuentros salvajes**: 4 zonas a 0.04 (Aldea 0.0), niveles 25-32.
- **Jefe `WORLD2_BOSS`** (`is_boss=True`): Echo Guardian `(105,15)` — Magneton 36, Arbok 37, Rhydon 38, Charizard 39, Mewtwo 40. Al vencerlo: `world2_completed=True` + cinemática; el jugador permanece en el Mundo 2.
- **Rematches**: desde el Paquete 3 (R1), World 2 usa el `check_respawn()` centralizado de `game/respawn.py` (con `WORLD2_WILD_MARKERS`/`WORLD2_TRAINERS`); el filtro `is_boss`/`is_friendly` (jefe y NPCs nunca reaparecen) vive ahora dentro de esa función.
- **CRÍTICO**: el Mundo 2 usa solo las **32 especies con ataques** de `attacks.json`. Una especie inexistente crashea el normalizador; una `NOATK` pelearía solo con Struggle.

---

## 6. Known bugs / technical debt

### Bugs resueltos (Paquetes 1–3)

- **Equipos silenciosamente reducidos (Pkg 3 · B4)**: el Champion Nexus tenía 3 especies inexistentes en `pokemons.json` (Gengar/Alakazam/Arcanine) que `_build_pokemon` omitía devolviendo `None` → peleaba solo con Rhydon. Igual Battle Girl Nadia (Machoke). Corregido curando los datos + validación estricta que ahora lo impediría.
- **Spawn en partida nueva** (`map/__init__.py`): `position=(None,None)` es una tupla *truthy*, así que el guard `if start_pos` no caía al spawn por defecto → `player.pos=(None,None)` → crash en `renderer.render`. Corregido: el guard ahora verifica `start_pos and start_pos[0] is not None`. Era un bug latente desde Q1 (solo se reproducía creando partida desde cero).
- **B1** (`damage.py`): `_lookup_chart` ya no cae en la fila del defensor cuando falta la del atacante (usaba un `or` erróneo) → efectividad correcta con default 1.0.
- **B3** (`damage.py`): el mensaje de efectividad ya no dice "Special attack" impreciso.
- **Código muerto**: eliminada la clase `EvolvedPokemon` de `models.py` (referenciaba `self.base_attack` inexistente).

### Deuda técnica

- `defeated_dict` en `main.py` se recarga desde disco en cada transición de mapa (I/O redundante). `cleared_markers_dict` ya usa el patrón correcto (mutación en RAM por referencia). Ver TODO en `main.py`.
- La IA usa ataques de estado **puros** (daño 0) por probabilidad de dificultad (Q1); aún no integra los de daño+estado en su scoring táctico ni cambia de Pokémon por estado.
- Static actualmente se activa con cualquier ataque; debería requerir flag de "contacto" en `attacks.json`.
- Dungeon wild markers (Geodude, Haunter en `DUNGEON_WILD_MARKERS`) no tienen respawn — `check_respawn` solo se invoca desde el overworld de cada mundo.

---

## 7. Save/progress rules

### Formato del save (v2 multi-mundo — Fase Q1)

`SAVE_VERSION = 2`. **Globales**: `team`, `bag`, `pokedex`, `chapter2_unlocked`, `world2_completed`, `difficulty`. **Per-world** (en `worlds.<id>`): `current_map`, `position`, `defeated_trainers`, `cleared_wild_markers`. `steps` independiente por mundo.

```json
{
  "slot_name": "mi_partida", "save_version": 2, "current_world": "world1",
  "difficulty": "normal", "chapter2_unlocked": true, "world2_completed": false,
  "steps": {"world1": 336, "world2": 37},
  "team": [ ... ], "bag": { ... }, "pokedex": [ ... ],
  "worlds": {
    "world1": {"current_map": "main", "position": {"x": 139, "y": 54},
               "defeated_trainers": {"main": [], "dungeon": [], "dungeon_pn": []},
               "cleared_wild_markers": {"main": [], "dungeon": [], "dungeon_pn": []}},
    "world2": {"current_map": "world2_main", "position": {"x": 15, "y": 8},
               "defeated_trainers": {"world2_main": []},
               "cleared_wild_markers": {"world2_main": []}}
  }
}
```

(Ejemplo completo y `WORLD_MAPS` en `CLAUDE.md` → "Estructura de save v2".)

### Reglas críticas

- Listas de entidades: `[x, y, step]`. Backward-compat: `[x, y]` trata `step=0`.
- **`save_game(..., current_world=...)`** persiste el mundo activo y hace **merge no-destructivo**: lee el save de disco antes de escribir para preservar intacto el mundo inactivo. Nunca escribas un save sin pasar el `current_world` correcto.
- `chapter2_unlocked` (al vencer Champion Nexus) y `world2_completed` (al vencer Echo Guardian) se escriben `True` y nunca se revierten a `False` (el merge usa `OR` con el valor en disco).
- `_load_runtime_state(save_data)` en `main.py` arma el estado por mundo; el loop despacha por `(current_world, current_map)`.
- `cleared_markers_dict` pasa por referencia (RAM); `defeated_dict` se recarga de disco (deuda técnica heredada).
- En World 1, `_cur_dict()` debe incluir SIEMPRE `"main"`, `"dungeon"`, `"dungeon_pn"`. En World 2, `_cur_dict()` usa `"world2_main"`.

### Backward-compat de saves viejos

- **Migración v1→v2** automática (`_migrate_v1_to_v2()`): saves sin `save_version>=2` mueven `current_map`/`position`/`defeated_trainers`/`cleared_wild_markers` a `worlds.world1` y `steps` int → `{"world1": N, "world2": 0}`. No persiste hasta el siguiente `save_game()`.
- Sin `"pp"` → PP al máximo. Sin `"status"`/`"sleep_turns"` → `None`/`0`. Sin `chapter2_unlocked`/`world2_completed` → `False`.
- `"defeated_trainers"` lista plana → migrada. `"pokedex"` lista de strings → dicts con `caught: false`.

---

## 8. Next phase

**Capítulo 1 (Fases 1–P), Capítulo 2 (Fase Q: Q1–Q4) y Paquetes de pulido 1–3 COMPLETOS y verificados. Proyecto sellado el 2026-06-02 — pausa momentánea del desarrollo.** No hay fases pendientes planificadas.

Líneas futuras posibles (no planificadas — requieren diseño y aprobación del usuario antes de implementar):
- **Capítulo 3** (`world3`): el patrón multi-mundo (save v2, state machine por `current_world`, `map/worldN/`) ya lo soporta. Replicar la estructura de `map/world2/` y añadir `"world3"` a `WORLD_IDS`/`WORLD_MAPS`.
- Respawn/rematch en las dungeons (`dungeon`, `dungeon_pn`).
- IA de estado más táctica: integrar ataques de daño+estado en el scoring y cambiar de Pokémon ante un estado (hoy solo lanza estados puros por probabilidad — Paquete 2 / Q1).
- Menú in-game para cambiar la dificultad a media partida (hoy solo se elige al crear).
- Ampliar `attacks.json` para dar ataques a las 35 especies `NOATK` (hoy inutilizables en combate real).

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
