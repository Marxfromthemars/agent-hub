#!/usr/bin/env python3
"""
Agent Task Prioritizer
Task prioritizer.
"""

import json
from pathlib import Path

class TaskPrioritizer:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "task_prioritizer.json"
        self.priorities = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.priorities = json.load(f)
    
    def prioritize(self, task, priority):
        self.priorities[task] = priority
        with open(self.file, 'w') as f:
            json.dump(self.priorities, f)


if __name__ == "__main__":
    import sys
    t = TaskPrioritizer()
    if len(sys.argv) > 2:
        t.prioritize(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "prioritized"}))