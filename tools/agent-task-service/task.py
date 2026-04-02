#!/usr/bin/env python3
"""
Agent Task Service
Task service.
"""

import json
from pathlib import Path

class TaskService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "task_service.json"
        self.tasks = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.tasks = json.load(f)
    
    def submit(self, task_id, task):
        self.tasks[task_id] = task
        with open(self.file, 'w') as f:
            json.dump(self.tasks, f)


if __name__ == "__main__":
    import sys
    t = TaskService()
    if len(sys.argv) > 2:
        t.submit(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "submitted"}))