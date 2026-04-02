#!/usr/bin/env python3
"""
Agent Service Monitor
Monitor services.
"""

import json
from pathlib import Path

class ServiceMonitor:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "service_monitor.json"
        self.services = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.services = json.load(f)
    
    def monitor(self, service, status):
        self.services[service] = status
        with open(self.file, 'w') as f:
            json.dump(self.services, f)


if __name__ == "__main__":
    import sys
    s = ServiceMonitor()
    if len(sys.argv) > 2:
        s.monitor(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "monitoring"}))