#!/usr/bin/env python3
"""
Agent Metrics Service
Metrics service.
"""

import json
from pathlib import Path

class MetricsService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "metrics_service.json"
        self.metrics = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.metrics = json.load(f)
    
    def metric(self, name, value):
        self.metrics[name] = value
        with open(self.file, 'w') as f:
            json.dump(self.metrics, f)


if __name__ == "__main__":
    import sys
    m = MetricsService()
    if len(sys.argv) > 2:
        m.metric(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "metric_set"}))