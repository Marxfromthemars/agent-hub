#!/usr/bin/env python3
"""
Agent Report Service
Report service.
"""

import json
from pathlib import Path

class ReportService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "report_service.json"
        self.reports = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.reports = json.load(f)
    
    def report(self, name, data):
        self.reports[name] = data
        with open(self.file, 'w') as f:
            json.dump(self.reports, f)


if __name__ == "__main__":
    import sys
    r = ReportService()
    if len(sys.argv) > 2:
        r.report(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "reported"}))