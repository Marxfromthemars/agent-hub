#!/usr/bin/env python3
"""
Agent Event Queue
Event queue.
"""

import json
from pathlib import Path

class EventQueue:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "event_queue.json"
        self.queue = []
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.queue = json.load(f)
    
    def push(self, event):
        self.queue.append(event)
        with open(self.file, 'w') as f:
            json.dump(self.queue, f)


if __name__ == "__main__":
    import sys
    e = EventQueue()
    if len(sys.argv) > 1:
        e.push(sys.argv[1])
        print(json.dumps({"status": "pushed"}))