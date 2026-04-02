#!/usr/bin/env python3
"""
Agent Token Manager
Token management.
"""

import json
from pathlib import Path

class TokenManager:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "token_manager.json"
        self.tokens = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.tokens = json.load(f)
    
    def add(self, agent_id, token):
        self.tokens[agent_id] = token
        with open(self.file, 'w') as f:
            json.dump(self.tokens, f)


if __name__ == "__main__":
    import sys
    t = TokenManager()
    if len(sys.argv) > 2:
        t.add(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "added"}))