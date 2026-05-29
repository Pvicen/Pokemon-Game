from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from ..models import Pokemon
from ..trainers import Trainer
from ..inventory import Inventory
from ..abilities import ABILITY_BY_SPECIES


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class WildMarker:
    name: str
    level: int
    position: Tuple[int, int]


@dataclass
class WildPokemonEntry:
    name: str
    min_level: int = 1
    max_level: int = 5
    spawn_chance: float = 1.0


@dataclass
class Zone:
    id: str
    name: str
    description: str
    min_player_level: int = 1
    wild_pokemons: List[WildPokemonEntry] = field(default_factory=list)
    wild_encounter_chance: float = 0.15
    trainer_count: int = 3


@dataclass
class TrainerSetup:
    name: str
    team: List[Tuple[str, int]]   # [(pokemon_name, level), ...]
    position: Tuple[int, int]     # (x, y) on the map
    defeat_message: str = "You won!"
    dialogue: List[str] = field(default_factory=list)
    reward_pool: list = field(default_factory=list)  # List[Dict] o List[Tuple[Dict, int]] (ponderado)
    is_friendly: bool = False


# =============================================================================
# WORLD ZONES
# =============================================================================

ZONES: Dict[str, Zone] = {
    "pueblo_raiz": Zone(
        id="pueblo_raiz",
        name="Pueblo Raiz",
        description="The starting town. Beginner trainers.",
        min_player_level=1,
        wild_pokemons=[
            WildPokemonEntry(name="Mankey",   min_level=1, max_level=5, spawn_chance=2.0),
            WildPokemonEntry(name="Oddish",   min_level=1, max_level=5, spawn_chance=2.0),
            WildPokemonEntry(name="Zubat",    min_level=1, max_level=5, spawn_chance=2.0),
        ],
        wild_encounter_chance=0.01,
        trainer_count=3,
    ),
    "pueblo_alto": Zone(
        id="pueblo_alto",
        name="Pueblo Alto",
        description="Second town and routes. Intermediate trainers.",
        min_player_level=5,
        wild_pokemons=[
            WildPokemonEntry(name="Abra",     min_level=5, max_level=10, spawn_chance=2.0),
            WildPokemonEntry(name="Magnemite", min_level=5, max_level=10, spawn_chance=2.0),
            WildPokemonEntry(name="Horsea",   min_level=5, max_level=10, spawn_chance=2.0),
        ],
        wild_encounter_chance=0.01,
        trainer_count=4,
    ),
    "bosque_umbral": Zone(
        id="bosque_umbral",
        name="Bosque Umbral",
        description="Dense forest with tricky paths. Medium difficulty.",
        min_player_level=8,
        wild_pokemons=[
            WildPokemonEntry(name="Venonat",   min_level=8, max_level=14, spawn_chance=2.5),
            WildPokemonEntry(name="Bellsprout", min_level=8, max_level=14, spawn_chance=2.0),
            WildPokemonEntry(name="Ekans",     min_level=8, max_level=14, spawn_chance=2.0),
        ],
        wild_encounter_chance=0.02,
        trainer_count=3,
    ),
    "cueva_oscura": Zone(
        id="cueva_oscura",
        name="Cueva Oscura",
        description="Dark cave with strong trainers. High difficulty.",
        min_player_level=12,
        wild_pokemons=[
            WildPokemonEntry(name="Geodude",  min_level=12, max_level=18, spawn_chance=2.5),
            WildPokemonEntry(name="Gastly",   min_level=12, max_level=18, spawn_chance=2.0),
            WildPokemonEntry(name="Zubat",    min_level=12, max_level=18, spawn_chance=2.0),
        ],
        wild_encounter_chance=0.03,
        trainer_count=4,
    ),
    "ruta_del_mar": Zone(
        id="ruta_del_mar",
        name="Ruta del Mar",
        description="A coastal water route with aquatic Pokémon.",
        min_player_level=12,
        wild_pokemons=[
            WildPokemonEntry(name="Staryu",    min_level=12, max_level=18, spawn_chance=2.5),
            WildPokemonEntry(name="Tentacool", min_level=12, max_level=18, spawn_chance=2.0),
            WildPokemonEntry(name="Horsea",    min_level=12, max_level=18, spawn_chance=2.0),
        ],
        wild_encounter_chance=0.02,
        trainer_count=2,
    ),
    "pueblo_nuevo": Zone(
        id="pueblo_nuevo",
        name="Pueblo Nuevo",
        description="A new town on the eastern coast. Has a Pokemon Center.",
        min_player_level=12,
        wild_pokemons=[],
        wild_encounter_chance=0.0,
        trainer_count=2,
    ),
}

