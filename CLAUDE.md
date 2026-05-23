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
- **Workflow obligatorio**: explicar problema → listar archivos → cambios exactos → esperar aprobación → editar → explicar cómo probar

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
│   └── items.json           # Definiciones de ítems (incluye pokeball/greatball/ultraball)
├── controllers/
│   ├── human.py             # HumanController (input del jugador)
│   └── ia.py                # IAcontroller (IA enemiga)
├── game/
│   ├── setup_game.py        # TrainerSetup, WildMarker, Zone, TRAINERS, WILD_MARKERS, ZONES
│   ├── encounters.py        # trigger_encounter(), trigger_wild_encounter(), trigger_wild_marker_encounter()
│   ├── save_load.py         # save_game(), load_game(), restore_player_trainer()
│   └── ui_menus.py          # open_bag_menu() — menú de bolsa fuera de batalla (tecla E)
├── map/
│   ├── tiles.py             # OBSTACLE_GRID, _build_map()
│   ├── player.py            # PlayerState (posición, movimiento)
│   ├── renderer.py          # render() — dibuja el mapa (T=entrenador, !=Pokémon salvaje)
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
| 13 | ✅ Captura de Pokémon salvajes (Pokéballs, fórmula HP, equipo max 6) |
| Feature A | ✅ Menú de bolsa fuera de batalla (tecla E) |
| Feature B | ✅ Selector de Pokémon objetivo al usar ítems en batalla |
| 14 | ✅ Pokémon visibles en el mapa como marcadores `!` |

## Zonas del mapa

| Zona | Coordenadas | Dificultad | Encuentro salvaje |
|------|-------------|------------|-------------------|
| Pueblo Raiz | rows 28-48, cols 1-38 | Fácil (Lv 1-5) | 1% |
| Pueblo Alto | rows 1-21, cols 1-38 | Medio-bajo (Lv 5-10) | 1% |
| Bosque Umbral | rows 1-21, cols 44-118 | Medio-alto (Lv 8-14) | 2% |
| Cueva Oscura | rows 28-48, cols 87-118 | Difícil (Lv 12-18) | 3% |

## Centro Pokémon
- Posición: `(9, 11)` — puerta del edificio en Pueblo Alto
- Cura HP al máximo Y revive Pokémon desmayados (comportamiento estándar de los juegos)
- Si todos están al 100% de HP: mensaje "already in perfect health"

## NPCs amistosos (sin batalla)
| NPC | Posición | Zona |
|-----|----------|------|
| Elder Roy | (20, 38) | Pueblo Raiz |
| Nurse Clara | (35, 22) | Pueblo Alto |
| Lost Traveler | (65, 7) | Bosque Umbral |
| Deserter | (95, 44) | Cueva Oscura |

Todos usan `is_friendly=True` y `reward_pool` ponderado (mejor loot en zonas más difíciles).

## Pokémon visibles en mapa (Fase 14)
Marcadores `!` en posiciones fijas. Al pisarlos → batalla salvaje inmediata.
- Solo desaparecen si el jugador **gana o captura** el Pokémon.
- Si huye o pierde, el marcador permanece en el mapa.
- Las posiciones derrotadas se guardan en `defeated_trainers` del save (misma lista que entrenadores — deuda técnica anotada: si en el futuro se quiere respawn de wild markers, habrá que separar en `cleared_wild_markers`).

| Pokémon | Nivel | Posición | Zona |
|---------|-------|----------|------|
| Meowth | 3 | (15, 32) | Pueblo Raiz |
| Mankey | 4 | (30, 36) | Pueblo Raiz |
| Magnemite | 7 | (12, 8) | Pueblo Alto |
| Horsea | 7 | (25, 14) | Pueblo Alto |
| Bellsprout | 10 | (52, 18) | Bosque Umbral |
| Venonat | 11 | (75, 8) | Bosque Umbral |
| Geodude | 13 | (91, 27) | Cueva Oscura |
| Gastly | 14 | (105, 34) | Cueva Oscura |

## Captura de Pokémon (Fase 13)
- Opción `[4] Throw Pokéball` visible solo en batallas salvajes (`is_wild=True`)
- Fórmula: `base_rate = 1.0 - (hp_ratio * 0.75)`, `catch_rate = min(0.95, base_rate * catch_rate_mult)`
- La Pokéball se consume **antes** de calcular el éxito (si falla, igual se gasta)
- Equipo máximo: 6 Pokémon (no se puede capturar si el equipo está lleno)
- Pokéballs disponibles: `pokeball` (×1.0), `greatball` (×1.5), `ultraball` (×2.0)

## Menú de bolsa fuera de batalla (Feature A)
- Tecla `E` en cualquier punto del mapa
- Lógica en `game/ui_menus.py` — `map/__init__.py` solo llama `open_bag_menu(player_trainer)`
- **Usar ítem**: solo muestra Pokémon con HP < máximo (evita gastar pociones en vano)
- **Revivir**: solo muestra Pokémon desmayados
- **Cambiar Pokémon activo**: no permite seleccionar desmayados

## Ítems en batalla (Feature B)
- Al usar Revive → selector de Pokémon desmayado (`HumanController._pick_fainted`)
- Al usar Poción → `target_index` pasado a `Inventory.use()`, funciona con cualquier tipo de ítem
- `usable_items(in_battle=False)` excluye ítems `battle_only` (X-Attack, X-Defense) y ítems de captura

## Starters disponibles
Pikachu, Bulbasaur, Squirtle, Charmeleon — el jugador elige 2 al inicio de partida nueva.

## Keys del juego
- `W/A/S/D` — mover
- `E` — abrir menú de bolsa (usar ítems, cambiar Pokémon activo)
- `Q` — guardar y salir

## Ítems disponibles (keys en código)
`potion`, `superpotion`, `maxpotion`, `revive`, `maxrevive`, `xattack`, `xspecialattack`, `xdefense`, `xspecialdefense`, `toughhelmet`, `pokeball`, `greatball`, `ultraball`

## Estructura de save
```json
{
  "slot_name": "mi_partida",
  "position": {"x": 20, "y": 43},
  "team": [{"name": "Squirtle", "level": 5, "health": 44, "exp": 0}],
  "bag": {"potion": 2, "xdefense": 1, "pokeball": 5},
  "defeated_trainers": [[10, 44], [28, 43]]
}
```
> Nota: `defeated_trainers` almacena tanto posiciones de entrenadores derrotados como marcadores `!` de Pokémon salvajes eliminados.

## Bugs conocidos / Deuda técnica
- `defeated_trainers` en el save mezcla entrenadores y wild markers — si en el futuro se quiere respawn de wild markers, separar en `cleared_wild_markers`.
- El Centro Pokémon cura TODO el equipo (HP + revive desmayados). Es comportamiento estándar de Pokémon, pero podría ajustarse si se quiere más dificultad.

## Pendiente (próximas ideas)
- **Estados de combate**: veneno, parálisis, sueño — daría más profundidad táctica
- **Más ítems**: antídoto, despertar, etc. (lógico si se añaden estados)
- **Respawn de wild markers**: separar `cleared_wild_markers` en el save para poder hacer que los Pokémon visibles reaparezcan
- **Mostrar equipo rápido**: tecla `T` para ver HP/nivel del equipo sin abrir la bolsa
