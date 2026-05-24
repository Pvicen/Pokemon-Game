from .models import Pokemon
from .data_io import load_items
from .inventory import Inventory

class Trainer:
    
    def __init__(self, name:str, team: list[Pokemon], controller=None, bag: Inventory | None = None):
        if not team or not all(isinstance(p, Pokemon) for p in team):
            raise ValueError("Equipo inválido")
        
        self.name = name
        self.team = team
        self.active_index = 0
        self.controller = controller
        
        #Default items
        self.bag = bag if bag is not None else Inventory({"potion": 1, "xdefense": 1})
        self.pokedex_seen: list[dict] = []
            
    @property
    def ActivePokemon(self) -> Pokemon:
        return self.team[self.active_index]
    
    
    def HasAvaliablePokemon(self) -> bool:
        return any(p.is_alive() for p in self.team)
    

    def CheckPokemonSwitch(self, index: int) -> bool:
        return (
            0 <= index < len(self.team)
            and self.team[index].is_alive()
            and index != self.active_index
        )
        
    
    def SwitchPokemon(self, index: int) -> bool:
        if self.CheckPokemonSwitch(index):
            self.active_index = index
            print(f"🔄 {self.name} switched to {self.ActivePokemon.name}!")
            return True
        return False
        
    
    def register_seen(self, pokemon_name: str) -> None:
        if not any(e["name"] == pokemon_name for e in self.pokedex_seen):
            self.pokedex_seen.append({"name": pokemon_name, "caught": False, "level_caught": None})

    def register_caught(self, pokemon_name: str, level: int) -> None:
        for e in self.pokedex_seen:
            if e["name"] == pokemon_name:
                e["caught"] = True
                e["level_caught"] = level
                return
        self.pokedex_seen.append({"name": pokemon_name, "caught": True, "level_caught": level})

    def UseItems(self, item_key: str, enemy_trainer=None, in_battle: bool = True, target_index: int | None = None) -> bool:
        if self.bag is None:
            print("❌ No inventory available.")
            return False
        return self.bag.use(item_key, user_trainer=self, target_trainer=enemy_trainer, in_battle=in_battle, target_index=target_index)