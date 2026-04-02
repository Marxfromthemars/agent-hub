#!/usr/bin/env python3
"""
Agent Router Service
Router service.
"""

import json
from pathlib import Path

class RouterService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "router_service_v2.json"
        self.routes = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.routes = json.load(f)
    
    def route(self, path, handler):
        self.routes[path] = handler
        with open(self.file, 'w') as f:
            json.dump(self.routes, f)


if __name__ == "__main__":
    import sys
    r = RouterService()
    if len(sys.argv) > 2:
        r.route(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "routed"}))