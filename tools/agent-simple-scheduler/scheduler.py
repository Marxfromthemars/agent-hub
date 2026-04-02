#!/usr/bin/env python3
"""
Agent Task Scheduler
Simple task scheduler.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

class TaskScheduler:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "task_scheduler.json"
        self.scheduled = []
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.scheduled = json.load(f)
    
    def schedule(self, task, at):
        self.scheduled.append({"task": task, "at": at, "created": datetime.utcnow().isoformat()})
        with open(self.file, 'w') as f:
            json.dump(self.scheduled, f)


if __name__ == "__main__":
    import sys
    s = TaskScheduler()
    if len(sys.argv) > 2:
        s.schedule(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "scheduled"}))