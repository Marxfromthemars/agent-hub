#!/usr/bin/env python3
"""
Agent Worker Service
Worker service.
"""

import json
from pathlib import Path

class WorkerService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "worker_service.json"
        self.workers = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.workers = json.load(f)
    
    def add(self, worker_id, status):
        self.workers[worker_id] = status
        with open(self.file, 'w') as f:
            json.dump(self.workers, f)


if __name__ == "__main__":
    import sys
    w = WorkerService()
    if len(sys.argv) > 2:
        w.add(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "added"}))