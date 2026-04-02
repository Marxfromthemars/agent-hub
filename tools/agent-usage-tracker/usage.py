#!/usr/bin/env python3
"""
Agent Usage Tracker
Tracks API and resource usage for billing/analytics.
"""

import json
from datetime import datetime
from pathlib import Path

class UsageTracker:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.usage_file = self.data_dir / "usage_tracking.json"
        self.usage = self._load_usage()
    
    def _load_usage(self):
        if self.usage_file.exists():
            with open(self.usage_file) as f:
                return json.load(f)
        return {"records": [], "by_agent": {}, "by_day": {}}
    
    def _save_usage(self):
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage, f, indent=2)
    
    def record(self, agent_id, resource_type, amount, cost=None):
        """Record resource usage."""
        record = {
            "id": f"usage-{len(self.usage['records']) + 1}",
            "agent_id": agent_id,
            "resource_type": resource_type,
            "amount": amount,
            "cost": cost or amount * 0.01,  # Default $0.01 per unit
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.usage["records"].append(record)
        
        # Aggregate by agent
        if agent_id not in self.usage["by_agent"]:
            self.usage["by_agent"][agent_id] = {"total_cost": 0, "resources": {}}
        
        self.usage["by_agent"][agent_id]["total_cost"] += record["cost"]
        
        if resource_type not in self.usage["by_agent"][agent_id]["resources"]:
            self.usage["by_agent"][agent_id]["resources"][resource_type] = 0
        self.usage["by_agent"][agent_id]["resources"][resource_type] += amount
        
        # Aggregate by day
        day = datetime.utcnow().strftime("%Y-%m-%d")
        if day not in self.usage["by_day"]:
            self.usage["by_day"][day] = {"total_cost": 0, "requests": 0}
        self.usage["by_day"][day]["total_cost"] += record["cost"]
        self.usage["by_day"][day]["requests"] += 1
        
        self._save_usage()
        
        return {"status": "recorded", "cost": record["cost"]}
    
    def get_agent_usage(self, agent_id):
        """Get usage for an agent."""
        return self.usage["by_agent"].get(agent_id, {})
    
    def get_day_usage(self, day=None):
        """Get usage for a day."""
        day = day or datetime.utcnow().strftime("%Y-%m-%d")
        return self.usage["by_day"].get(day, {})
    
    def get_summary(self):
        """Get usage summary."""
        return {
            "total_records": len(self.usage["records"]),
            "total_agents": len(self.usage["by_agent"]),
            "total_cost": sum(a["total_cost"] for a in self.usage["by_agent"].values()),
            "days_tracked": len(self.usage["by_day"])
        }


def main():
    import sys
    tracker = UsageTracker()
    
    if len(sys.argv) < 2:
        print("Agent Usage Tracker")
        print("Usage: usage-tracker.py <command> [args]")
        print("Commands:")
        print("  record <agent_id> <resource_type> <amount> [cost]")
        print("  agent <agent_id>")
        print("  day [date]")
        print("  summary")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "record":
        if len(sys.argv) < 5:
            print("Usage: record <agent_id> <resource_type> <amount> [cost]")
            return
        cost = float(sys.argv[5]) if len(sys.argv) > 5 else None
        result = tracker.record(sys.argv[2], sys.argv[3], float(sys.argv[4]), cost)
        print(json.dumps(result, indent=2))
    
    elif cmd == "agent":
        if len(sys.argv) < 3:
            print("Usage: agent <agent_id>")
            return
        result = tracker.get_agent_usage(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "day":
        day = sys.argv[2] if len(sys.argv) > 2 else None
        result = tracker.get_day_usage(day)
        print(json.dumps(result, indent=2))
    
    elif cmd == "summary":
        result = tracker.get_summary()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()