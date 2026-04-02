#!/usr/bin/env python3
"""
Agent Log Aggregator
Centralized logging for agent operations.
"""

import json
from datetime import datetime
from pathlib import Path

class LogAggregator:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.logs_file = self.data_dir / "aggregated_logs.json"
        self.logs = self._load_logs()
    
    def _load_logs(self):
        if self.logs_file.exists():
            with open(self.logs_file) as f:
                return json.load(f)
        return {"logs": []}
    
    def _save_logs(self):
        with open(self.logs_file, 'w') as f:
            json.dump(self.logs, f, indent=2)
    
    def log(self, agent_id, level, message, metadata=None):
        """Log a message."""
        entry = {
            "id": len(self.logs["logs"]) + 1,
            "agent_id": agent_id,
            "level": level,  # debug, info, warning, error
            "message": message,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logs["logs"].append(entry)
        self.logs["logs"] = self.logs["logs"][-1000:]  # Keep last 1000
        self._save_logs()
        
        return {"status": "logged", "log_id": entry["id"]}
    
    def query(self, agent_id=None, level=None, limit=50):
        """Query logs."""
        results = self.logs["logs"]
        
        if agent_id:
            results = [l for l in results if l["agent_id"] == agent_id]
        if level:
            results = [l for l in results if l["level"] == level]
        
        return results[-limit:]
    
    def get_stats(self):
        """Get log statistics."""
        logs = self.logs["logs"]
        
        by_level = {"debug": 0, "info": 0, "warning": 0, "error": 0}
        by_agent = {}
        
        for log in logs:
            by_level[log["level"]] = by_level.get(log["level"], 0) + 1
            by_agent[log["agent_id"]] = by_agent.get(log["agent_id"], 0) + 1
        
        return {
            "total": len(logs),
            "by_level": by_level,
            "by_agent": by_agent
        }


def main():
    import sys
    aggregator = LogAggregator()
    
    if len(sys.argv) < 2:
        print("Agent Log Aggregator")
        print("Usage: log-aggregator.py <command> [args]")
        print("Commands:")
        print("  log <agent_id> <level> <message>")
        print("  query [agent_id] [level] [limit]")
        print("  stats")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "log":
        if len(sys.argv) < 5:
            print("Usage: log <agent_id> <level> <message>")
            return
        result = aggregator.log(sys.argv[2], sys.argv[3], " ".join(sys.argv[4:]))
        print(json.dumps(result, indent=2))
    
    elif cmd == "query":
        agent_id = sys.argv[2] if len(sys.argv) > 2 else None
        level = sys.argv[3] if len(sys.argv) > 3 else None
        limit = int(sys.argv[4]) if len(sys.argv) > 4 else 50
        result = aggregator.query(agent_id, level, limit)
        print(json.dumps(result, indent=2))
    
    elif cmd == "stats":
        result = aggregator.get_stats()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()