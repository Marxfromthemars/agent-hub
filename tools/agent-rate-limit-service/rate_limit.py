#!/usr/bin/env python3
"""
Agent Rate Limit Service
Rate limit service.
"""

import json
from pathlib import Path

class RateLimitService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "rate_limit_service.json"
        self.limits = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.limits = json.load(f)
    
    def limit(self, user, limit):
        self.limits[user] = limit
        with open(self.file, 'w') as f:
            json.dump(self.limits, f)


if __name__ == "__main__":
    import sys
    r = RateLimitService()
    if len(sys.argv) > 2:
        r.limit(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "limited"}))