# Pokemon-Game — Reglas del proyecto

Juego de Pokémon por terminal (ASCII) en Python: combate por turnos, dos mundos explorables,
entrenadores, salvajes, Pokédex y partidas guardadas por nombre. Estas reglas complementan (y en
conflicto, prevalecen sobre) el `AGENTS.md` general de `C:\Dev`. Vicente decide; la IA ejecuta la
Caja que él manda.

## Método C.C.D. y escalada de modelos

**C**ajas, **C**ontratos y **D**euda Técnica. Documento maestro de Vicente (2026-09-25), piedra
angular de todo repo bajo `C:\Dev`; se reproduce igual en cada `AGENTS.md`. La IA solo ejecuta lo
que Vicente manda por Cajas.

### 1. Ley primera: avance sobre perfección
El objetivo del desarrollador y las IAs es alcanzar el Producto Mínimo Viable (MVP). Si el «Camino
Feliz» funciona y no hay riesgos graves, se aprueba y se avanza.
* **Prohibido:** los bucles de refutación. La IA no decide si el código está perfecto; el
  desarrollador (Arquitecto) es el árbitro final.

### 2. Arquitectura por Cajas y Contratos
* **Las Cajas:** todo se programa de forma aislada (Caja Red, Caja BD, Caja Interfaz).
* **Aislamiento de contexto:** al programar una Caja, NUNCA se pasa a la IA el código de las demás
  Cajas.
* **Los Contratos:** el único puente entre Cajas es el Contrato (el formato exacto de los datos que
  entran y salen, p. ej. un JSON). A la IA solo se le pasa este Contrato como contexto para que
  programe la Caja correspondiente.

### 3. Gestión de deuda técnica
* **Errores medios/bajos:** optimizaciones, estética o casos de borde improbables NO se arreglan en
  la fase de construcción.
* **Archivo `DEUDA_TECNICA.md`:** cada proyecto tiene este archivo en su raíz. Todo error no crítico
  se anota aquí con su explicación y se ignora temporalmente.
* Solo se detiene el avance ante errores **Bloqueantes** (crasheos absolutos) o **Altos** (brechas
  de seguridad, pérdida de datos).

### 4. La regla de los subagentes (solo exploración)
* **Prohibido:** usar subagentes para debatir, buscar bugs o criticar código ya escrito.
* **Uso permitido:** «Exploradores de Contratos». Antes de programar se pueden lanzar un número
  estricto y limitado de subagentes (2 o 3) SOLO para leer Cajas distintas y proponer el Contrato
  que las va a unir. Una vez hecho el molde, los subagentes desaparecen.

### 5. Matriz de escalada de modelos (uso eficiente de tokens)
* **Nivel 1 — El día a día (Opus 5.5, modo estándar):** el 90 % del trabajo. Hacer moldes,
  programar Cajas individuales a partir de Contratos, lanzar subagentes de exploración. Consumo
  eficiente.
* **Nivel 2 — El refactorizador menor (Fable 5.1, modo estándar):** cuando hay un cambio de rumbo
  arquitectónico y hay que reescribir varios archivos para que sigan una nueva lógica. Mantiene
  excelente coherencia narrativa.
* **Nivel 3 — El botón nuclear algorítmico (Opus 5.5, UltraCode):** uso quirúrgico y
  ultra-restringido. Solo para crear desde cero cuellos de botella lógicos o matemáticos muy
  complejos (p. ej. el motor del Análisis Financiero). Se usa, se copia el código y se vuelve al
  Nivel 1.
* **Nivel 4 — El mega-refactor / cataclismo (Fable 5.1, UltraCode):** solo en migraciones masivas
  de tecnología o cambios estructurales que reescriben la mayoría del proyecto manteniendo lógica
  compleja de fondo.
* **Nivel 5 — El Tribunal Supremo / auditor final (GPT-6 Astra Ultra):** la última fase de la
  inteligencia. Cero programación. Misiones exclusivas: (1) **Auditoría final:** al terminar una
  Caja crítica se le pasa el código a GPT para buscar ÚNICAMENTE vulnerabilidades Altas o
  Bloqueantes; si está limpio, responde «CAJA APROBADA». (2) **El Solucionador (fallback):** si los
  modelos anteriores fracasan resolviendo un crasheo grave, se le pasa el problema a Astra para que
  diagnostique y repare.

## Cajas de este repo

| Caja | Ficheros | Contrato que la une al resto |
|---|---|---|
| Datos | `data/`, `data_io/` | Esquemas JSON — `docs/contratos.md` §1 |
| Combate | `combat.py`, `damage.py`, `models.py`, `abilities.py`, `experience.py`, `inventory.py`, `trainers.py`, `utils.py`, `controllers/` | Objetos `Pokemon`/`Trainer` construidos por la Caja Juego |
| Mapa | `map/` (un motor por mundo: `map/` = Mundo 1, `map/world2/` = Mundo 2) | Códigos de retorno de `run_*()` — `docs/contratos.md` §3 |
| Juego | `game/` salvo `save_load.py` | Entidades y zonas de `game/setup_game.py` |
| Guardado | `game/save_load.py` | Save v2 — `docs/contratos.md` §2 |
| Orquestación | `main.py` | Solo la máquina de estados; despacha por `(current_world, current_map)` |

`ui_common.py` es una hoja compartida (solo stdlib) y la usan todas las Cajas.

## Qué no hacer

- **No romper partidas guardadas.** Campo nuevo en el save = valor por defecto en `save_game()`
  y tolerancia a su ausencia al cargar. Las listas `[x, y, step]` siguen aceptando `[x, y]`.
  Nunca escribir un save sin el `current_world` correcto (el guardado hace merge con el disco).
- **No meter entrenadores, spawns ni wild markers en `map/`.** Van en `game/setup_game.py`;
  `map/` solo pinta, mueve y detecta transiciones.
- **No engordar `main.py`**: ahí solo vive la máquina de estados.
- **No usar especies sin ataques** en equipos, markers ni zonas: `_build_pokemon()` lanza
  `UnknownSpeciesError` / `SpeciesWithoutAttacksError` a propósito. Solo 32 de las 67 especies de
  `data/pokemons.json` tienen ataques en `data/attacks.json`.
- **No tocar `map/renderer.py` para otro mundo**: cada mundo tiene su motor en `map/worldN/`.
- **No importar nada del proyecto desde `ui_common.py`** (reabriría el ciclo `combat↔map`).
- **No subir `saves/`** (partidas del jugador) ni añadir dependencias de runtime aparte de
  `readchar` sin que Vicente lo apruebe.
- Identificadores y textos del juego en **inglés**; docs, commits y conversación en español.

## Dónde mirar

- `docs/arquitectura.md` — mapa de módulos, máquina de estados y sistemas de juego.
- `docs/contratos.md` — formato de datos, save v2 y transiciones entre mapas.
- `DEUDA_TECNICA.md` — errores no críticos anotados y líneas futuras.
- `README.md` — cómo jugar.

## Ejecutar y verificar

Entorno: `.venv` en la raíz (Python 3.13, `uv venv .venv` + `uv pip install -r requirements.txt`).
Jugar: `.venv\Scripts\python.exe jugar.py` (el lanzador registra la raíz como paquete
`Pokemon_Game`; sin él, los imports relativos exigen que la carpeta se llame así).

No hay tests automáticos. Gate mínimo antes de commitear:

```powershell
.venv\Scripts\python.exe -m compileall -q -x "\.venv" .
```

y arrancar `jugar.py` hasta el menú principal. Lo que toque combate, mapa o guardado se prueba
jugando el camino feliz con una partida de `saves/`.
