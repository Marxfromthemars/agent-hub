#!/usr/bin/env python3
"""
Agent Tracer Service
Tracer service.
"""

import json
from pathlib import Path

class TracerService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "tracer_service.json"
        self.traces = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.traces = json.load(f)
    
    def trace(self, name, data):
        self.traces[name] = data
        with open(self.file, 'w') as f:
            json.dump(self.traces, f)


if __name__ == "__main__":
    import sys
    t = TracerService()
    if len(sys.argv) > 2:
        t.trace(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "traced"}))