#!/usr/bin/env python3
"""
Agent Health Check
Check agent health status.
"""

import json
from datetime import datetime
from pathlib import Path

class HealthCheck:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.file = self.data_dir / "health.json"
        self.data = {"checks": []}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.data = json.load(f)
    
    def _save(self):
        with open(self.file, 'w') as f:
            json.dump(self.data, f)
    
    def check(self, agent_id, status="healthy"):
        check = {"agent": agent_id, "status": status, "ts": datetime.utcnow().isoformat()}
        self.data["checks"].append(check)
        self._save()
        return check


if __name__ == "__main__":
    import sys
    h = HealthCheck()
    print(json.dumps(h.check(sys.argv[1] if len(sys.argv) > 1 else "marxagent")))