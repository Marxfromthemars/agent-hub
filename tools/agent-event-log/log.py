#!/usr/bin/env python3
"""
Agent Event Log
Central event logging.
"""

import json
from datetime import datetime
from pathlib import Path

class EventLog:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "event_log.json"
        self.events = []
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.events = json.load(f)
    
    def log(self, event_type, data):
        self.events.append({"type": event_type, "data": data, "ts": datetime.utcnow().isoformat()})
        self.events[-1000:]
        with open(self.file, 'w') as f:
            json.dump(self.events, f)
        return {"status": "logged"}


if __name__ == "__main__":
    import sys
    e = EventLog()
    if len(sys.argv) > 2:
        print(json.dumps(e.log(sys.argv[1], sys.argv[2])))