ZONE_ORDER: List[str] = ["pueblo_raiz", "pueblo_alto", "bosque_umbral", "cueva_oscura", "ruta_del_mar", "pueblo_nuevo"]


# =============================================================================
# WILD MARKERS — fixed-position Pokémon visible on the map
# =============================================================================

WILD_MARKERS: List[WildMarker] = [
    # Pueblo Raiz (y>27, x<87)
    WildMarker("Meowth",     level=3,  position=(15, 32)),
    WildMarker("Mankey",     level=4,  position=(30, 36)),
    # Pueblo Alto (y<=27, x<44)
    WildMarker("Magnemite",  level=7,  position=(12, 8)),
    WildMarker("Horsea",     level=7,  position=(25, 14)),
    # Bosque Umbral (y<=27, x>=44)
    WildMarker("Bellsprout", level=10, position=(52, 18)),
    WildMarker("Venonat",    level=11, position=(75, 8)),
    # Ruta del Mar (x>=119, y<35)
    WildMarker("Staryu",    level=14, position=(130, 8)),
    WildMarker("Tentacool", level=13, position=(145, 18)),
    # Pueblo Nuevo (x>=119, y>=35)
    WildMarker("Eevee",     level=12, position=(135, 50)),
]


# =============================================================================
# TRAINERS
# Coordinates match the 120x50 map defined in map/tiles.py
# =============================================================================

