#!/usr/bin/env python3
"""
Agent Task Store
Task storage.
"""

import json
from pathlib import Path

class TaskStore:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "task_store.json"
        self.tasks = []
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.tasks = json.load(f)
    
    def add(self, task):
        self.tasks.append(task)
        with open(self.file, 'w') as f:
            json.dump(self.tasks, f)


if __name__ == "__main__":
    import sys
    t = TaskStore()
    if len(sys.argv) > 1:
        t.add(sys.argv[1])
        print(json.dumps({"status": "added"}))