#!/usr/bin/env python3
"""
Agent Alerting Service
Alerting service.
"""

import json
from pathlib import Path

class AlertingService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "alerting_service_v2.json"
        self.alerts = []
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.alerts = json.load(f)
    
    def alert(self, msg):
        self.alerts.append(msg)
        with open(self.file, 'w') as f:
            json.dump(self.alerts, f)


if __name__ == "__main__":
    import sys
    a = AlertingService()
    if len(sys.argv) > 1:
        a.alert(sys.argv[1])
        print(json.dumps({"status": "alerted"}))