#!/usr/bin/env python3
"""
Agent Rule Engine
Rule engine service.
"""

import json
from pathlib import Path

class RuleEngine:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "rule_engine.json"
        self.rules = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.rules = json.load(f)
    
    def add_rule(self, name, rule):
        self.rules[name] = rule
        with open(self.file, 'w') as f:
            json.dump(self.rules, f)


if __name__ == "__main__":
    import sys
    r = RuleEngine()
    if len(sys.argv) > 2:
        r.add_rule(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "rule_added"}))