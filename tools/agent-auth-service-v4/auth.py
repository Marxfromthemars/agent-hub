#!/usr/bin/env python3
"""
Agent Auth Service
Auth service.
"""

import json
from pathlib import Path

class AuthService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "auth_service_v4.json"
        self.auth = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.auth = json.load(f)
    
    def auth(self, user, token):
        self.auth[user] = token
        with open(self.file, 'w') as f:
            json.dump(self.auth, f)


if __name__ == "__main__":
    import sys
    a = AuthService()
    if len(sys.argv) > 2:
        a.auth(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "authenticated"}))