#!/usr/bin/env python3
"""
Agent Watch List
Watch list for agents.
"""

import json
from pathlib import Path

class WatchList:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "watch_list.json"
        self.watch = []
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.watch = json.load(f)
    
    def add(self, item):
        if item not in self.watch:
            self.watch.append(item)
            with open(self.file, 'w') as f:
                json.dump(self.watch, f)


if __name__ == "__main__":
    import sys
    w = WatchList()
    if len(sys.argv) > 1:
        w.add(sys.argv[1])
        print(json.dumps({"status": "added"}))