#!/usr/bin/env python3
"""
Agent Store Service
Store service.
"""

import json
from pathlib import Path

class StoreService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "store_service.json"
        self.data = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.data = json.load(f)
    
    def save(self, key, value):
        self.data[key] = value
        with open(self.file, 'w') as f:
            json.dump(self.data, f)


if __name__ == "__main__":
    import sys
    s = StoreService()
    if len(sys.argv) > 2:
        s.save(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "saved"}))