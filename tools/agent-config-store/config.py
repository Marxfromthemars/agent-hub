#!/usr/bin/env python3
"""
Agent Config Store
Configuration storage.
"""

import json
from pathlib import Path

class ConfigStore:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "config_store.json"
        self.config = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.config = json.load(f)
    
    def set(self, key, value):
        self.config[key] = value
        with open(self.file, 'w') as f:
            json.dump(self.config, f)
    
    def get(self, key):
        return self.config.get(key)


if __name__ == "__main__":
    c = ConfigStore()
    if len(__import__('sys').argv) > 2:
        c.set(__import__('sys').argv[1], __import__('sys').argv[2])
        print(json.dumps({"status": "set"}))