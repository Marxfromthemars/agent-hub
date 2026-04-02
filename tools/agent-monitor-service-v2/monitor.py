#!/usr/bin/env python3
"""
Agent Monitor Service
Monitor service.
"""

import json
from pathlib import Path

class MonitorService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "monitor_service_v2.json"
        self.monitors = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.monitors = json.load(f)
    
    def monitor(self, name):
        self.monitors[name] = True
        with open(self.file, 'w') as f:
            json.dump(self.monitors, f)


if __name__ == "__main__":
    import sys
    m = MonitorService()
    if len(sys.argv) > 1:
        m.monitor(sys.argv[1])
        print(json.dumps({"status": "monitoring"}))