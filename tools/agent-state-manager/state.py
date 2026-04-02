#!/usr/bin/env python3
"""
Agent State Manager
Manages agent state.
"""

import json
from datetime import datetime
from pathlib import Path

class StateManager:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "agent_state.json"
        self.state = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.state = json.load(f)
    
    def set(self, agent_id, state):
        self.state[agent_id] = {"state": state, "updated": datetime.utcnow().isoformat()}
        with open(self.file, 'w') as f:
            json.dump(self.state, f)
        return {"status": "set"}
    
    def get(self, agent_id):
        return self.state.get(agent_id, {})


if __name__ == "__main__":
    import sys
    s = StateManager()
    if len(sys.argv) > 2:
        print(json.dumps(s.set(sys.argv[1], sys.argv[2])))
    elif len(sys.argv) > 1:
        print(json.dumps(s.get(sys.argv[1])))