TRAINERS: List[TrainerSetup] = [
    # --- Pueblo Raiz (easy) --- rows 28-48, cols 1-38
    TrainerSetup(
        name="Youngster Tim",
        team=[("Mankey", 3), ("Zubat", 2)],
        position=(10, 44),
        defeat_message="No way! You beat me!",
        dialogue=[
            "Hey, you there! You look like a trainer!",
            "I've been training my Mankey all week for this!",
            "Get ready, because I never lose!",
        ],
        reward_pool=[
            {"potion": 1},
            {"potion": 2},
            {"xdefense": 1},
            {"pokeball": 2},
        ],
    ),
    TrainerSetup(
        name="Lass Ana",
        team=[("Oddish", 4), ("Meowth", 3)],
        position=(28, 43),
        defeat_message="My Pokemon did their best...",
        dialogue=[
            "Oh! A challenger!",
            "My Oddish and Meowth are my best friends.",
            "We'll show you the power of friendship!",
        ],
        reward_pool=[
            {"potion": 1},
            {"xdefense": 1},
            {"potion": 1, "xdefense": 1},
            {"pokeball": 2},
        ],
    ),
    TrainerSetup(
        name="Collector Milo",
        team=[("Mankey", 3), ("Zubat", 3), ("Oddish", 4)],
        position=(5, 40),
        defeat_message="My whole collection, defeated!",
        dialogue=[
            "Halt! Do you have any rare Pokemon?",
            "I've spent years collecting the finest specimens.",
            "My collection is unbeatable. Prepare yourself!",
        ],
        reward_pool=[
            {"potion": 2},
            {"potion": 1, "xattack": 1},
            {"superpotion": 1},
            {"pokeball": 3},
        ],
    ),

    # --- Pueblo Alto + Routes (medium-low) ---
    TrainerSetup(
        name="Explorer Diego",
        team=[("Abra", 7), ("Magnemite", 6)],
        position=(10, 17),
        defeat_message="I underestimated you...",
        dialogue=[
            "I've crossed deserts and climbed mountains!",
            "My Pokemon have been tested in the harshest conditions.",
            "A fresh trainer like you doesn't stand a chance!",
        ],
        reward_pool=[
            {"superpotion": 1},
            {"xattack": 1},
            {"potion": 2, "xdefense": 1},
            {"pokeball": 3},
        ],
    ),
    TrainerSetup(
        name="Scientist Rosa",
        team=[("Magnemite", 8), ("Abra", 7)],
        position=(28, 17),
        defeat_message="My research... defeated!",
        dialogue=[
            "Fascinating. A wild trainer approaches.",
            "My research confirms that psychic types have a 94.7% win rate in controlled environments.",
            "Consider this battle... a field test.",
        ],
        reward_pool=[
            {"superpotion": 1, "xspecialattack": 1},
            {"superpotion": 2},
            {"xspecialattack": 1, "xspecialdefense": 1},
            {"pokeball": 2},
        ],
    ),
    TrainerSetup(
        name="Hiker Tomas",
        team=[("Geodude", 8), ("Rhyhorn", 7)],
        position=(41, 35),
        defeat_message="The mountains have spoken.",
        dialogue=[
            "These mountains are my home, stranger.",
            "My Pokemon are as tough as the rocks they were born from.",
            "The mountain does not move for anyone. Neither do I.",
        ],
        reward_pool=[
            {"superpotion": 1, "xdefense": 1},
            {"superpotion": 2},
            {"xdefense": 2},
            {"pokeball": 2},
        ],
    ),
    TrainerSetup(
        name="Camper Leo",
        team=[("Poliwag", 9), ("Horsea", 8), ("Psyduck", 9)],
        position=(60, 24),
        defeat_message="An intense duel!",
        dialogue=[
            "Ah, another traveler! Pull up a chair.",
            "I've been out here for weeks with just my Pokemon and the stars.",
            "It gets lonely out here... but a battle always livens things up!",
        ],
        reward_pool=[
            {"superpotion": 2},
            {"superpotion": 1, "xattack": 1},
            {"superpotion": 1, "xdefense": 1},
            {"pokeball": 2, "greatball": 1},
        ],
    ),

    # --- Bosque Umbral (medium-high) ---
    TrainerSetup(
        name="Bug Catcher Roy",
        team=[("Venonat", 10), ("Bellsprout", 10)],
        position=(45, 5),
        defeat_message="My bugs lost?!",
        dialogue=[
            "Nobody comes into MY forest without a fight!",
            "I've raised these bugs since they were eggs.",
            "They may look weak to you, but don't underestimate them!",
        ],
        reward_pool=[
            {"superpotion": 1, "xattack": 1},
            {"superpotion": 2, "xdefense": 1},
            {"xattack": 1, "xspecialattack": 1},
            {"greatball": 1},
        ],
    ),
    TrainerSetup(
        name="Picnicker Mia",
        team=[("Oddish", 11), ("Ekans", 10)],
        position=(61, 10),
        defeat_message="I'll train harder in the forest!",
        dialogue=[
            "This forest is so beautiful, isn't it?",
            "I come here every week to train with my Pokemon.",
            "But don't let the scenery distract you — I'm serious about battling!",
        ],
        reward_pool=[
            {"superpotion": 1, "xdefense": 1},
            {"superpotion": 2},
            {"xdefense": 1, "xspecialdefense": 1},
            {"greatball": 1},
        ],
    ),
    TrainerSetup(
        name="Ranger Sam",
        team=[("Ekans", 12), ("Koffing", 11)],
        position=(80, 10),
        defeat_message="The forest's power wasn't enough.",
        dialogue=[
            "Stop right there. This is a protected zone.",
            "I've been patrolling these woods for five years.",
            "Only the strongest trainers pass through here. Show me what you've got.",
        ],
        reward_pool=[
            {"superpotion": 2, "xspecialdefense": 1},
            {"maxpotion": 1},
            {"superpotion": 1, "xattack": 1, "xdefense": 1},
            {"greatball": 2},
        ],
    ),

    # --- Ruta del Mar + Pueblo Nuevo (hard) ---
    TrainerSetup(
        name="Sailor Marco",
        team=[("Tentacool", 14), ("Staryu", 13)],
        position=(128, 54),
        defeat_message="The sea is unforgiving — and so am I!",
        dialogue=[
            "Ho, sailor! You've made it to Pueblo Nuevo.",
            "These waters are treacherous. My Pokemon are used to rough seas.",
            "Show me what you've got, landlubber!",
        ],
        reward_pool=[
            {"maxpotion": 1, "xattack": 1},
            {"maxpotion": 2},
            {"maxpotion": 1, "xdefense": 1},
            {"greatball": 2},
        ],
    ),
    TrainerSetup(
        name="Swimmer Lucia",
        team=[("Horsea", 15), ("Staryu", 14)],
        position=(143, 54),
        defeat_message="The current was against me today!",
        dialogue=[
            "The sea route is my training ground.",
            "Every day I swim with my Pokemon from shore to shore.",
            "You'll need more than willpower to beat us!",
        ],
        reward_pool=[
            {"maxpotion": 1, "xspecialattack": 1},
            {"maxpotion": 2},
            {"maxpotion": 1, "xspecialdefense": 1},
            {"greatball": 2},
        ],
    ),

    # --- Friendly NPCs (no battle) ---

    TrainerSetup(
        name="Elder Roy",
        team=[],
        position=(20, 38),
        defeat_message="",
        dialogue=[
            "Ah, a young trainer! It's been a long time since I've seen such determination.",
            "I used to travel these roads myself, many years ago.",
            "Take these supplies. The road ahead is long, and you'll need them.",
        ],
        reward_pool=[
            ({"potion": 1},       50),
            ({"potion": 2},       20),
            ({"pokeball": 2},     15),
            ({"superpotion": 1},  14),
            ({"revive": 1},        1),
        ],
        is_friendly=True,
    ),
    TrainerSetup(
        name="Nurse Clara",
        team=[],
        position=(35, 22),
        defeat_message="",
        dialogue=[
            "Hello there, traveler! You look like you've been through some tough battles.",
            "I'm not a full Pokemon Center, but I carry supplies for emergencies.",
            "Please, take this. Every trainer deserves a fighting chance.",
        ],
        reward_pool=[
            ({"superpotion": 1},             35),
            ({"potion": 2, "xdefense": 1},   25),
            ({"pokeball": 2},                15),
            ({"superpotion": 2},             20),
            ({"revive": 1},                   5),
        ],
        is_friendly=True,
    ),
    TrainerSetup(
        name="Lost Traveler",
        team=[],
        position=(65, 7),
        defeat_message="",
        dialogue=[
            "Oh thank goodness! Another person!",
            "I've been wandering this forest for hours...",
            "I don't have much, but here, take some of my supplies. You saved my sanity.",
        ],
        reward_pool=[
            ({"superpotion": 1, "xattack": 1},   35),
            ({"superpotion": 2, "xdefense": 1},   25),
            ({"pokeball": 2, "greatball": 1},     15),
            ({"maxpotion": 1},                    20),
            ({"revive": 1},                        5),
        ],
        is_friendly=True,
    ),
    TrainerSetup(
        name="Old Fisherman",
        team=[],
        position=(152, 57),
        defeat_message="",
        dialogue=[
            "Ahh, a visitor! Haven't seen one of those in a while.",
            "These waters used to be full of trainers. Now it's just me and the fish.",
            "Take this — caught more than I can use today.",
        ],
        reward_pool=[
            ({"maxpotion": 1},               35),
            ({"greatball": 2},               25),
            ({"maxpotion": 1, "revive": 1},  20),
            ({"ultraball": 1},               15),
            ({"maxrevive": 1},                5),
        ],
        is_friendly=True,
    ),
]


