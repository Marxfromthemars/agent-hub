#!/usr/bin/env python3
"""
Agent Handler Service
Handler service.
"""

import json
from pathlib import Path

class HandlerService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "handler_service_v4.json"
        self.handlers = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.handlers = json.load(f)
    
    def handle(self, event, handler):
        self.handlers[event] = handler
        with open(self.file, 'w') as f:
            json.dump(self.handlers, f)


if __name__ == "__main__":
    import sys
    h = HandlerService()
    if len(sys.argv) > 2:
        h.handle(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "handled"}))