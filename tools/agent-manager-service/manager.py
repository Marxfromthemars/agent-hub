#!/usr/bin/env python3
"""
Agent Manager Service
Manager service.
"""

import json
from pathlib import Path

class ManagerService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "manager_service.json"
        self.managers = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.managers = json.load(f)
    
    def add(self, name, config):
        self.managers[name] = config
        with open(self.file, 'w') as f:
            json.dump(self.managers, f)


if __name__ == "__main__":
    import sys
    m = ManagerService()
    if len(sys.argv) > 1:
        m.add(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "")
        print(json.dumps({"status": "added"}))