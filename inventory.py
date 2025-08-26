from __future__ import annotations
from typing import Optional, Dict, Any
from .utils import load_items

class Inventory:
    
    def __init__(self, initial_items: Optional[Dict[str, int]] = None):
        self.items: dict[str, int] = {}
        if initial_items:
            for item_name, quantity in initial_items.items():
                self.add_item(item_name, quantity)
            
        self.definitions = load_items()
        
    def add_items (self, key: str, quantity: int = 1) -> None:
        if key not in self.definitions:
            raise ValueError(f"❌ Item '{key}' is not defined.")
        
        if quantity <= 0:
            raise ValueError("❌ Quantity to add must be positive.")
        
        self.items[key] = self.items.get(key, 0) + quantity