#!/usr/bin/env python3
"""
Agent Session Service
Session service.
"""

import json
from pathlib import Path

class SessionService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "session_service_v2.json"
        self.sessions = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.sessions = json.load(f)
    
    def session(self, user, token):
        self.sessions[user] = token
        with open(self.file, 'w') as f:
            json.dump(self.sessions, f)


if __name__ == "__main__":
    import sys
    s = SessionService()
    if len(sys.argv) > 2:
        s.session(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "session_created"}))