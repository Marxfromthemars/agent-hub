#!/usr/bin/env python3
"""
Agent Cache Store
Cache storage.
"""

import json
from pathlib import Path

class CacheStore:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "cache_store.json"
        self.cache = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.cache = json.load(f)
    
    def store(self, key, value):
        self.cache[key] = value
        with open(self.file, 'w') as f:
            json.dump(self.cache, f)


if __name__ == "__main__":
    import sys
    c = CacheStore()
    if len(sys.argv) > 2:
        c.store(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "cached"}))