#!/usr/bin/env python3
"""
Agent Rule Engine Service
Rule engine service.
"""

import json
from pathlib import Path

class RuleEngineService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "rule_engine_service.json"
        self.rules = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.rules = json.load(f)
    
    def rule(self, name, rule):
        self.rules[name] = rule
        with open(self.file, 'w') as f:
            json.dump(self.rules, f)


if __name__ == "__main__":
    import sys
    r = RuleEngineService()
    if len(sys.argv) > 2:
        r.rule(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "rule_set"}))