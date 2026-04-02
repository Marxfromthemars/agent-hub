#!/usr/bin/env python3
"""
Agent Message Queue
Message queue for agents.
"""

import json
from datetime import datetime
from pathlib import Path

class MessageQueue:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "msg_queue.json"
        self.queue = []
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.queue = json.load(f)
    
    def enqueue(self, msg, to):
        self.queue.append({"msg": msg, "to": to, "ts": datetime.utcnow().isoformat()})
        with open(self.file, 'w') as f:
            json.dump(self.queue, f)
        return {"status": "queued"}
    
    def dequeue(self, agent_id):
        for i, m in enumerate(self.queue):
            if m["to"] == agent_id:
                self.queue.pop(i)
                with open(self.file, 'w') as f:
                    json.dump(self.queue, f)
                return m
        return None


if __name__ == "__main__":
    import sys
    q = MessageQueue()
    if len(sys.argv) > 2 and sys.argv[1] == "enqueue":
        print(json.dumps(q.enqueue(sys.argv[2], sys.argv[3])))