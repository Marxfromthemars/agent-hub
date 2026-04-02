#!/usr/bin/env python3
"""
Agent Compliance Service
Compliance service.
"""

import json
from pathlib import Path

class ComplianceService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "compliance_service_v2.json"
        self.compliance = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.compliance = json.load(f)
    
    def comply(self, item):
        self.compliance[item] = True
        with open(self.file, 'w') as f:
            json.dump(self.compliance, f)


if __name__ == "__main__":
    import sys
    c = ComplianceService()
    if len(sys.argv) > 1:
        c.comply(sys.argv[1])
        print(json.dumps({"status": "compliant"}))