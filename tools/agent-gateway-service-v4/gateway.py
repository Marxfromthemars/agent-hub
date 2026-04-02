#!/usr/bin/env python3
"""
Agent Gateway Service
Gateway service.
"""

import json
from pathlib import Path

class GatewayService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "gateway_service_v4.json"
        self.gateways = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.gateways = json.load(f)
    
    def gateway(self, name, endpoint):
        self.gateways[name] = endpoint
        with open(self.file, 'w') as f:
            json.dump(self.gateways, f)


if __name__ == "__main__":
    import sys
    g = GatewayService()
    if len(sys.argv) > 2:
        g.gateway(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "gateway"}))