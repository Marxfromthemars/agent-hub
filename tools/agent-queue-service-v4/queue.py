#!/usr/bin/env python3
"""
Agent Queue Service
Queue service.
"""

import json
from pathlib import Path

class QueueService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "queue_service_v4.json"
        self.queue = []
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.queue = json.load(f)
    
    def enqueue(self, item):
        self.queue.append(item)
        with open(self.file, 'w') as f:
            json.dump(self.queue, f)


if __name__ == "__main__":
    import sys
    q = QueueService()
    if len(sys.argv) > 1:
        q.enqueue(sys.argv[1])
        print(json.dumps({"status": "enqueued"}))