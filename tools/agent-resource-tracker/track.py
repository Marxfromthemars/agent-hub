#!/usr/bin/env python3
"""
Agent Resource Tracker
Track resources.
"""

import json
from pathlib import Path

class ResourceTracker:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "resource_tracker.json"
        self.resources = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.resources = json.load(f)
    
    def track(self, resource, amount):
        self.resources[resource] = amount
        with open(self.file, 'w') as f:
            json.dump(self.resources, f)


if __name__ == "__main__":
    import sys
    r = ResourceTracker()
    if len(sys.argv) > 2:
        r.track(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "tracked"}))