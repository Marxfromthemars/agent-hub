#!/usr/bin/env python3
"""
Agent Metrics Collector
Collects agent metrics.
"""

import json
from datetime import datetime
from pathlib import Path

class MetricsCollector:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.file = self.data_dir / "metrics.json"
        self.data = {"metrics": []}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.data = json.load(f)
    
    def _save(self):
        with open(self.file, 'w') as f:
            json.dump(self.data, f)
    
    def collect(self, agent_id, metric, value):
        self.data["metrics"].append({
            "agent": agent_id,
            "metric": metric,
            "value": value,
            "ts": datetime.utcnow().isoformat()
        })
        self._save()
        return {"status": "collected"}


if __name__ == "__main__":
    import sys
    m = MetricsCollector()
    if len(sys.argv) > 3:
        print(json.dumps(m.collect(sys.argv[1], sys.argv[2], float(sys.argv[3]))))