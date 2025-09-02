# Pokemon/__init__.py

"""
Top-level public API for the Pokemon package.
Expose stable entry-points so consumers don't depend on internal structure.
"""

# (Optional) Semantic version (kept here or in a separate _version.py)
__version__ = "0.1.0"

# 1) Data I/O: loaders, errors, validators (from subpackage facade)
from .data_io import (
    load_pokemons_json,
    load_items,
    load_attacks_json,
    load_type_chart,
    DataValidationError,
    MalformedJSONError,
    FileNotFoundInDataDir,
    # validators (if you want them public at top-level)
    validate_pokemon_schema,
    validate_attacks_schema,
    validate_items_schema,
    validate_type_chart_schema,
)

# 2) Core domain models (adjust names to your actual classes)
# If you keep Trainer in trainers.py, import from there instead of models.py
try:
    from .models import Pokemon, Evolution  # change to your real class names
except Exception:
    # Keep import resilient during partial builds/refactors
    pass

try:
    from .trainers import Trainer  # if you have a Trainer class here
except Exception:
    pass

# 3) Battle/combat entry-points
try:
    from .combat import pokemon_combat  # adjust to your main function/class
except Exception:
    pass

__all__ = [
    # Version
    "__version__",
    # Loaders
    "load_pokemons_json",
    "load_items",
    "load_attacks_json",
    "load_type_chart",
    # Errors
    "DataValidationError",
    "MalformedJSONError",
    "FileNotFoundInDataDir",
    # Validators (if you want them at top-level)
    "validate_pokemon_schema",
    "validate_attacks_schema",
    "validate_items_schema",
    "validate_type_chart_schema",
    # Models (adjust if names differ)
    "Pokemon",
    "Evolution",
    "Trainer",
    # Battle API
    "pokemon_combat",
]