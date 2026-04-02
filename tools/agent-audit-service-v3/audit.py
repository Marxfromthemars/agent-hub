#!/usr/bin/env python3
"""
Agent Audit Service
Audit service.
"""

import json
from pathlib import Path

class AuditService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "audit_service_v3.json"
        self.audits = []
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.audits = json.load(f)
    
    def audit(self, action):
        self.audits.append(action)
        with open(self.file, 'w') as f:
            json.dump(self.audits, f)


if __name__ == "__main__":
    import sys
    a = AuditService()
    if len(sys.argv) > 1:
        a.audit(sys.argv[1])
        print(json.dumps({"status": "audited"}))