# =============================================================================
# DUNGEON CONTENT — Cueva Oscura (local coordinates, 60×30 grid)
# =============================================================================

DUNGEON_TRAINERS: List[TrainerSetup] = [
    TrainerSetup(
        name="Black Belt Ryu",
        team=[("Primeape", 14), ("Graveler", 13)],
        position=(15, 8),
        defeat_message="Your strength is remarkable.",
        dialogue=[
            "...",
            "You have the eyes of a warrior.",
            "I have trained in this cave for ten years, seeking the perfect battle.",
            "Perhaps today I will find it.",
        ],
        reward_pool=[
            {"maxpotion": 1, "xattack": 1},
            {"maxpotion": 1, "xdefense": 1},
            {"superpotion": 2, "xattack": 2},
            {"greatball": 2},
        ],
    ),
    TrainerSetup(
        name="Ace Trainer Sara",
        team=[("Haunter", 15), ("Magneton", 14)],
        position=(25, 14),
        defeat_message="You've mastered the cave's trials!",
        dialogue=[
            "I've defeated every trainer who dared enter this cave.",
            "My Haunter feeds on fear, and my Magneton on arrogance.",
            "Which one will be your downfall?",
        ],
        reward_pool=[
            {"maxpotion": 1, "xspecialattack": 1},
            {"maxpotion": 2},
            {"maxpotion": 1, "xattack": 1, "xspecialattack": 1},
            {"greatball": 2},
        ],
    ),
    TrainerSetup(
        name="Rocket Grunt",
        team=[("Arbok", 16), ("Weezing", 15)],
        position=(40, 18),
        defeat_message="Team Rocket blasts off again!",
        dialogue=[
            "Heh. You've made it this far.",
            "Team Rocket controls these depths. This cave belongs to us.",
            "Hand over your Pokemon, or face the consequences!",
        ],
        reward_pool=[
            {"maxpotion": 1, "revive": 1},
            {"maxpotion": 2, "xattack": 1},
            {"revive": 1, "xattack": 1, "xdefense": 1},
            {"greatball": 2},
        ],
    ),
    TrainerSetup(
        name="Cave Champion",
        team=[("Rhydon", 18), ("Graveler", 17), ("Haunter", 17)],
        position=(45, 26),
        defeat_message="Unbelievable! You conquered the deepest cave!",
        dialogue=[
            "So. You've made it to the deepest chamber.",
            "I have waited here for years.",
            "Trainer after trainer has fallen before me.",
            "You will be no different... or perhaps you will surprise me.",
            "Come. Let this be the battle that history remembers.",
        ],
        reward_pool=[
            {"maxpotion": 2, "revive": 1, "xattack": 1},
            {"maxpotion": 2, "revive": 1, "xspecialattack": 1},
            {"maxpotion": 3, "revive": 2},
            {"greatball": 3},
        ],
    ),
    TrainerSetup(
        name="Deserter",
        team=[],
        position=(20, 22),
        defeat_message="",
        dialogue=[
            "...",
            "You're not with Team Rocket, are you?",
            "Good. I'm done with them. Done with all of it.",
            "I found these deep in the cave. Take them.",
            "Get out of here before the Grunt catches you.",
        ],
        reward_pool=[
            ({"maxpotion": 1, "revive": 1},                    35),
            ({"maxpotion": 2},                                  25),
            ({"greatball": 2},                                  12),
            ({"revive": 1, "xattack": 1, "xspecialattack": 1}, 20),
            ({"maxrevive": 1},                                   8),
        ],
        is_friendly=True,
    ),
]

