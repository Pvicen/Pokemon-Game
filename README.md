# Pokemon-Game

Juego de Pokémon por terminal (ASCII) en Python. Combate por turnos, overworld 160×65 con 6 zonas, cuevas con entrenadores NPC, Pokémon salvajes, inventario, Pokédex y guardado por slots.

## Estado actual

**Capítulo 2 completo (Fase Q).** El juego tiene dos mundos: el overworld original (160×65) y el Mundo 2 (120×50), accesible por un portal en Pueblo Nuevo tras derrotar al Champion Nexus. Incluye save multi-mundo v2, 5 zonas nuevas, NPCs narrativos, 8 entrenadores, encuentros salvajes, rematches y el jefe final **Echo Guardian**.

**Pulido (Paquetes 1–2):** renderizado anti-flicker y **selección de dificultad** (Fácil / Normal / Difícil) al crear partida. En Difícil los enemigos pegan más fuerte, dan menos XP y la IA usa ataques de estado (Thunder Wave, Toxic, Sleep Powder); el daño que infliges tú nunca se penaliza.

No hay fases pendientes planificadas. Ver [AGENTS.md](AGENTS.md) y [CLAUDE.md](CLAUDE.md) para detalle y posibles líneas futuras.

## Cómo ejecutar

### Opción A — Con instalación editable (recomendada)

```powershell
# Desde la raíz del proyecto
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
python -m Pokemon_Game
```

### Opción B — Sin instalar, desde el directorio padre

```powershell
# Subir un nivel por encima de la carpeta Pokemon-Game
cd "c:\Users\Usuario\OneDrive\Documentos"
python -m Pokemon-Game
```

> **Nota**: el guion en el nombre de la carpeta puede causar problemas con la importación del módulo en algunos entornos. La Opción A (`pip install -e .`) es la más robusta.

## Dependencias

```
readchar>=2.0.0
```

Instalar con: `pip install -r requirements.txt`

## Controles

| Tecla | Acción |
|-------|--------|
| W/A/S/D | Mover |
| E | Bolsa |
| P | Pokédex |
| T | Ver equipo |
| Q | Guardar y salir |

## Fases completadas

1–14, A–P (Capítulo 1), Q1–Q4 (Capítulo 2) y Paquetes 1–2 (pulido): combate, mapa ASCII, cuevas, Pokédex, PP, estados alterados, habilidades pasivas, respawn, rematches, cueva end-game, arquitectura multi-mundo, Mundo 2 con jefe final, renderizado anti-flicker y sistema de dificultad con IA táctica.

Ver [AGENTS.md](AGENTS.md) y [CLAUDE.md](CLAUDE.md) para el detalle completo de arquitectura, fases y save format.
