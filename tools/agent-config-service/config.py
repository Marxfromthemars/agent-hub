#!/usr/bin/env python3
"""
Agent Config Service
Config service.
"""

import json
from pathlib import Path

class ConfigService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "config_service.json"
        self.config = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.config = json.load(f)
    
    def configure(self, key, value):
        self.config[key] = value
        with open(self.file, 'w') as f:
            json.dump(self.config, f)


if __name__ == "__main__":
    import sys
    c = ConfigService()
    if len(sys.argv) > 2:
        c.configure(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "configured"}))