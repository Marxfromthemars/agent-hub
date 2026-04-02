#!/usr/bin/env python3
"""
Agent Task Service
Task service.
"""

import json
from pathlib import Path

class TaskService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "task_service_v2.json"
        self.tasks = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.tasks = json.load(f)
    
    def task(self, task_id, data):
        self.tasks[task_id] = data
        with open(self.file, 'w') as f:
            json.dump(self.tasks, f)


if __name__ == "__main__":
    import sys
    t = TaskService()
    if len(sys.argv) > 2:
        t.task(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "task_set"}))