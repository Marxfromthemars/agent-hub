#!/usr/bin/env python3
"""
Agent Metric Store
Store metrics.
"""

import json
from datetime import datetime
from pathlib import Path

class MetricStore:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "metric_store.json"
        self.metrics = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.metrics = json.load(f)
    
    def store(self, name, value):
        self.metrics[name] = {"value": value, "ts": datetime.utcnow().isoformat()}
        with open(self.file, 'w') as f:
            json.dump(self.metrics, f)


if __name__ == "__main__":
    import sys
    m = MetricStore()
    if len(sys.argv) > 2:
        m.store(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "stored"}))