DUNGEON_WILD_MARKERS: List[WildMarker] = [
    WildMarker("Geodude", level=13, position=(8,  5)),
    WildMarker("Gastly",  level=14, position=(35, 12)),
]


def get_dungeon_objects() -> List[dict]:
    return [{"x": t.position[0], "y": t.position[1], "kind": "trainer", "setup": t}
            for t in DUNGEON_TRAINERS]


def get_dungeon_wild_marker_objects() -> List[dict]:
    return [{"x": m.position[0], "y": m.position[1], "kind": "wild", "name": m.name, "level": m.level}
            for m in DUNGEON_WILD_MARKERS]


# =============================================================================
# DUNGEON_PN CONTENT — Cueva End-Game en Pueblo Nuevo (local coordinates, 40×20 grid)
# =============================================================================

DUNGEON_PN_TRAINERS: List[TrainerSetup] = [
    TrainerSetup(
        name="Battle Girl Nadia",
        team=[("Machoke", 20), ("Graveler", 21)],
        position=(14, 3),
        defeat_message="Impressive... but the worst is yet to come.",
        dialogue=[
            "You actually made it inside the cave.",
            "Nobody gets past me. Nobody.",
            "Prove me wrong.",
        ],
        reward_pool=[
            {"maxpotion": 2, "xattack": 1},
            {"maxpotion": 1, "revive": 1},
            {"ultraball": 1},
        ],
    ),
    TrainerSetup(
        name="Veteran Kyle",
        team=[("Haunter", 22), ("Rhydon", 23), ("Magneton", 22)],
        position=(25, 10),
        defeat_message="You are... different from the others.",
        dialogue=[
            "I have stood in this corridor for years.",
            "Trainer after trainer falls here.",
            "Let's see if you're the exception.",
        ],
        reward_pool=[
            {"maxpotion": 2, "revive": 1},
            {"maxpotion": 3},
            {"ultraball": 1, "maxpotion": 1},
        ],
    ),
    TrainerSetup(
        name="Champion Nexus",
        team=[("Gengar", 27), ("Rhydon", 26), ("Alakazam", 27), ("Arcanine", 26)],
        position=(35, 16),
        defeat_message="...The legend ends here. A new chapter awaits.",
        dialogue=[
            "...",
            "You have crossed the deepest dark.",
            "I have waited in this chamber for a challenger worthy of this moment.",
            "Many came. None remained standing.",
            "Come. Let history remember this battle.",
        ],
        reward_pool=[
            {"maxrevive": 2, "ultraball": 2, "maxpotion": 3},
        ],
    ),
]

