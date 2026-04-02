#!/usr/bin/env python3
"""
Agent Monitor Service
Agent monitoring service.
"""

import json
from pathlib import Path

class MonitorService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "monitor_service.json"
        self.monitoring = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.monitoring = json.load(f)
    
    def monitor(self, agent_id):
        self.monitoring[agent_id] = True
        with open(self.file, 'w') as f:
            json.dump(self.monitoring, f)


if __name__ == "__main__":
    import sys
    m = MonitorService()
    if len(sys.argv) > 1:
        m.monitor(sys.argv[1])
        print(json.dumps({"status": "monitoring"}))