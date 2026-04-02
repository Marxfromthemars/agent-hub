#!/usr/bin/env python3
"""
Agent Cache Service
Cache service.
"""

import json
from pathlib import Path

class CacheService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "cache_service_v2.json"
        self.cache = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.cache = json.load(f)
    
    def cache(self, key, value):
        self.cache[key] = value
        with open(self.file, 'w') as f:
            json.dump(self.cache, f)


if __name__ == "__main__":
    import sys
    c = CacheService()
    if len(sys.argv) > 2:
        c.cache(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "cached"}))