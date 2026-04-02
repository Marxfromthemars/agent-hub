#!/usr/bin/env python3
"""
Agent Task Automation
Automates recurring tasks based on triggers and schedules.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

class TaskAutomator:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.automations_file = self.data_dir / "task_automations.json"
        self.executions_file = self.data_dir / "automation_executions.json"
        self.automations = self._load_automations()
        self.executions = self._load_executions()
    
    def _load_automations(self):
        if self.automations_file.exists():
            with open(self.automations_file) as f:
                return json.load(f)
        return {"automations": []}
    
    def _load_executions(self):
        if self.executions_file.exists():
            with open(self.executions_file) as f:
                return json.load(f)
        return {"executions": []}
    
    def _save_automations(self):
        with open(self.automations_file, 'w') as f:
            json.dump(self.automations, f, indent=2)
    
    def _save_executions(self):
        with open(self.executions_file, 'w') as f:
            json.dump(self.executions, f, indent=2)
    
    def create_automation(self, name, trigger_type, trigger_config, action):
        """Create a new automation."""
        automation = {
            "id": f"auto-{len(self.automations['automations']) + 1}",
            "name": name,
            "trigger_type": trigger_type,  # schedule, event, condition
            "trigger_config": trigger_config,
            "action": action,
            "enabled": True,
            "created": datetime.utcnow().isoformat(),
            "last_run": None,
            "run_count": 0
        }
        
        self.automations["automations"].append(automation)
        self._save_automations()
        
        return {"status": "created", "automation_id": automation["id"]}
    
    def execute_automation(self, automation_id):
        """Execute an automation."""
        for automation in self.automations["automations"]:
            if automation["id"] == automation_id:
                execution = {
                    "id": f"exec-{len(self.executions['executions']) + 1}",
                    "automation_id": automation_id,
                    "automation_name": automation["name"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "running",
                    "result": None
                }
                
                self.executions["executions"].append(execution)
                
                # Simulate execution
                execution["status"] = "completed"
                execution["result"] = {"executed": True, "action": automation["action"]}
                
                automation["last_run"] = datetime.utcnow().isoformat()
                automation["run_count"] += 1
                
                self._save_automations()
                self._save_executions()
                
                return {"status": "executed", "execution": execution}
        
        return {"status": "not_found"}
    
    def check_scheduled(self):
        """Check and execute scheduled automations."""
        now = datetime.utcnow()
        executed = []
        
        for automation in self.automations["automations"]:
            if not automation.get("enabled", True):
                continue
            
            if automation["trigger_type"] == "schedule":
                config = automation["trigger_config"]
                interval_minutes = config.get("interval_minutes", 60)
                
                last_run = automation.get("last_run")
                if last_run:
                    last_dt = datetime.fromisoformat(last_run)
                    if (now - last_dt).total_seconds() / 60 >= interval_minutes:
                        result = self.execute_automation(automation["id"])
                        executed.append(result)
        
        return {"checked": len(self.automations["automations"]), "executed": len(executed)}
    
    def toggle_automation(self, automation_id, enabled):
        """Enable or disable an automation."""
        for automation in self.automations["automations"]:
            if automation["id"] == automation_id:
                automation["enabled"] = enabled
                self._save_automations()
                return {"status": "updated", "enabled": enabled}
        return {"status": "not_found"}
    
    def get_automations(self):
        """Get all automations."""
        return self.automations["automations"]
    
    def get_executions(self, limit=20):
        """Get recent executions."""
        return self.executions["executions"][-limit:]
    
    def get_stats(self):
        """Get automation statistics."""
        autos = self.automations["automations"]
        enabled = sum(1 for a in autos if a.get("enabled", True))
        
        return {
            "total": len(autos),
            "enabled": enabled,
            "disabled": len(autos) - enabled,
            "total_runs": sum(a.get("run_count", 0) for a in autos),
            "recent_executions": len(self.get_executions(24))
        }


def main():
    import sys
    automator = TaskAutomator()
    
    if len(sys.argv) < 2:
        print("Agent Task Automation")
        print("Usage: task-automation.py <command> [args]")
        print("Commands:")
        print("  create <name> <trigger_type> <interval_minutes> <action>")
        print("  execute <automation_id>")
        print("  check")
        print("  toggle <automation_id> <enabled>")
        print("  list")
        print("  executions [limit]")
        print("  stats")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "create":
        if len(sys.argv) < 5:
            print("Usage: create <name> <trigger_type> <interval_minutes> <action>")
            return
        name = sys.argv[2]
        trigger_type = sys.argv[3]
        interval = int(sys.argv[4])
        action = sys.argv[5] if len(sys.argv) > 5 else "execute"
        
        trigger_config = {"interval_minutes": interval}
        result = automator.create_automation(name, trigger_type, trigger_config, action)
        print(json.dumps(result, indent=2))
    
    elif cmd == "execute":
        if len(sys.argv) < 3:
            print("Usage: execute <automation_id>")
            return
        result = automator.execute_automation(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "check":
        result = automator.check_scheduled()
        print(json.dumps(result, indent=2))
    
    elif cmd == "toggle":
        if len(sys.argv) < 4:
            print("Usage: toggle <automation_id> <enabled>")
            return
        enabled = sys.argv[3].lower() == "true"
        result = automator.toggle_automation(sys.argv[2], enabled)
        print(json.dumps(result, indent=2))
    
    elif cmd == "list":
        result = automator.get_automations()
        print(json.dumps(result, indent=2))
    
    elif cmd == "executions":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        result = automator.get_executions(limit)
        print(json.dumps(result, indent=2))
    
    elif cmd == "stats":
        result = automator.get_stats()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()