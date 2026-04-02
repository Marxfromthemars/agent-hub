#!/usr/bin/env python3
"""
Agent Error Handler
Error handler.
"""

import json
from pathlib import Path

class ErrorHandler:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "error_handler.json"
        self.errors = []
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.errors = json.load(f)
    
    def error(self, msg):
        self.errors.append(msg)
        with open(self.file, 'w') as f:
            json.dump(self.errors, f)


if __name__ == "__main__":
    import sys
    e = ErrorHandler()
    if len(sys.argv) > 1:
        e.error(sys.argv[1])
        print(json.dumps({"status": "error_handled"}))