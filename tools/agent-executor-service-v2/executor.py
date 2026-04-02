#!/usr/bin/env python3
"""
Agent Executor Service
Executor service.
"""

import json
from pathlib import Path

class ExecutorService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "executor_service_v2.json"
        self.executors = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.executors = json.load(f)
    
    def execute(self, name, cmd):
        self.executors[name] = cmd
        with open(self.file, 'w') as f:
            json.dump(self.executors, f)


if __name__ == "__main__":
    import sys
    e = ExecutorService()
    if len(sys.argv) > 2:
        e.execute(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "executed"}))