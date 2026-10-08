# Deuda técnica — Pokemon-Game

Registro del método C.C.D. (`AGENTS.md`, «Gestión de deuda técnica»): todo error **medio o bajo**
que aparece construyendo una Caja se anota aquí con su explicación y se ignora temporalmente. Lo
**Bloqueante** o **Alto** no va aquí: detiene el avance hasta resolverse.

| Fecha | Caja / zona | Qué pasa | Por qué se difiere | Estado |
|---|---|---|---|---|
| 2026-06-02 | Orquestación (`main.py`) | `defeated_dict` se recarga del disco en cada cambio de mapa; `cleared_markers_dict` ya va por referencia en RAM | Solo es I/O redundante | abierta |
| 2026-06-02 | Mapa (`dungeon.py`, `dungeon_pn.py`) | Las cuevas no llaman a `check_respawn`: sus markers y entrenadores no reaparecen | No rompe nada; es contenido | abierta |
| 2026-06-02 | Combate (`controllers/ia.py`) | La IA solo usa ataques de estado puros (daño 0) por probabilidad; no puntúa los de daño+estado ni cambia de Pokémon | Mejora de juego, no fallo | abierta |
| 2026-06-02 | Combate (`abilities.py`) | Static se activa con cualquier ataque; debería exigir contacto (falta ese campo en `attacks.json`) | Caso de borde | abierta |
| 2026-06-02 | Combate (`experience.py`) | `_apply_species` no actualiza `evolution_by_item` tras evolucionar por nivel; además debería vivir en `models.py` (TODO en `inventory.py`) | Hoy ninguna especie tiene ambas evoluciones | abierta |
| 2026-09-27 | Orquestación (`main.py`) | `_main_menu()` se llama a sí misma ante cada opción inválida o tras borrar una partida | Solo fallaría tras cientos de entradas inválidas seguidas | abierta |
| 2026-09-27 | Empaquetado | `pip install -e .` no instala el juego como `Pokemon_Game` (`setup.cfg` busca subpaquetes, no la raíz) | `jugar.py` lo sustituye | abierta |
| 2026-09-27 | Datos | 35 de las 67 especies no tienen ataques en `attacks.json` y no se pueden usar | Es ampliación de contenido | abierta |

## Líneas futuras (sin planificar; decide Vicente)

- Capítulo 3 (`world3`), según `docs/contratos.md` §3.
- Menú dentro de la partida para cambiar la dificultad.
