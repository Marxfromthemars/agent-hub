#!/usr/bin/env python3
"""
Agent Task Scheduler
Schedules and coordinates task execution across multiple agents.
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

class AgentScheduler:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.schedule_file = self.data_dir / "task_schedule.json"
        self.history_file = self.data_dir / "schedule_history.json"
        self.schedule = self._load_schedule()
        self.history = self._load_history()
    
    def _load_schedule(self):
        if self.schedule_file.exists():
            with open(self.schedule_file) as f:
                return json.load(f)
        return {"pending": [], "running": [], "completed": [], "scheduled": []}
    
    def _load_history(self):
        if self.history_file.exists():
            with open(self.history_file) as f:
                return json.load(f)
        return {"executions": []}
    
    def _save_schedule(self):
        with open(self.schedule_file, 'w') as f:
            json.dump(self.schedule, f, indent=2)
    
    def _save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def schedule_task(self, task_type, agent_id, payload, run_at=None, interval=None):
        """Schedule a task for execution."""
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        task = {
            "id": task_id,
            "type": task_type,
            "agent_id": agent_id,
            "payload": payload,
            "scheduled_at": datetime.utcnow().isoformat(),
            "run_at": run_at or datetime.utcnow().isoformat(),
            "interval": interval,  # None = one-time, otherwise recurring
            "status": "pending",
            "attempts": 0
        }
        
        self.schedule["pending"].append(task)
        self._save_schedule()
        return {"status": "scheduled", "task_id": task_id, "task": task}
    
    def execute_pending(self, agent_registry):
        """Execute all tasks that are due."""
        now = datetime.utcnow()
        to_execute = []
        
        # Find tasks due for execution
        self.schedule["pending"] = [
            task for task in self.schedule["pending"]
            if datetime.fromisoformat(task["run_at"]) <= now
        ]
        
        for task in self.schedule["pending"][:]:  # Copy to avoid mutation issues
            agent = agent_registry.get(task["agent_id"])
            if agent:
                result = self._execute_task(task, agent)
                self.schedule["pending"].remove(task)
                self.schedule["running"].append(result)
                
                # Handle recurring tasks
                if task.get("interval"):
                    task["run_at"] = (datetime.fromisoformat(task["run_at"]) + 
                                     timedelta(minutes=task["interval"])).isoformat()
                    task["status"] = "pending"
                    self.schedule["pending"].append(task)
                else:
                    self.schedule["completed"].append(result)
        
        self._save_schedule()
        return {"executed": len(self.schedule["running"])}
    
    def _execute_task(self, task, agent):
        """Execute a single task."""
        task["attempts"] += 1
        task["started_at"] = datetime.utcnow().isoformat()
        task["status"] = "running"
        
        # Record in history
        self.history["executions"].append({
            "task_id": task["id"],
            "agent_id": task["agent_id"],
            "started_at": task["started_at"],
            "type": task["type"]
        })
        self._save_history()
        
        return task
    
    def complete_task(self, task_id, result=None):
        """Mark a task as completed."""
        for task in self.schedule["running"]:
            if task["id"] == task_id:
                task["status"] = "completed"
                task["completed_at"] = datetime.utcnow().isoformat()
                task["result"] = result or {}
                
                self.schedule["running"].remove(task)
                self.schedule["completed"].append(task)
                self._save_schedule()
                return {"status": "completed"}
        
        return {"status": "not_found"}
    
    def fail_task(self, task_id, error):
        """Mark a task as failed."""
        for task in self.schedule["running"]:
            if task["id"] == task_id:
                task["status"] = "failed"
                task["failed_at"] = datetime.utcnow().isoformat()
                task["error"] = str(error)
                
                self.schedule["running"].remove(task)
                self._save_schedule()
                return {"status": "marked_failed"}
        
        return {"status": "not_found"}
    
    def get_queue(self):
        """Get all queued tasks."""
        return {
            "pending": self.schedule["pending"],
            "running": self.schedule["running"],
            "completed": self.schedule["completed"][-20:]  # Last 20
        }
    
    def get_statistics(self):
        """Get scheduler statistics."""
        return {
            "pending": len(self.schedule["pending"]),
            "running": len(self.schedule["running"]),
            "completed_today": len([
                t for t in self.schedule["completed"]
                if t.get("completed_at", "").startswith(datetime.utcnow().strftime("%Y-%m-%d"))
            ]),
            "total_completed": len(self.schedule["completed"]),
            "total_executions": len(self.history["executions"])
        }


def main():
    import sys
    scheduler = AgentScheduler()
    
    if len(sys.argv) < 2:
        print("Agent Task Scheduler")
        print("Usage: agent-scheduler.py <command> [args]")
        print("Commands:")
        print("  schedule <type> <agent_id> <payload_json> [run_at]")
        print("  queue")
        print("  stats")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "schedule":
        if len(sys.argv) < 4:
            print("Usage: schedule <type> <agent_id> <payload_json>")
            return
        task_type = sys.argv[2]
        agent_id = sys.argv[3]
        try:
            payload = json.loads(sys.argv[4])
        except:
            payload = {"data": sys.argv[4]}
        run_at = sys.argv[5] if len(sys.argv) > 5 else None
        
        result = scheduler.schedule_task(task_type, agent_id, payload, run_at)
        print(json.dumps(result, indent=2))
    
    elif cmd == "queue":
        queue = scheduler.get_queue()
        print(json.dumps(queue, indent=2))
    
    elif cmd == "stats":
        stats = scheduler.get_statistics()
        print(json.dumps(stats, indent=2))
    
    elif cmd == "execute":
        # Simple agent registry for demo
        registry = {"marxagent": {"id": "marxagent"}}
        result = scheduler.execute_pending(registry)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()