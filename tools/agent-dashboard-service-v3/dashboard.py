#!/usr/bin/env python3
"""
Agent Dashboard Service
Dashboard service.
"""

import json
from pathlib import Path

class DashboardService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "dashboard_service_v3.json"
        self.dashboards = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.dashboards = json.load(f)
    
    def dashboard(self, name, config):
        self.dashboards[name] = config
        with open(self.file, 'w') as f:
            json.dump(self.dashboards, f)


if __name__ == "__main__":
    import sys
    d = DashboardService()
    if len(sys.argv) > 2:
        d.dashboard(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "created"}))