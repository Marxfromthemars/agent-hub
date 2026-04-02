#!/usr/bin/env python3
"""
Agent Security Service
Security service.
"""

import json
from pathlib import Path

class SecurityService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "security_service.json"
        self.security = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.security = json.load(f)
    
    def secure(self, item):
        self.security[item] = True
        with open(self.file, 'w') as f:
            json.dump(self.security, f)


if __name__ == "__main__":
    import sys
    s = SecurityService()
    if len(sys.argv) > 1:
        s.secure(sys.argv[1])
        print(json.dumps({"status": "secured"}))