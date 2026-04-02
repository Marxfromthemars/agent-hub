#!/usr/bin/env python3
"""
Agent Queue Monitor
Monitor queues.
"""

import json
from pathlib import Path

class QueueMonitor:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "queue_monitor.json"
        self.queues = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.queues = json.load(f)
    
    def add(self, queue_name):
        self.queues[queue_name] = self.queues.get(queue_name, 0) + 1
        with open(self.file, 'w') as f:
            json.dump(self.queues, f)


if __name__ == "__main__":
    import sys
    q = QueueMonitor()
    if len(sys.argv) > 1:
        q.add(sys.argv[1])
        print(json.dumps({"status": "added"}))