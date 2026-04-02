#!/usr/bin/env python3
"""
Agent Profile Manager
Manage agent profiles.
"""

import json
from pathlib import Path

class ProfileManager:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "profile_manager.json"
        self.profiles = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.profiles = json.load(f)
    
    def save(self, agent_id, profile):
        self.profiles[agent_id] = profile
        with open(self.file, 'w') as f:
            json.dump(self.profiles, f)


if __name__ == "__main__":
    import sys
    p = ProfileManager()
    if len(sys.argv) > 2:
        p.save(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "saved"}))