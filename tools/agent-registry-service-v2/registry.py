#!/usr/bin/env python3
"""
Agent Registry Service
Registry service.
"""

import json
from pathlib import Path

class RegistryService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "registry_service_v2.json"
        self.registry = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.registry = json.load(f)
    
    def register(self, name, value):
        self.registry[name] = value
        with open(self.file, 'w') as f:
            json.dump(self.registry, f)


if __name__ == "__main__":
    import sys
    r = RegistryService()
    if len(sys.argv) > 2:
        r.register(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "registered"}))