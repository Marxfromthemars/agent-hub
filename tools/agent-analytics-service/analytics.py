#!/usr/bin/env python3
"""
Agent Analytics Service
Analytics service.
"""

import json
from pathlib import Path

class AnalyticsService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "analytics_service.json"
        self.data = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.data = json.load(f)
    
    def track(self, metric, value):
        self.data[metric] = value
        with open(self.file, 'w') as f:
            json.dump(self.data, f)


if __name__ == "__main__":
    import sys
    a = AnalyticsService()
    if len(sys.argv) > 2:
        a.track(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "tracked"}))