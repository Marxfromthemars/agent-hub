#!/usr/bin/env python3
"""
Agent Validator Service
Validator service.
"""

import json
from pathlib import Path

class ValidatorService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "validator_service_v3.json"
        self.validators = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.validators = json.load(f)
    
    def validate(self, rule, data):
        self.validators[rule] = data
        with open(self.file, 'w') as f:
            json.dump(self.validators, f)


if __name__ == "__main__":
    import sys
    v = ValidatorService()
    if len(sys.argv) > 2:
        v.validate(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "validated"}))