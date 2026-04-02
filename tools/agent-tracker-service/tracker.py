#!/usr/bin/env python3
"""
Agent Tracker Service
Tracker service.
"""

import json
from pathlib import Path

class TrackerService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "tracker_service.json"
        self.tracking = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.tracking = json.load(f)
    
    def track(self, item, value):
        self.tracking[item] = value
        with open(self.file, 'w') as f:
            json.dump(self.tracking, f)


if __name__ == "__main__":
    import sys
    t = TrackerService()
    if len(sys.argv) > 2:
        t.track(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "tracking"}))