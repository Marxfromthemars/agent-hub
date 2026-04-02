#!/usr/bin/env python3
"""
Agent Session Manager
Manage agent sessions.
"""

import json
from datetime import datetime
from pathlib import Path

class SessionManager:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "sessions.json"
        self.sessions = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.sessions = json.load(f)
    
    def create(self, agent_id):
        self.sessions[agent_id] = {"started": datetime.utcnow().isoformat()}
        with open(self.file, 'w') as f:
            json.dump(self.sessions, f)


if __name__ == "__main__":
    import sys
    s = SessionManager()
    if len(sys.argv) > 1:
        s.create(sys.argv[1])
        print(json.dumps({"status": "created"}))