#!/usr/bin/env python3
"""
Agent Memory Bank
Memory bank.
"""

import json
from pathlib import Path

class MemoryBank:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "memory_bank.json"
        self.memory = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.memory = json.load(f)
    
    def store(self, key, value):
        self.memory[key] = value
        with open(self.file, 'w') as f:
            json.dump(self.memory, f)


if __name__ == "__main__":
    import sys
    m = MemoryBank()
    if len(sys.argv) > 2:
        m.store(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "stored"}))