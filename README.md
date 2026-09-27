# Pokemon-Game

Juego de Pokémon por terminal (ASCII) en Python. Combate por turnos con PP, estados alterados y
habilidades; dos mundos explorables con cuevas, entrenadores, Pokémon salvajes, rematches,
Pokédex, tres dificultades y partidas guardadas por nombre.

## Cómo jugar

Requiere Python 3 (probado con 3.13) y [uv](https://docs.astral.sh/uv/). Desde la raíz del repo:

```powershell
uv venv .venv
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
.venv\Scripts\python.exe jugar.py
```

`jugar.py` arranca el juego sin importar cómo se llame la carpeta. Las partidas se guardan en
`saves/` (fuera de git).

## Controles

| Tecla | Acción |
|-------|--------|
| W/A/S/D | Mover |
| E | Bolsa |
| P | Pokédex |
| T | Ver equipo |
| Q | Guardar y salir |

## Progresión

1. **Mundo 1**: overworld con seis zonas, dos Centros Pokémon y dos cuevas. En la cueva final,
   junto a Pueblo Nuevo, espera el Champion Nexus.
2. Vencerlo abre el **portal al Mundo 2** en Pueblo Nuevo: cinco zonas nuevas, NPCs narrativos,
   ocho entrenadores y el jefe final, **Echo Guardian**.

## Para desarrollar

Reglas y método de trabajo en [AGENTS.md](AGENTS.md); arquitectura y contratos en
[docs/](docs/); errores conocidos y líneas futuras en [DEUDA_TECNICA.md](DEUDA_TECNICA.md).
