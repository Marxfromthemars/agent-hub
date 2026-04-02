#!/usr/bin/env python3
"""
Agent Handler Service
Handler service.
"""

import json
from pathlib import Path

class HandlerService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "handler_service_v2.json"
        self.handlers = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.handlers = json.load(f)
    
    def handle(self, event):
        self.handlers[event] = True
        with open(self.file, 'w') as f:
            json.dump(self.handlers, f)


if __name__ == "__main__":
    import sys
    h = HandlerService()
    if len(sys.argv) > 1:
        h.handle(sys.argv[1])
        print(json.dumps({"status": "handled"}))