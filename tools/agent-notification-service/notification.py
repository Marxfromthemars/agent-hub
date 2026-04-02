#!/usr/bin/env python3
"""
Agent Notification Service
Notification service.
"""

import json
from pathlib import Path

class NotificationService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "notification_service.json"
        self.notifications = []
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.notifications = json.load(f)
    
    def notify(self, msg):
        self.notifications.append(msg)
        with open(self.file, 'w') as f:
            json.dump(self.notifications, f)


if __name__ == "__main__":
    import sys
    n = NotificationService()
    if len(sys.argv) > 1:
        n.notify(sys.argv[1])
        print(json.dumps({"status": "notified"}))