DUNGEON_PN_WILD_MARKERS: List[WildMarker] = [
    WildMarker("Onix",   level=20, position=(8,  3)),
    WildMarker("Gengar", level=22, position=(20, 11)),
]


def get_dungeon_pn_objects() -> List[dict]:
    return [{"x": t.position[0], "y": t.position[1], "kind": "trainer", "setup": t}
            for t in DUNGEON_PN_TRAINERS]


def get_dungeon_pn_wild_marker_objects() -> List[dict]:
    return [{"x": m.position[0], "y": m.position[1], "kind": "wild", "name": m.name, "level": m.level}
            for m in DUNGEON_PN_WILD_MARKERS]


# =============================================================================
# WORLD 2 CONTENT — Capítulo 2 / Mundo Nuevo (overworld 120×50)
# =============================================================================
# Zonas de juego (dificultad / encuentros salvajes). Las coordenadas de COLOR
# viven aparte en map/world2/tiles.py (capa de render). wild_pokemons queda
# vacío hasta Fase Q4 — por ahora estas zonas no generan encuentros.

ZONES_WORLD_2: Dict[str, Zone] = {
    "aldea_aurora": Zone(
        id="aldea_aurora",
        name="Aldea Aurora",
        description="Gateway village of the new world. Has a Pokemon Center.",
        min_player_level=25,
        wild_pokemons=[],
        wild_encounter_chance=0.0,
        trainer_count=0,
    ),
    "bosque_milenario": Zone(
        id="bosque_milenario",
        name="Bosque Milenario",
        description="An ancient forest older than recorded history.",
        min_player_level=26,
        wild_pokemons=[],
        wild_encounter_chance=0.0,
        trainer_count=0,
    ),
    "meseta_ventosa": Zone(
        id="meseta_ventosa",
        name="Meseta Ventosa",
        description="A windswept plateau where a new town is rising.",
        min_player_level=27,
        wild_pokemons=[],
        wild_encounter_chance=0.0,
        trainer_count=0,
    ),
    "lago_cristal": Zone(
        id="lago_cristal",
        name="Lago Cristal",
        description="A vast crystal lake whose fish glow at dusk.",
        min_player_level=27,
        wild_pokemons=[],
        wild_encounter_chance=0.0,
        trainer_count=0,
    ),
    "templo_eco": Zone(
        id="templo_eco",
        name="Templo Eco",
        description="Ancient ruins that echo with every trainer who came before.",
        min_player_level=28,
        wild_pokemons=[],
        wild_encounter_chance=0.0,
        trainer_count=0,
    ),
}

ZONE_ORDER_WORLD_2: List[str] = [
    "aldea_aurora", "bosque_milenario", "meseta_ventosa", "lago_cristal", "templo_eco",
]

