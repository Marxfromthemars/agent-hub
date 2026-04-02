#!/usr/bin/env python3
"""
Agent Event Store
Event storage.
"""

import json
from datetime import datetime
from pathlib import Path

class EventStore:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "event_store.json"
        self.events = []
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.events = json.load(f)
    
    def store(self, event):
        self.events.append({"event": event, "ts": datetime.utcnow().isoformat()})
        with open(self.file, 'w') as f:
            json.dump(self.events, f)


if __name__ == "__main__":
    import sys
    e = EventStore()
    if len(sys.argv) > 1:
        e.store(sys.argv[1])
        print(json.dumps({"status": "stored"}))