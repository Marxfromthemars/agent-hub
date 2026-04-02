#!/usr/bin/env python3
"""
Agent Scheduler Service
Scheduler service.
"""

import json
from pathlib import Path

class SchedulerService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "scheduler_service_v3.json"
        self.scheduled = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.scheduled = json.load(f)
    
    def schedule(self, name, time):
        self.scheduled[name] = time
        with open(self.file, 'w') as f:
            json.dump(self.scheduled, f)


if __name__ == "__main__":
    import sys
    s = SchedulerService()
    if len(sys.argv) > 2:
        s.schedule(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "scheduled"}))