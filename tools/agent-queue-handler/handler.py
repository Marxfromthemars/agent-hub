#!/usr/bin/env python3
"""
Agent Queue Handler
Queue handler service.
"""

import json
from pathlib import Path

class QueueHandler:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "queue_handler.json"
        self.queues = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.queues = json.load(f)
    
    def handle(self, name):
        self.queues[name] = self.queues.get(name, 0) + 1
        with open(self.file, 'w') as f:
            json.dump(self.queues, f)


if __name__ == "__main__":
    import sys
    q = QueueHandler()
    if len(sys.argv) > 1:
        q.handle(sys.argv[1])
        print(json.dumps({"status": "handled"}))