# Pokemon-Game

Juego de Pokémon por terminal (ASCII) en Python. Combate por turnos, overworld 160×65 con 6 zonas, cuevas con entrenadores NPC, Pokémon salvajes, inventario, Pokédex y guardado por slots.

## Estado actual

**Fase P completada** — Capítulo 1 completo. Incluye cueva end-game en Pueblo Nuevo con Champion Nexus, cinemática post-victoria y `chapter2_unlocked` en el save.

Siguiente paso: **Fase Q — Capítulo 2 / Mundo Nuevo** (pendiente).

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

1–14, A–P: combate, mapa ASCII, cuevas, Pokédex, PP, estados alterados, habilidades pasivas, respawn, rematches, cueva end-game.

Ver [AGENTS.md](AGENTS.md) para el detalle completo de arquitectura, fases y roadmap.
