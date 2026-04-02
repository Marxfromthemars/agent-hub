#!/usr/bin/env python3
"""
Agent Scheduler Cron
Cron-like scheduler for agent tasks.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

class CronScheduler:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.crons_file = self.data_dir / "cron_schedules.json"
        self.crons = self._load_crons()
    
    def _load_crons(self):
        if self.crons_file.exists():
            with open(self.crons_file) as f:
                return json.load(f)
        return {"schedules": []}
    
    def _save_crons(self):
        with open(self.crons_file, 'w') as f:
            json.dump(self.crons, f, indent=2)
    
    def add(self, name, schedule, command):
        """Add a cron schedule."""
        schedule_entry = {
            "id": f"cron-{len(self.crons['schedules']) + 1}",
            "name": name,
            "schedule": schedule,
            "command": command,
            "enabled": True,
            "last_run": None,
            "next_run": self._calc_next_run(schedule),
            "created": datetime.utcnow().isoformat()
        }
        
        self.crons["schedules"].append(schedule_entry)
        self._save_crons()
        
        return {"status": "added", "cron_id": schedule_entry["id"]}
    
    def _calc_next_run(self, schedule):
        """Calculate next run time (simplified)."""
        # Simplified: if schedule contains "hourly", add 1 hour
        if "hourly" in schedule.lower():
            return (datetime.utcnow() + timedelta(hours=1)).isoformat()
        elif "daily" in schedule.lower():
            return (datetime.utcnow() + timedelta(days=1)).isoformat()
        return (datetime.utcnow() + timedelta(hours=24)).isoformat()
    
    def due(self):
        """Get schedules due for execution."""
        now = datetime.utcnow()
        due = []
        
        for cron in self.crons["schedules"]:
            if not cron.get("enabled", True):
                continue
            
            next_run = datetime.fromisoformat(cron["next_run"])
            if now >= next_run:
                due.append(cron)
        
        return due
    
    def mark_run(self, cron_id):
        """Mark a cron as run."""
        for cron in self.crons["schedules"]:
            if cron["id"] == cron_id:
                cron["last_run"] = datetime.utcnow().isoformat()
                cron["next_run"] = self._calc_next_run(cron["schedule"])
                self._save_crons()
                return {"status": "marked"}
        return {"error": "not found"}
    
    def list(self):
        """List all schedules."""
        return self.crons["schedules"]


def main():
    import sys
    cron = CronScheduler()
    
    if len(sys.argv) < 2:
        print("Agent Cron Scheduler")
        print("Usage: cron-scheduler.py <command> [args]")
        print("Commands:")
        print("  add <name> <schedule> <command>")
        print("  due")
        print("  mark <cron_id>")
        print("  list")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "add":
        if len(sys.argv) < 5:
            print("Usage: add <name> <schedule> <command>")
            return
        result = cron.add(sys.argv[2], sys.argv[3], sys.argv[4])
        print(json.dumps(result, indent=2))
    
    elif cmd == "due":
        result = cron.due()
        print(json.dumps(result, indent=2))
    
    elif cmd == "mark":
        if len(sys.argv) < 3:
            print("Usage: mark <cron_id>")
            return
        result = cron.mark_run(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "list":
        result = cron.list()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()