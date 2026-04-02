#!/usr/bin/env python3
"""
Agent Scheduler Queue
Queue-based task scheduler.
"""

import json
from datetime import datetime
from pathlib import Path

class SchedulerQueue:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.file = self.data_dir / "scheduler_queue.json"
        self.data = {"queue": []}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.data = json.load(f)
    
    def _save(self):
        with open(self.file, 'w') as f:
            json.dump(self.data, f)
    
    def push(self, task, priority=0):
        self.data["queue"].append({"task": task, "priority": priority, "ts": datetime.utcnow().isoformat()})
        self.data["queue"].sort(key=lambda x: x["priority"], reverse=True)
        self._save()
        return {"status": "pushed"}
    
    def pop(self):
        if self.data["queue"]:
            item = self.data["queue"].pop(0)
            self._save()
            return item
        return None


if __name__ == "__main__":
    import sys
    q = SchedulerQueue()
    if len(sys.argv) > 1:
        if sys.argv[1] == "push":
            print(json.dumps(q.push(sys.argv[2], int(sys.argv[3] or 0))))
        elif sys.argv[1] == "pop":
            print(json.dumps(q.pop()))