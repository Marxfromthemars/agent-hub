#!/usr/bin/env python3
"""
Agent Event Handler
Handle agent events.
"""

import json
from datetime import datetime
from pathlib import Path

class EventHandler:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "events_handler.json"
        self.events = []
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.events = json.load(f)
    
    def handle(self, event_type, data):
        self.events.append({"type": event_type, "data": data, "ts": datetime.utcnow().isoformat()})
        with open(self.file, 'w') as f:
            json.dump(self.events, f)


if __name__ == "__main__":
    import sys
    h = EventHandler()
    if len(sys.argv) > 2:
        h.handle(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "handled"}))