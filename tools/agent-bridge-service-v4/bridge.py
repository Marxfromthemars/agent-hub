#!/usr/bin/env python3
"""
Agent Bridge Service
Bridge service.
"""

import json
from pathlib import Path

class BridgeService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "bridge_service_v4.json"
        self.bridges = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.bridges = json.load(f)
    
    def bridge(self, source, target):
        self.bridges[source] = target
        with open(self.file, 'w') as f:
            json.dump(self.bridges, f)


if __name__ == "__main__":
    import sys
    b = BridgeService()
    if len(sys.argv) > 2:
        b.bridge(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "bridged"}))