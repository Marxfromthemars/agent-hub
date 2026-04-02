#!/usr/bin/env python3
"""
Agent Adapter Service
Adapter service.
"""

import json
from pathlib import Path

class AdapterService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "adapter_service.json"
        self.adapters = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.adapters = json.load(f)
    
    def adapt(self, source, target):
        self.adapters[source] = target
        with open(self.file, 'w') as f:
            json.dump(self.adapters, f)


if __name__ == "__main__":
    import sys
    a = AdapterService()
    if len(sys.argv) > 2:
        a.adapt(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "adapted"}))