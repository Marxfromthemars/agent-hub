#!/usr/bin/env python3
"""
Agent Connector Service
Connector service.
"""

import json
from pathlib import Path

class ConnectorService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "connector_service_v4.json"
        self.connectors = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.connectors = json.load(f)
    
    def connect(self, name, endpoint):
        self.connectors[name] = endpoint
        with open(self.file, 'w') as f:
            json.dump(self.connectors, f)


if __name__ == "__main__":
    import sys
    c = ConnectorService()
    if len(sys.argv) > 2:
        c.connect(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "connected"}))