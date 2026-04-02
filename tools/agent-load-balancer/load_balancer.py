#!/usr/bin/env python3
"""
Agent Load Balancer
Load balancer.
"""

import json
from pathlib import Path

class LoadBalancer:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "load_balancer.json"
        self.balancers = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.balancers = json.load(f)
    
    def balance(self, target, weight):
        self.balancers[target] = weight
        with open(self.file, 'w') as f:
            json.dump(self.balancers, f)


if __name__ == "__main__":
    import sys
    l = LoadBalancer()
    if len(sys.argv) > 2:
        l.balance(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "balanced"}))