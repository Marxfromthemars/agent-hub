#!/usr/bin/env python3
"""
Agent Task Manager
Simple task management.
"""

import json
from datetime import datetime
from pathlib import Path

class TaskManager:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "tasks_simple.json"
        self.tasks = []
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.tasks = json.load(f)
    
    def create(self, title):
        self.tasks.append({"title": title, "status": "pending", "ts": datetime.utcnow().isoformat()})
        with open(self.file, 'w') as f:
            json.dump(self.tasks, f)


if __name__ == "__main__":
    import sys
    t = TaskManager()
    if len(sys.argv) > 1:
        t.create(sys.argv[1])
        print(json.dumps({"status": "created"}))