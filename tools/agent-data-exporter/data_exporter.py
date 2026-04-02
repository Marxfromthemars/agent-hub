#!/usr/bin/env python3
"""
Agent Data Exporter
Data exporter.
"""

import json
from pathlib import Path

class DataExporter:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "data_exporter.json"
        self.exports = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.exports = json.load(f)
    
    def export(self, name, data):
        self.exports[name] = data
        with open(self.file, 'w') as f:
            json.dump(self.exports, f)


if __name__ == "__main__":
    import sys
    d = DataExporter()
    if len(sys.argv) > 2:
        d.export(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "exported"}))