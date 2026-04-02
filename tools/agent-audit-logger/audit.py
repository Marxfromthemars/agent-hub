#!/usr/bin/env python3
"""
Agent Audit Logger
Comprehensive audit logging for agent activities.
"""

import json
from datetime import datetime
from pathlib import Path

class AuditLogger:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.log_file = self.data_dir / "audit_log.json"
        self.logs = self._load_logs()
    
    def _load_logs(self):
        if self.log_file.exists():
            with open(self.log_file) as f:
                return json.load(f)
        return {"logs": []}
    
    def _save_logs(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.logs, f, indent=2)
    
    def log(self, actor, action, target, result="success", details=None):
        """Log an audit event."""
        entry = {
            "id": len(self.logs["logs"]) + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "actor": actor,
            "action": action,
            "target": target,
            "result": result,  # success, failure, pending
            "details": details or {}
        }
        
        self.logs["logs"].append(entry)
        self.logs["logs"] = self.logs["logs"][-1000:]  # Keep last 1000
        self._save_logs()
        
        return {"status": "logged", "entry_id": entry["id"]}
    
    def query(self, actor=None, action=None, since_minutes=60):
        """Query audit logs."""
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(minutes=since_minutes)
        
        results = []
        for entry in self.logs["logs"]:
            if datetime.fromisoformat(entry["timestamp"]) > cutoff:
                if actor and entry["actor"] != actor:
                    continue
                if action and entry["action"] != action:
                    continue
                results.append(entry)
        
        return results
    
    def get_stats(self):
        """Get audit statistics."""
        logs = self.logs["logs"]
        
        by_actor = {}
        by_action = {}
        by_result = {"success": 0, "failure": 0, "pending": 0}
        
        for entry in logs:
            by_actor[entry["actor"]] = by_actor.get(entry["actor"], 0) + 1
            by_action[entry["action"]] = by_action.get(entry["action"], 0) + 1
            by_result[entry["result"]] = by_result.get(entry["result"], 0) + 1
        
        return {
            "total_entries": len(logs),
            "by_actor": by_actor,
            "by_action": by_action,
            "by_result": by_result
        }


def main():
    import sys
    logger = AuditLogger()
    
    if len(sys.argv) < 2:
        print("Agent Audit Logger")
        print("Usage: audit-logger.py <command> [args]")
        print("Commands:")
        print("  log <actor> <action> <target> [result] [details]")
        print("  query [actor] [action] [minutes]")
        print("  stats")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "log":
        if len(sys.argv) < 5:
            print("Usage: log <actor> <action> <target> [result] [details]")
            return
        result = sys.argv[4] if len(sys.argv) > 4 else "success"
        details = sys.argv[5] if len(sys.argv) > 5 else None
        result = logger.log(sys.argv[2], sys.argv[3], sys.argv[4], result, details)
        print(json.dumps(result, indent=2))
    
    elif cmd == "query":
        actor = sys.argv[2] if len(sys.argv) > 2 else None
        action = sys.argv[3] if len(sys.argv) > 3 else None
        minutes = int(sys.argv[4]) if len(sys.argv) > 4 else 60
        results = logger.query(actor, action, minutes)
        print(json.dumps(results, indent=2))
    
    elif cmd == "stats":
        result = logger.get_stats()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()