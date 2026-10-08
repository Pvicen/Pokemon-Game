# Arquitectura

Mapa de referencia. El código es la fuente de verdad: posiciones, equipos, zonas y layouts de
mapa viven en `game/setup_game.py` y en los `tiles.py`/`dungeon*.py` de `map/`, no aquí.

## Módulos

| Ruta | Qué hace |
|---|---|
| `main.py` | Menú principal (cargar / nueva / borrar partida, dificultad) y máquina de estados de mapas |
| `jugar.py` | Lanzador: registra la raíz como paquete `Pokemon_Game` y llama a `main()` |
| `combat.py` | Combate por turnos: PP, Struggle (`STRUGGLE`), estados, captura, veneno a fin de ronda |
| `damage.py` | Daño, efectividad de tipos, buffs |
| `models.py` | Clase `Pokemon`: PP (`restore_all_pp`), estados (`apply_status`/`clear_status`) |
| `trainers.py` | Clase `Trainer` y Pokédex (`register_seen`/`register_caught`) |
| `inventory.py` | Ítems: curación, revivir, buffs, piedras (`_apply_evolution`), curas de estado |
| `experience.py` | `ExperienceManager`, evolución por nivel (`_apply_species`) |
| `abilities.py` | `ABILITY_BY_SPECIES` y hooks `fire_on_entry`/`fire_pre_damage`/`fire_on_hit_received` |
| `controllers/` | `HumanController` (menús del jugador) e `IAcontroller` (rival) |
| `ui_common.py` | Hoja compartida (solo stdlib): `pause`, `collect_attacks`, `pick_pokemon` |
| `data/` + `data_io/` | JSON de especies, ataques, ítems y tabla de tipos; carga con caché, validación y normalización (`data_io/checks/`) |
| `game/setup_game.py` | Zonas, entrenadores, NPCs, wild markers y jefe de ambos mundos; `_build_pokemon` |
| `game/encounters.py` | `trigger_encounter`, `trigger_wild_encounter`, `trigger_wild_marker_encounter` |
| `game/respawn.py` | `check_respawn`: markers a los `MARKER_RESPAWN_STEPS` pasos, rematches a los `TRAINER_REMATCH_STEPS` |
| `game/difficulty.py` | `DIFFICULTY_PRESETS` y sus getters; estado global de sesión |
| `game/save_load.py` | Guardado y carga (save v2), migración v1→v2 |
| `game/ui_menus.py` | Bolsa (`open_bag_menu`), Pokédex (`open_pokedex`), equipo (`show_team_summary`) |
| `map/` | Mundo 1: overworld (`__init__.py`, `tiles.py`, `renderer.py`), cuevas `dungeon.py` y `dungeon_pn.py`, `terminal.py` (redibujado sin parpadeo) |
| `map/world2/` | Mundo 2: motor propio (`main.py`, `tiles.py`, `renderer.py`) |
| `saves/` | Partidas del jugador (`<nombre>.json`), fuera de git |

`game/world.py` y `map/saves.py` están reservados (sin uso).

## Máquina de estados (`main.py`)

Un `while True` despacha por `(current_world, current_map)`:

- Mundo 1: `main` → `run_map()`, `dungeon` → `run_dungeon()`, `dungeon_pn` → `run_dungeon_pn()`.
- Mundo 2: `world2_main` → `run_world2_map()`.

Cada `run_*()` devuelve un código de transición (`docs/contratos.md` §3). Tras cada retorno que
no sea `"quit"`, `main.py` recarga el save del disco para tomar mapa y posición autoritativos
(`_load_runtime_state`).

## Sistemas de juego

- **Combate.** El jugador puede atacar, usar ítems, cambiar de Pokémon o lanzar Poké Ball (solo
  contra salvajes). Sin PP en ningún ataque se usa Struggle.
- **Estados.** Veneno (1/8 de la vida máxima a fin de ronda), parálisis (velocidad a la mitad y
  25 % de perder el turno) y sueño (1–3 turnos). El Centro Pokémon cura vida, PP y estados.
- **Captura.** Probabilidad `min(0.95, (1 - 0.75 · vida_restante) · multiplicador_de_ball)`;
  equipo máximo de 6.
- **Dificultad.** Se elige al crear partida (`_ask_difficulty`) y se guarda en el save. Solo
  escala el daño que recibe el jugador, la XP y la probabilidad de que la IA use ataques de
  estado:

  | Modo | Daño enemigo | XP | IA usa estado |
  |---|:---:|:---:|:---:|
  | easy | ×0.75 | ×1.25 | 10 % |
  | normal | ×1.00 | ×1.00 | 20 % |
  | hard | ×1.30 | ×0.85 | 45 % |

- **Respawn y rematches.** `check_respawn` se llama en cada paso desde los overworlds de ambos
  mundos (no desde las cuevas). Los rematches suben el equipo al nivel medio del jugador. NPCs
  amistosos y jefes no reaparecen.
- **Progresión.** Vencer al Champion Nexus (cueva `dungeon_pn`) activa `chapter2_unlocked` y
  abre el portal al Mundo 2 (`WORLD2_PORTAL_POS`). Vencer al Echo Guardian activa
  `world2_completed`.
- **Validación de especies.** `_build_pokemon` falla con `UnknownSpeciesError` o
  `SpeciesWithoutAttacksError` (ambas `InvalidSpeciesError`) al construir, no a mitad de combate.
  `restore_player_trainer` es la única excepción: omite con aviso las especies inválidas de saves
  antiguos.
