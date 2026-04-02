#!/usr/bin/env python3
"""
Agent Verifier Service
Verifier service.
"""

import json
from pathlib import Path

class VerifierService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "verifier_service_v4.json"
        self.verifiers = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.verifiers = json.load(f)
    
    def verify(self, item, result):
        self.verifiers[item] = result
        with open(self.file, 'w') as f:
            json.dump(self.verifiers, f)


if __name__ == "__main__":
    import sys
    v = VerifierService()
    if len(sys.argv) > 2:
        v.verify(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "verified"}))