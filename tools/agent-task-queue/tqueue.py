#!/usr/bin/env python3
"""
Agent Task Queue
Simple task queue.
"""

import json
from datetime import datetime
from pathlib import Path

class TaskQueue:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "task_queue.json"
        self.tasks = []
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.tasks = json.load(f)
    
    def add(self, task):
        self.tasks.append({"task": task, "ts": datetime.utcnow().isoformat()})
        with open(self.file, 'w') as f:
            json.dump(self.tasks, f)
        return {"status": "added"}


if __name__ == "__main__":
    import sys
    t = TaskQueue()
    if len(sys.argv) > 1:
        print(json.dumps(t.add(sys.argv[1])))