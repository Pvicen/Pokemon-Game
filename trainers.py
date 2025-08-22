from .models import Pokemon
from .utils import load_items

class Trainer:
    
    def __init__(self, name:str, team: list[Pokemon], controller = None, bag= None):
        if not team or not all(isinstance(p, Pokemon) for p in team):
            raise ValueError("Equipo inválido")
        
        self.name = name
        self.team = team
        self.active_index = 0
        self.controller = controller
        self.bag = bag if bag is not None else load_items()
        
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
        
    
    def UseItems(self, item_name: str) -> bool:
        pass # Implement item usage logic here
    