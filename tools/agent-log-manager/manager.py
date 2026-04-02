#!/usr/bin/env python3
"""
Agent Log Manager
Manage logs.
"""

import json
from datetime import datetime
from pathlib import Path

class LogManager:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "log_manager.json"
        self.logs = []
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.logs = json.load(f)
    
    def log(self, msg):
        self.logs.append({"msg": msg, "ts": datetime.utcnow().isoformat()})
        with open(self.file, 'w') as f:
            json.dump(self.logs, f)


if __name__ == "__main__":
    import sys
    l = LogManager()
    if len(sys.argv) > 1:
        l.log(sys.argv[1])
        print(json.dumps({"status": "logged"}))