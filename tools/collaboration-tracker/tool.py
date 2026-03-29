#!/usr/bin/env python3
"""
Collaboration Tracker - Track agent interactions and outcomes
"""
import json
from datetime import datetime
from pathlib import Path

class CollaborationTracker:
    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir or "data/collaboration")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.collaborations_file = self.data_dir / "collaborations.json"
        self.load()
    
    def load(self):
        if self.collaborations_file.exists():
            with open(self.collaborations_file) as f:
                self.collaborations = json.load(f)
        else:
            self.collaborations = []
    
    def save(self):
        with open(self.collaborations_file, 'w') as f:
            json.dump(self.collaborations, f, indent=2)
    
    def track(self, agent1, agent2, task, outcome, value=0):
        """Track a collaboration between two agents"""
        collab = {
            "id": len(self.collaborations) + 1,
            "agent1": agent1,
            "agent2": agent2,
            "task": task,
            "outcome": outcome,
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.collaborations.append(collab)
        self.save()
        return collab
    
    def get_stats(self, agent_id=None):
        """Get collaboration statistics"""
        if agent_id:
            filtered = [c for c in self.collaborations if c["agent1"] == agent_id or c["agent2"] == agent_id]
        else:
            filtered = self.collaborations
        
        return {
            "total": len(filtered),
            "successful": sum(1 for c in filtered if c["outcome"] == "success"),
            "total_value": sum(c["value"] for c in filtered)
        }

if __name__ == "__main__":
    t = CollaborationTracker()
    t.track("marxagent", "builder", "build-platform", "success", 100)
    t.track("marxagent", "researcher", "write-paper", "success", 50)
    stats = t.get_stats()
    print(f"Collaboration stats: {stats}")
