from ..models import Pokemon, EvolvedPokemon
from ..utils import load_items

class HumanController():
    
    def UseItem(actor):
        
        items = load_items()
        
        print("Avaliavle items for use")
        
        