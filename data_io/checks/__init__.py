"""
Public API for data_io.checks subpackage.
Re-exports schema validators so callers don't import individual files.
"""

# Import explicitly from sibling modules (fine-grained control)
from .pokemons import validate_pokemons
from .attacks import validate_attacks
from .items import validate_items
from .type_effectiveness import validate_type_chart

# Optional: you can expose additional utilities if you have them:
# from .pokemon import normalize_pokemon_entry

# Define the explicit public surface for "from data_io.checks import *"
__all__ = [
    "validate_pokemons",
    "validate_attacks",
    "validate_items",
    "validate_type_chart",
    # "normalize_pokemon_entry",
]