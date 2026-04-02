#!/usr/bin/env python3
"""
Agent Store Service
Store service.
"""

import json
from pathlib import Path

class StoreService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "store_service_v4.json"
        self.store = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.store = json.load(f)
    
    def put(self, key, value):
        self.store[key] = value
        with open(self.file, 'w') as f:
            json.dump(self.store, f)


if __name__ == "__main__":
    import sys
    s = StoreService()
    if len(sys.argv) > 2:
        s.put(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "stored"}))