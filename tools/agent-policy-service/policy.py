#!/usr/bin/env python3
"""
Agent Policy Service
Policy service.
"""

import json
from pathlib import Path

class PolicyService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "policy_service.json"
        self.policies = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.policies = json.load(f)
    
    def add(self, name, policy):
        self.policies[name] = policy
        with open(self.file, 'w') as f:
            json.dump(self.policies, f)


if __name__ == "__main__":
    import sys
    p = PolicyService()
    if len(sys.argv) > 2:
        p.add(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "added"}))