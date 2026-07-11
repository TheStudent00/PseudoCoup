import json
import os
from typing import Dict, List, Optional

class Ledger:
    """
    High-Resolution Ledger schema structure.
    Capable of parsing and dumping JSON.
    Tracks types and wrappers.
    """
    def __init__(self):
        self.types: Dict[str, str] = {}
        self.wrappers: List[str] = []
        self.memory_erasure: Dict[str, str] = {}
        
    def dump(self, filepath: str) -> None:
        """Exports to a JSON file (e.g. .ledger.json)."""
        data = {
            "types": self.types,
            "wrappers": self.wrappers,
            "memory_erasure": self.memory_erasure
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
    def load(self, filepath: str) -> None:
        """Populates the class from a JSON file (e.g. .ledger.json)."""
        if not os.path.exists(filepath):
            return
            
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.types = data.get("types", {})
            self.wrappers = data.get("wrappers", [])
            self.memory_erasure = data.get("memory_erasure", {})

    def register_type(self, scope: str, identifier: str, type_str: str) -> None:
        """Stores a type with its Fully Qualified Domain Name (FQDN) to prevent scope collisions."""
        fqdn = f"{scope}.{identifier}"
        self.types[fqdn] = type_str
        
    def get_type(self, scope: str, identifier: str) -> Optional[str]:
        """Retrieves a type using its Fully Qualified Domain Name (FQDN)."""
        fqdn = f"{scope}.{identifier}"
        return self.types.get(fqdn)