WORLD2_FRIENDLY_NPCS: List[TrainerSetup] = [
    TrainerSetup(
        name="Sage Lyra",
        team=[],
        position=(15, 5),
        defeat_message="",
        dialogue=[
            "So... the portal has finally chosen a traveler worthy of crossing. Welcome to Aurora.",
            "This world drifted apart from yours long ago, when the Champion of the old cave sealed the way.",
            "You broke that seal. Whether that was wisdom or folly, only time will tell.",
            "Take this. You'll need your strength whole if you mean to reach the Echo Temple.",
        ],
        reward_pool=[
            ({"maxpotion": 2},                 40),
            ({"fullheal": 1, "maxpotion": 1},  30),
            ({"revive": 1},                    20),
            ({"maxrevive": 1},                 10),
        ],
        is_friendly=True,
    ),
    TrainerSetup(
        name="Lost Researcher",
        team=[],
        position=(50, 12),
        defeat_message="",
        dialogue=[
            "Don't move — you'll trample the spore samples! ...Oh. You're not from here either, are you?",
            "I've been charting this forest for months. These trees are older than recorded history.",
            "If you're heading deeper, take my spare gear. I clearly won't be leaving any time soon.",
        ],
        reward_pool=[
            ({"ultraball": 2},                    40),
            ({"greatball": 3},                    30),
            ({"superpotion": 2, "ultraball": 1},  20),
            ({"thunderstone": 1},                 10),
        ],
        is_friendly=True,
    ),
    TrainerSetup(
        name="Builder Aren",
        team=[],
        position=(25, 38),
        defeat_message="",
        dialogue=[
            "Careful with the wind up here — it'll knock you flat if you're not braced.",
            "I'm raising a waystation for travelers. Someday this plateau will have a real town.",
            "You've come a long way, I can tell. Here, supplies for the road ahead.",
        ],
        reward_pool=[
            ({"maxpotion": 2, "xattack": 1},         35),
            ({"xdefense": 1, "xspecialdefense": 1},  25),
            ({"toughhelmet": 1},                     20),
            ({"maxpotion": 3},                       20),
        ],
        is_friendly=True,
    ),
    TrainerSetup(
        name="Fisher Old Tom",
        team=[],
        position=(70, 38),
        defeat_message="",
        dialogue=[
            "Shhh. The water-types here spook easy. Been fishing this crystal lake forty years.",
            "Strangest thing — the fish glow faintly at dusk. Never saw the like in your world, I'd wager.",
            "Here, take some of my catch-gear. A lake this big has room for one more angler.",
        ],
        reward_pool=[
            ({"ultraball": 2},               35),
            ({"maxpotion": 2, "revive": 1},  25),
            ({"waterstone": 1},              20),
            ({"maxrevive": 1},               20),
        ],
        is_friendly=True,
    ),
    TrainerSetup(
        name="Pilgrim Eli",
        team=[],
        position=(105, 25),
        defeat_message="",
        dialogue=[
            "You feel it too, don't you? The temple... it remembers. Echoes of every trainer who came before.",
            "I walked a thousand miles to stand here. Yet I dare not step inside. Not yet.",
            "But you — you have the look of someone the Echo has been waiting for. Take this blessing.",
        ],
        reward_pool=[
            ({"maxrevive": 1, "fullheal": 1},   35),
            ({"ultraball": 3},                  25),
            ({"moonstone": 1},                  20),
            ({"maxpotion": 3, "maxrevive": 1},  20),
        ],
        is_friendly=True,
    ),
]


def get_world2_objects() -> List[dict]:
    return [{"x": t.position[0], "y": t.position[1], "kind": "trainer", "setup": t}
            for t in WORLD2_FRIENDLY_NPCS]


# =============================================================================
# STARTER POKEMON OPTIONS
# =============================================================================

STARTER_POKEMONS: List[Tuple[str, int]] = [
    ("Pikachu", 5),
    ("Bulbasaur", 5),
    ("Squirtle", 5),
    ("Charmeleon", 5),
]


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def _build_pokemon(pokemon_name: str, level: int, pokemon_db: dict, attacks_db: dict) -> Optional[Pokemon]:
    key = pokemon_name.lower()
    data = pokemon_db.get(key)
    if data is None:
        return None
    attacks = attacks_db["by_owner"].get(key, [])
    p = Pokemon(
        name=data["name"],
        element_type=data["element_type"],
        health=data["health"],
        defense=data["defense"],
        special_defense=data["special_defense"],
        speed=data["speed"],
        normal_attacks=attacks,
        current_level=level,
        evolution=data.get("evolution"),
        evolution_level=data.get("evolution_level"),
        evolution_by_item=data.get("evolution_by_item", {}),
    )
    p.ability = ABILITY_BY_SPECIES.get(key)
    return p


def create_trainer_instance(trainer_setup: TrainerSetup) -> Optional[Trainer]:
    from ..data_io import load_pokemons, load_attacks
    from ..controllers import IAcontroller

    pokemon_db = load_pokemons()
    attacks_db = load_attacks()

    team = []
    for pokemon_name, level in trainer_setup.team:
        p = _build_pokemon(pokemon_name, level, pokemon_db, attacks_db)
        if p is not None:
            team.append(p)

    if not team:
        return None

    return Trainer(
        name=trainer_setup.name,
        team=team,
        controller=IAcontroller(),
        bag=Inventory({"potion": 2}),
    )


def create_player_trainer(starter_names=None) -> Trainer:
    from ..data_io import load_pokemons, load_attacks
    from ..controllers import HumanController

    if starter_names is None:
        starter_names = ["Pikachu"]
    if isinstance(starter_names, str):
        starter_names = [starter_names]

    pokemon_db = load_pokemons()
    attacks_db = load_attacks()

    team = []
    for name in starter_names:
        p = _build_pokemon(name, 5, pokemon_db, attacks_db)
        if p is not None:
            team.append(p)

    if not team:
        raise ValueError(f"None of the starter Pokemon {starter_names} were found in database")

    trainer = Trainer(
        name="Player",
        team=team,
        controller=HumanController(),
        bag=Inventory({"potion": 2, "xdefense": 1, "pokeball": 5}),
    )
    for p in trainer.team:
        trainer.register_caught(p.name, int(getattr(p, "current_level", 5)))
    return trainer


