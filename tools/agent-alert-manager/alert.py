#!/usr/bin/env python3
"""
Agent Alert Manager
Manages alerts for agent events.
"""

import json
from datetime import datetime
from pathlib import Path

class AlertManager:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.file = self.data_dir / "alerts.json"
        self.data = {"alerts": []}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.data = json.load(f)
    
    def _save(self):
        with open(self.file, 'w') as f:
            json.dump(self.data, f)
    
    def alert(self, level, msg):
        self.data["alerts"].append({"level": level, "msg": msg, "ts": datetime.utcnow().isoformat()})
        self._save()
        return {"status": "alerted"}


if __name__ == "__main__":
    import sys
    a = AlertManager()
    if len(sys.argv) > 2:
        print(json.dumps(a.alert(sys.argv[1], sys.argv[2])))