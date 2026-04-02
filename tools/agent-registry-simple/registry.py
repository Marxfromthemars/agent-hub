#!/usr/bin/env python3
"""
Agent Registry
Agent registration.
"""

import json
from datetime import datetime
from pathlib import Path

class AgentRegistry:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "registry.json"
        self.agents = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.agents = json.load(f)
    
    def register(self, agent_id, name, caps):
        self.agents[agent_id] = {"name": name, "caps": caps, "ts": datetime.utcnow().isoformat()}
        with open(self.file, 'w') as f:
            json.dump(self.agents, f)


if __name__ == "__main__":
    import sys
    r = AgentRegistry()
    if len(sys.argv) > 3:
        r.register(sys.argv[1], sys.argv[2], sys.argv[3].split(","))
        print(json.dumps({"status": "registered"}))