#!/usr/bin/env python3
"""
Agent Status Monitor
Monitor agent status.
"""

import json
from datetime import datetime
from pathlib import Path

class StatusMonitor:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "status.json"
        self.status = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.status = json.load(f)
    
    def update(self, agent_id, status):
        self.status[agent_id] = {"status": status, "ts": datetime.utcnow().isoformat()}
        with open(self.file, 'w') as f:
            json.dump(self.status, f)


if __name__ == "__main__":
    import sys
    s = StatusMonitor()
    if len(sys.argv) > 2:
        s.update(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "updated"}))