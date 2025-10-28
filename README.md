# Pokemon-Game (local)

Quick start (PowerShell):

1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies and the project in editable mode

```powershell
pip install -r requirements.txt
pip install -e .
```

3. Run the game (module mode) from the project root

```powershell
python -m Pokemon-Game.main
```

Notes:
- The package uses relative imports expecting to be executed as a package. Running `main.py` directly may fail because of relative imports; use `python -m` or install editable (`pip install -e .`).
- If you prefer not to install, run via `PYTHONPATH`:

```powershell
$env:PYTHONPATH = $PWD
python -c "from main import main; main()"
```
