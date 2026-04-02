#!/usr/bin/env python3
"""
Agent Time Tracker
Track time spent on agent activities.
"""

import json
from datetime import datetime
from pathlib import Path

class TimeTracker:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.file = self.data_dir / "time_tracker.json"
        self.data = {"entries": []}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.data = json.load(f)
    
    def _save(self):
        with open(self.file, 'w') as f:
            json.dump(self.data, f)
    
    def start(self, agent_id, task):
        entry = {"agent": agent_id, "task": task, "start": datetime.utcnow().isoformat(), "end": None}
        self.data["entries"].append(entry)
        self._save()
        return entry
    
    def stop(self, agent_id):
        for e in reversed(self.data["entries"]):
            if e["agent"] == agent_id and not e.get("end"):
                e["end"] = datetime.utcnow().isoformat()
                self._save()
                return e
        return None


if __name__ == "__main__":
    import sys
    t = TimeTracker()
    
    if len(sys.argv) < 3:
        print("Usage: time-tracker.py start|stop <agent_id> [task]")
        sys.exit()
    
    if sys.argv[1] == "start":
        print(json.dumps(t.start(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")))
    elif sys.argv[1] == "stop":
        print(json.dumps(t.stop(sys.argv[2])))