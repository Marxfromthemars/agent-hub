#!/usr/bin/env python3
"""
Agent Worker Service
Worker service.
"""

import json
from pathlib import Path

class WorkerService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "worker_service_v4.json"
        self.workers = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.workers = json.load(f)
    
    def work(self, name, task):
        self.workers[name] = task
        with open(self.file, 'w') as f:
            json.dump(self.workers, f)


if __name__ == "__main__":
    import sys
    w = WorkerService()
    if len(sys.argv) > 2:
        w.work(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "working"}))