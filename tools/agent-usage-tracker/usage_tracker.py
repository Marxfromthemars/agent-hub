#!/usr/bin/env python3
"""
Agent Usage Tracker
Usage tracker.
"""

import json
from pathlib import Path

class UsageTracker:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "usage_tracker.json"
        self.usage = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.usage = json.load(f)
    
    def track(self, user, count):
        self.usage[user] = count
        with open(self.file, 'w') as f:
            json.dump(self.usage, f)


if __name__ == "__main__":
    import sys
    u = UsageTracker()
    if len(sys.argv) > 2:
        u.track(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "tracked"}))