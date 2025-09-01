from .errors import DataPathError, DataValidationError, DataIOError
from .paths import data_dir
from .loaders import load_dataset

from .checks.attacks import validate_attacks, normalize_attacks
from .checks.pokemons import validate_pokemons, normalize_pokemons
from .checks.items import validate_items, normalize_items
from .checks.type_effectiveness import validate_type_chart, normalize_type_chart  # (cuando lo agregues)

def load_attacks() -> dict:
    return load_dataset(
        "attacks.json",
        validator=validate_attacks,
        normalizer=normalize_attacks,
        use_cache=True,
    )
    
    
def load_pokemons() -> dict:
    return load_dataset(
        "pokemons.json",
        validator=validate_pokemons,
        normalizer=normalize_pokemons,
        use_cache=True,
    )


def load_items() -> dict:
    return load_dataset(
        "items.json",
        validator=validate_items,
        normalizer=normalize_items,
        use_cache=True)

def load_type_chart() -> dict:
    return load_dataset(
        "type_effectiveness.json",
        validator=validate_type_chart,
        normalizer=normalize_type_chart,
        use_cache=True,
    )
    

def load_all_data() -> dict:
    return {
        "attacks": load_attacks(),
        "pokemons": load_pokemons(),
        "items": load_items(),
        "type_chart": load_type_chart(),
    }