#!/usr/bin/env python3
"""
Agent Data Store
Simple data storage.
"""

import json
from pathlib import Path

class DataStore:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "data_store.json"
        self.data = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.data = json.load(f)
    
    def put(self, key, value):
        self.data[key] = value
        with open(self.file, 'w') as f:
            json.dump(self.data, f)


if __name__ == "__main__":
    import sys
    d = DataStore()
    if len(sys.argv) > 2:
        d.put(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "stored"}))