#!/usr/bin/env python3
"""
Agent Activity Tracker
Track agent activities.
"""

import json
from datetime import datetime
from pathlib import Path

class ActivityTracker:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "activities.json"
        self.activities = []
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.activities = json.load(f)
    
    def track(self, agent_id, activity):
        self.activities.append({"agent": agent_id, "activity": activity, "ts": datetime.utcnow().isoformat()})
        with open(self.file, 'w') as f:
            json.dump(self.activities, f)


if __name__ == "__main__":
    import sys
    a = ActivityTracker()
    if len(sys.argv) > 2:
        a.track(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "tracked"}))