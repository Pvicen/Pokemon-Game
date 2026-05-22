# Pokemon Game — Contexto del Proyecto

## Descripción
Juego de Pokémon por terminal (ASCII, 120×50 tiles) en Python. Combate por turnos, mapa explorable, entrenadores NPC, Pokémon salvajes, inventario, guardado/cargado de partidas con nombre.

## Cómo ejecutar
```
python -m Pokemon-Game
```
Desde el directorio padre de la carpeta `Pokemon-Game/`.

## Reglas de trabajo (OBLIGATORIAS)
- NO reescribir el proyecto desde cero
- NO modificar archivos sin explicar el plan primero
- Trabajar en pasos pequeños, código modular
- NO mezclar lógica en `main.py`
- Todo el código en inglés; comunicación con el usuario en **español**
- Entrenadores, Pokémon salvajes y spawns van en `game/` — NUNCA en `map/`
- `map/` solo maneja: terreno, render, movimiento del jugador, viewport, colisiones

## Arquitectura

```
Pokemon-Game/
├── main.py                  # Menú principal, selección de save, arranca run_map()
├── combat.py                # Motor de combate por turnos
├── models.py                # Clase Pokemon, EvolvedPokemon
├── trainers.py              # Clase Trainer
├── inventory.py             # Clase Inventory (ítems, efectos)
├── damage.py                # Cálculo de daño y efectividad
├── experience.py            # ExperienceManager (XP, level-up, evolución)
├── data/
│   ├── pokemons.json        # Stats base de cada Pokémon
│   ├── attacks.json         # Ataques por propietario
│   └── items.json           # Definiciones de ítems
├── controllers/
│   ├── human.py             # HumanController (input del jugador)
│   └── ia.py                # IAcontroller (IA enemiga)
├── game/
│   ├── setup_game.py        # TrainerSetup, Zone, TRAINERS, ZONES, choose_starter()
│   ├── encounters.py        # trigger_encounter(), trigger_wild_encounter()
│   └── save_load.py         # save_game(), load_game(), restore_player_trainer()
├── map/
│   ├── tiles.py             # OBSTACLE_GRID, _build_map(), POKEMON_CENTER_POS implícito
│   ├── player.py            # PlayerState (posición, movimiento)
│   ├── renderer.py          # render() — dibuja el mapa en terminal
│   ├── events.py            # check_collision()
│   └── __init__.py          # run_map() — loop principal del mapa
└── saves/                   # Partidas guardadas ({nombre}.json)
```

## Estado actual — Fases completadas

| Fase | Estado |
|------|--------|
| 1–8 | ✅ Base: modelos, combate, IA, daño, XP, inventario, mapa |
| 9A | ✅ Saves con nombre (múltiples slots, `saves/`) |
| 9B | ✅ Selección de 2 starters con stats/ataques |
| 10 | ✅ Inventario jugador (2 Potions + 1 X-Defense; guarda/carga) |
| 11A | ✅ Diálogo de entrenadores antes de batalla |
| 11B | ✅ Recompensas aleatorias al ganar (reward_pool) |
| 11C | ✅ NPCs amistosos (diálogo + regalo, sin batalla) |
| 11.5 | ✅ Reward pools ponderados por zona para NPCs amistosos |
| 11.5 | ✅ Probabilidades de encuentros salvajes reducidas (1–3%) |
| 12 | ✅ Centro Pokémon real (x=9, y=11 en Pueblo Alto). Sin auto-heal. |

## Zonas del mapa

| Zona | Coordenadas | Dificultad | Encuentro salvaje |
|------|-------------|------------|-------------------|
| Pueblo Raiz | rows 28-48, cols 1-38 | Fácil (Lv 1-5) | 1% |
| Pueblo Alto | rows 1-21, cols 1-38 | Medio-bajo (Lv 5-10) | 1% |
| Bosque Umbral | rows 1-21, cols 44-118 | Medio-alto (Lv 8-14) | 2% |
| Cueva Oscura | rows 28-48, cols 87-118 | Difícil (Lv 12-18) | 3% |

## Centro Pokémon
- Posición: `(9, 11)` — puerta del edificio en Pueblo Alto
- Solo cura si algún Pokémon está dañado o desmayado
- Si todos están al 100%: mensaje "already in perfect health"

## NPCs amistosos (sin batalla)
| NPC | Posición | Zona |
|-----|----------|------|
| Elder Roy | (20, 38) | Pueblo Raiz |
| Nurse Clara | (35, 22) | Pueblo Alto |
| Lost Traveler | (65, 7) | Bosque Umbral |
| Deserter | (95, 44) | Cueva Oscura |

Todos usan `is_friendly=True` y `reward_pool` ponderado (mejor loot en zonas más difíciles).

## Starters disponibles
Pikachu, Bulbasaur, Squirtle, Charmeleon — el jugador elige 2 al inicio de partida nueva.

## Keys del juego
- `W/A/S/D` — mover
- `Q` — guardar y salir

## Pendiente (próximas fases)

### Fase 13 — Captura de Pokémon salvajes
- Opción `[4] Throw Pokéball` en combate salvaje
- Fórmula de captura basada en HP restante
- Pokémon capturado se añade al equipo

### Fase 14 — Pokémon visibles en mapa
- Marcadores ASCII en posiciones fijas por zona
- Al pisar → batalla (reemplaza parte del encuentro random)

### Feature A — Menú de inventario fuera de batalla (tecla E)
- Usar pociones en cualquier Pokémon del equipo (selector)
- Revivir cualquier Pokémon desmayado (selector)
- Cambiar Pokémon activo (active_index)

### Feature B — Mejora ítems en batalla
- Al usar Revive → selector de qué Pokémon desmayado revivir
- Actualmente solo afecta al Pokémon activo (bug conocido)

## Bugs conocidos
- `restore_player_trainer` tenía `max(1, saved_hp)` → Pokémon desmayados cargaban con 1 HP. **Ya corregido** a `max(0, saved_hp)`.
- En batalla, Revive/Potion siempre va al Pokémon activo. Fix pendiente en Feature B.

## Ítems disponibles (keys en código)
`potion`, `superpotion`, `maxpotion`, `revive`, `maxrevive`, `xattack`, `xspecialattack`, `xdefense`, `xspecialdefense`, `toughhelmet`

## Estructura de save
```json
{
  "slot_name": "mi_partida",
  "position": {"x": 20, "y": 43},
  "team": [{"name": "Squirtle", "level": 5, "health": 44, "exp": 0}],
  "bag": {"potion": 2, "xdefense": 1},
  "defeated_trainers": [[10, 44], [28, 43]]
}
```
