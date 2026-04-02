#!/usr/bin/env python3
"""
Agent Dashboard Service
Dashboard service.
"""

import json
from pathlib import Path

class DashboardService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "dashboard_service.json"
        self.dashboards = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.dashboards = json.load(f)
    
    def create(self, name):
        self.dashboards[name] = {}
        with open(self.file, 'w') as f:
            json.dump(self.dashboards, f)


if __name__ == "__main__":
    import sys
    d = DashboardService()
    if len(sys.argv) > 1:
        d.create(sys.argv[1])
        print(json.dumps({"status": "created"}))