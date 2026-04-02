#!/usr/bin/env python3
"""
Agent Notification Queue
Queue for notifications.
"""

import json
from datetime import datetime
from pathlib import Path

class NotificationQueue:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "notifications_queue.json"
        self.queue = []
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.queue = json.load(f)
    
    def notify(self, agent_id, msg):
        self.queue.append({"agent": agent_id, "msg": msg, "ts": datetime.utcnow().isoformat()})
        with open(self.file, 'w') as f:
            json.dump(self.queue, f)


if __name__ == "__main__":
    import sys
    n = NotificationQueue()
    if len(sys.argv) > 2:
        n.notify(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "queued"}))