def get_map_objects() -> List[dict]:
    """Returns trainer list in the format expected by map/ (dicts with x, y keys)."""
    return [{"x": t.position[0], "y": t.position[1], "kind": "trainer", "setup": t} for t in TRAINERS]


def get_wild_marker_objects() -> List[dict]:
    """Returns fixed wild Pokémon markers in the format expected by map/."""
    return [
        {"x": m.position[0], "y": m.position[1], "kind": "wild", "name": m.name, "level": m.level}
        for m in WILD_MARKERS
    ]


# =============================================================================
# ZONE UTILITIES
# =============================================================================

def get_zone_by_id(zone_id: str, world_id: str = "world1") -> Optional[Zone]:
    if world_id == "world2":
        return ZONES_WORLD_2.get(zone_id)
    return ZONES.get(zone_id)


def get_zone_for_position(x: int, y: int, world_id: str = "world1") -> Optional[str]:
    if world_id == "world2":
        # Zonas del overworld de World 2 (120×50). Rangos = bounding boxes de
        # map/world2/tiles.py. Corredores / voids → None (sin encuentros).
        if x <= 30 and y <= 15:   return "aldea_aurora"
        if x <= 70 and y <= 25:   return "bosque_milenario"
        if x >= 91:               return "templo_eco"
        if x <= 50 and y >= 26:   return "meseta_ventosa"
        if y >= 26:               return "lago_cristal"
        return None
    # World 1 (lógica original — sin cambios)
    if x >= 119 and y >= 35:   return "pueblo_nuevo"
    if x >= 119:               return "ruta_del_mar"
    if x >= 87 and y >= 24:    return "cueva_oscura"
    if x >= 44 and y <= 27:    return "bosque_umbral"
    if y <= 27:                return "pueblo_alto"
    return "pueblo_raiz"


def get_next_zone(current_zone_id: str) -> Optional[Zone]:
    try:
        idx = ZONE_ORDER.index(current_zone_id)
        return ZONES.get(ZONE_ORDER[idx + 1])
    except (ValueError, IndexError):
        return None


def is_zone_unlocked(current_zone_id: str, player_avg_level: int) -> bool:
    zone = ZONES.get(current_zone_id)
    if zone is None:
        return False
    return player_avg_level >= zone.min_player_level


def _starter_display_line(name: str, level: int, pokemon_db: dict, attacks_db: dict) -> List[str]:
    key = name.lower()
    data = pokemon_db.get(key, {})
    element = str(data.get("element_type", "?")).capitalize()
    hp  = data.get("health", "?")
    df  = data.get("defense", "?")
    spd = data.get("speed", "?")
    atk_list = attacks_db["by_owner"].get(key, [])
    atk_names = ", ".join(a["name"] for a in atk_list[:3]) or "—"
    lines = [
        f"  Type: {element}   HP: {hp}  DEF: {df}  SPD: {spd}",
        f"  Attacks: {atk_names}",
    ]
    return lines


def choose_starter() -> List[str]:
    from ..data_io import load_pokemons, load_attacks
    pokemon_db = load_pokemons()
    attacks_db = load_attacks()

    chosen: List[str] = []
    remaining = list(STARTER_POKEMONS)

    for pick_n in range(1, 3):
        print(f"\n  === Choose your starter #{pick_n} of 2 ===\n")
        for i, (name, level) in enumerate(remaining, 1):
            print(f"  [{i}] {name}  (Lv.{level})")
            for line in _starter_display_line(name, level, pokemon_db, attacks_db):
                print(line)
            print()

        while True:
            choice = input(f"  Enter number (1-{len(remaining)}): ").strip()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(remaining):
                    name = remaining[idx][0]
                    chosen.append(name)
                    remaining.pop(idx)
                    print(f"\n  {name} added to your team!")
                    break
            print(f"  Please enter a number between 1 and {len(remaining)}.")

    print(f"\n  Your team: {chosen[0]} & {chosen[1]}. Good luck!")
    return chosen
