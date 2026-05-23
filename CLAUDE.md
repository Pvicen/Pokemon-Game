# Pokemon Game — Contexto del Proyecto

## Descripción
Juego de Pokémon por terminal (ASCII) en Python. Combate por turnos, dos mapas (overworld 120×50 + dungeon 60×30), entrenadores NPC, Pokémon salvajes, inventario, guardado/cargado de partidas con nombre.

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
├── main.py                  # Menú principal, state machine de mapas (main/dungeon)
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
│   ├── setup_game.py        # TrainerSetup, WildMarker, Zone + listas TRAINERS/DUNGEON_TRAINERS/ZONES
│   ├── encounters.py        # trigger_encounter(), trigger_wild_encounter(), trigger_wild_marker_encounter()
│   ├── save_load.py         # save_game(), load_game(), restore_player_trainer(), load_defeated_dict()
│   └── ui_menus.py          # open_bag_menu(), open_pokedex()
├── map/
│   ├── tiles.py             # OBSTACLE_GRID, _build_map() — mapa principal 120×50
│   ├── dungeon.py           # DUNGEON_GRID, run_dungeon() — cueva 60×30
│   ├── player.py            # PlayerState (posición, movimiento)
│   ├── renderer.py          # render() — dibuja el mapa principal con colores ANSI por zona
│   ├── events.py            # check_collision()
│   └── __init__.py          # run_map() — loop principal del mapa overworld
└── saves/                   # Partidas guardadas ({nombre}.json)
```

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
| Bug Fix 1 | `trigger_encounter()` retorna `False` si el jugador pierde (trainer no desaparece) | ✅ |
| Bug Fix 2 | Pokéballs agregadas a `reward_pool` de trainers por zona | ✅ |
| F | Pokédex en juego (tecla `P`) — lista todos los Pokémon, marca capturados con ★ | ✅ |
| **D** | **Submapa independiente: Cueva Oscura (60×30, renderer oscuro, entidades propias)** | ✅ |

## Fases pendientes

| Prioridad | Fase | Descripción |
|-----------|------|-------------|
| 1 | **E** | Expandir mapa principal a 160×65 — Ruta del Mar (Pokémon agua) + Pueblo Nuevo (2° Centro Pokémon) |
| 2 | **G** | Evolución por ítems — Fire Stone, Water Stone, etc. (`data/items.json`, `inventory.py`) |
| 3 | **H** | UI/UX — barra HP en selector de cambio, tecla `T` vista rápida del equipo, bolsa por categoría |

### Ideas futuras (post-Fase H)
- Estados de combate: veneno, parálisis, sueño
- PP de ataques (usos limitados)
- Habilidades pasivas por especie
- Rematches de trainers (equipo más fuerte al subir niveles)
- Respawn de wild markers (requiere separar `cleared_wild_markers` del save)
- Pokédex mejorada: guardar nivel de captura por Pokémon (cambiar `pokedex_seen` a `list[dict]`)

## Arquitectura de mapas (Fase D)

`main.py` coordina un `while True` con variable `current_map`:
- `run_map()` → retorna `"enter_dungeon"` | `"quit"`
- `run_dungeon()` → retorna `"exit_dungeon"` | `"quit"`
- Al cambiar de mapa, `main.py` recarga el save para obtener posición y `defeated_dict` autoritativos.

### Transiciones
| Evento | Qué pasa |
|--------|----------|
| Jugador pisa `x≥87, y≥28` en overworld | Guarda con `current_map="dungeon"`, posición `(3,2)`, retorna `"enter_dungeon"` |
| Jugador pisa `▲` en dungeon `(3,1)` | Guarda con `current_map="main"`, posición `(90,26)`, retorna `"exit_dungeon"` |

### Dungeon — layout
60×30 tiles. Viewport 40×20. Posición inicial `(3,2)`, salida `▲` en `(3,1)`.

| Sección | Carve | Entidades |
|---------|-------|-----------|
| Entry room | `(1,1)-(8,4)` | Salida `▲(3,1)`, inicio `(3,2)` |
| Top corridor | `(5,4)-(25,8)` | Geodude `!` (8,5), Ryu `T` (15,8) |
| Vertical connector | `(20,5)-(22,15)` | — |
| Middle section | `(15,10)-(32,15)` | Sara `T` (25,14) |
| Right section | `(30,12)-(45,15)` | Gastly `!` (35,12) |
| Deep vertical | `(38,14)-(42,22)` | Grunt `T` (40,18) |
| Lower corridor | `(18,18)-(42,22)` | Deserter NPC (20,22) |
| Deep chamber | `(38,22)-(52,28)` | Champion `T` (45,26) |

## Zonas del mapa overworld

| Zona | Coordenadas | Dificultad | Encuentro salvaje |
|------|-------------|------------|-------------------|
| Pueblo Raiz | rows 28-48, cols 1-38 | Fácil (Lv 1-5) | 1% |
| Pueblo Alto | rows 1-21, cols 1-38 | Medio-bajo (Lv 5-10) | 1% |
| Bosque Umbral | rows 1-21, cols 44-118 | Medio-alto (Lv 8-14) | 2% |
| Cueva Oscura | rows 28-48, cols 87-118 | Difícil (Lv 12-18) | 3% |
| Cueva (dungeon) | todo `dungeon.py` | Difícil (Lv 12-18) | 3% — usa `zone_id="cueva_oscura"` explícito |

## Centro Pokémon
- Posición: `(9, 11)` — Pueblo Alto
- Cura HP al máximo y revive Pokémon desmayados
- Si todos están al 100% de HP: mensaje "already in perfect health"

## NPCs amistosos (overworld)
| NPC | Posición | Zona |
|-----|----------|------|
| Elder Roy | (20, 38) | Pueblo Raiz |
| Nurse Clara | (35, 22) | Pueblo Alto |
| Lost Traveler | (65, 7) | Bosque Umbral |

> Deserter fue movido al dungeon local `(20,22)` en Fase D.

## Pokémon visibles en mapa (Fase 14)
Marcadores `!`. Al pisarlos → batalla salvaje inmediata. Solo desaparecen si el jugador gana o captura.

### Overworld
| Pokémon | Nivel | Posición | Zona |
|---------|-------|----------|------|
| Meowth | 3 | (15, 32) | Pueblo Raiz |
| Mankey | 4 | (30, 36) | Pueblo Raiz |
| Magnemite | 7 | (12, 8) | Pueblo Alto |
| Horsea | 7 | (25, 14) | Pueblo Alto |
| Bellsprout | 10 | (52, 18) | Bosque Umbral |
| Venonat | 11 | (75, 8) | Bosque Umbral |

### Dungeon (coordenadas locales)
| Pokémon | Nivel | Posición |
|---------|-------|----------|
| Geodude | 13 | (8, 5) |
| Gastly | 14 | (35, 12) |

## Estructura de save (actual)
```json
{
  "slot_name": "mi_partida",
  "current_map": "main",
  "position": {"x": 20, "y": 43},
  "team": [{"name": "Squirtle", "level": 5, "health": 44, "exp": 0}],
  "bag": {"potion": 2, "xdefense": 1, "pokeball": 5},
  "defeated_trainers": {
    "main":   [[10, 44], [28, 43]],
    "dungeon": [[15, 8]]
  },
  "pokedex": ["Squirtle", "Meowth"]
}
```
> Backwards compatible: `load_defeated_dict()` migra saves viejos (lista plana → `{"main": [...], "dungeon": []}`)

## Captura de Pokémon (Fase 13)
- Opción `[4] Throw Pokéball` visible solo en batallas salvajes (`wild=True`)
- Fórmula: `base_rate = 1.0 - (hp_ratio * 0.75)`, `catch_rate = min(0.95, base_rate * mult)`
- La Pokéball se consume **antes** de calcular el éxito
- Equipo máximo: 6 Pokémon
- Pokéballs: `pokeball` (×1.0), `greatball` (×1.5), `ultraball` (×2.0)

## Menú de bolsa fuera de batalla (Feature A)
- Tecla `E` en cualquier punto del mapa (overworld y dungeon)
- **Usar ítem**: solo muestra Pokémon con HP < máximo
- **Revivir**: solo muestra Pokémon desmayados
- **Cambiar Pokémon activo**: no permite seleccionar desmayados

## Pokédex (Fase F)
- Tecla `P` en cualquier punto del mapa (overworld y dungeon)
- Lista todos los Pokémon de `data/pokemons.json` con tipo, nivel base, evolución
- Pokémon del equipo del jugador marcados con ★
- Detalle individual: stats, ataques disponibles

## Keys del juego
- `W/A/S/D` — mover
- `E` — abrir menú de bolsa (usar ítems, cambiar Pokémon activo)
- `P` — abrir Pokédex
- `Q` — guardar y salir

## Starters disponibles
Pikachu, Bulbasaur, Squirtle, Charmeleon — el jugador elige 2 al inicio de partida nueva.

## Ítems disponibles (keys en código)
`potion`, `superpotion`, `maxpotion`, `revive`, `maxrevive`, `xattack`, `xspecialattack`, `xdefense`, `xspecialdefense`, `toughhelmet`, `pokeball`, `greatball`, `ultraball`

## Bugs conocidos / Deuda técnica
- `defeated_trainers.main` mezcla entrenadores y wild markers del overworld — para respawn de wild markers habrá que separar `cleared_wild_markers`.
- El Centro Pokémon cura TODO el equipo. Comportamiento estándar, ajustable si se quiere más dificultad.
