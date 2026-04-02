#!/usr/bin/env python3
"""
Agent Resource Monitor
Tracks and manages agent resource usage (CPU, memory, tokens, compute).
"""

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

import json
from datetime import datetime
from pathlib import Path

class ResourceMonitor:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.usage_file = self.data_dir / "resource_usage.json"
        self.usage = self._load_usage()
    
    def _load_usage(self):
        if self.usage_file.exists():
            with open(self.usage_file) as f:
                return json.load(f)
        return {"agents": {}, "system": {}}
    
    def _save_usage(self):
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage, f, indent=2)
    
    def record_agent_usage(self, agent_id, tokens_used=None, compute_seconds=None):
        """Record resource usage for an agent."""
        now = datetime.utcnow().isoformat()
        
        if agent_id not in self.usage["agents"]:
            self.usage["agents"][agent_id] = {
                "total_tokens": 0,
                "total_compute_seconds": 0,
                "records": []
            }
        
        record = {"timestamp": now}
        if tokens_used:
            self.usage["agents"][agent_id]["total_tokens"] += tokens_used
            record["tokens"] = tokens_used
        if compute_seconds:
            self.usage["agents"][agent_id]["total_compute_seconds"] += compute_seconds
            record["compute_seconds"] = compute_seconds
        
        self.usage["agents"][agent_id]["records"].append(record)
        # Keep last 1000 records
        self.usage["agents"][agent_id]["records"] = self.usage["agents"][agent_id]["records"][-1000:]
        
        self._save_usage()
        return {"status": "recorded", "agent_id": agent_id}
    
    def get_system_stats(self):
        """Get current system resource statistics."""
        if HAS_PSUTIL:
            return {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "timestamp": datetime.utcnow().isoformat()
            }
        return {
            "cpu_percent": "unavailable (psutil not installed)",
            "memory_percent": "unavailable",
            "disk_percent": "unavailable",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_agent_usage(self, agent_id):
        """Get usage stats for an agent."""
        if agent_id not in self.usage["agents"]:
            return {"status": "not_found"}
        
        agent = self.usage["agents"][agent_id]
        return {
            "agent_id": agent_id,
            "total_tokens": agent["total_tokens"],
            "total_compute_seconds": agent["total_compute_seconds"],
            "record_count": len(agent["records"]),
            "last_record": agent["records"][-1] if agent["records"] else None
        }
    
    def get_all_usage(self):
        """Get usage for all agents."""
        return {
            agent_id: self.get_agent_usage(agent_id)
            for agent_id in self.usage["agents"]
        }
    
    def get_platform_usage(self):
        """Get aggregate platform usage."""
        total_tokens = sum(a["total_tokens"] for a in self.usage["agents"].values())
        total_compute = sum(a["total_compute_seconds"] for a in self.usage["agents"].values())
        
        return {
            "total_agents": len(self.usage["agents"]),
            "total_tokens": total_tokens,
            "total_compute_seconds": total_compute,
            "system": self.get_system_stats()
        }


def main():
    import sys
    monitor = ResourceMonitor()
    
    if len(sys.argv) < 2:
        print("Agent Resource Monitor")
        print("Usage: agent-monitor.py <command> [args]")
        print("Commands:")
        print("  record <agent_id> [tokens] [compute_seconds]")
        print("  agent <agent_id>")
        print("  all")
        print("  system")
        print("  platform")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "record":
        if len(sys.argv) < 3:
            print("Usage: record <agent_id> [tokens] [compute_seconds]")
            return
        agent_id = sys.argv[2]
        tokens = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else None
        compute = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else None
        result = monitor.record_agent_usage(agent_id, tokens, compute)
        print(json.dumps(result, indent=2))
    
    elif cmd == "agent":
        if len(sys.argv) < 3:
            print("Usage: agent <agent_id>")
            return
        stats = monitor.get_agent_usage(sys.argv[2])
        print(json.dumps(stats, indent=2))
    
    elif cmd == "all":
        usage = monitor.get_all_usage()
        print(json.dumps(usage, indent=2))
    
    elif cmd == "system":
        stats = monitor.get_system_stats()
        print(json.dumps(stats, indent=2))
    
    elif cmd == "platform":
        stats = monitor.get_platform_usage()
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()