"""Lanzador: arranca el juego desde la carpeta del repo, se llame como se llame.

El código usa imports relativos y espera importarse como paquete `Pokemon_Game`;
aquí se registra la raíz del repo con ese nombre y se llama a `main()`.

Uso:  .venv\\Scripts\\python.exe jugar.py
"""
import importlib.util
import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "Pokemon_Game", raiz / "__init__.py", submodule_search_locations=[str(raiz)]
)
paquete = importlib.util.module_from_spec(spec)
sys.modules["Pokemon_Game"] = paquete
spec.loader.exec_module(paquete)

from Pokemon_Game.main import main  # noqa: E402

main()
