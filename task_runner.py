#!/usr/bin/env python3
"""
AGENT TASK RUNNER - Execute real tasks for Agent Hub
"""
import json
import sys
import os
from datetime import datetime
from pathlib import Path

class TaskRunner:
    def __init__(self):
        self.hub_dir = Path("/root/.openclaw/workspace/agent-hub")
        self.tasks_file = self.hub_dir / "data" / "tasks.json"
        self.tasks = self.load_tasks()
    
    def load_tasks(self):
        if self.tasks_file.exists():
            with open(self.tasks_file) as f:
                return json.load(f)
        return {"tasks": [], "last_id": 0}
    
    def save_tasks(self):
        with open(self.tasks_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def create_task(self, title: str, description: str = "", priority: str = "medium") -> dict:
        self.tasks["last_id"] += 1
        task = {
            "id": self.tasks["last_id"],
            "title": title,
            "description": description,
            "priority": priority,
            "status": "pending",
            "created": datetime.utcnow().isoformat(),
            "assigned_to": None,
            "completed_at": None
        }
        self.tasks["tasks"].append(task)
        self.save_tasks()
        return task
    
    def list_tasks(self, status: str = None):
        tasks = self.tasks["tasks"]
        if status:
            tasks = [t for t in tasks if t["status"] == status]
        return tasks
    
    def complete_task(self, task_id: int, output: str = ""):
        for t in self.tasks["tasks"]:
            if t["id"] == task_id:
                t["status"] = "completed"
                t["completed_at"] = datetime.utcnow().isoformat()
                t["output"] = output
                self.save_tasks()
                return t
        return None
    
    def stats(self):
        tasks = self.tasks["tasks"]
        return {
            "total": len(tasks),
            "pending": len([t for t in tasks if t["status"] == "pending"]),
            "in_progress": len([t for t in tasks if t["status"] == "in_progress"]),
            "completed": len([t for t in tasks if t["status"] == "completed"])
        }

if __name__ == "__main__":
    runner = TaskRunner()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "list":
            for t in runner.list_tasks():
                status_icon = {"pending": "○", "in_progress": "◐", "completed": "●"}.get(t["status"], "?")
                print(f"{status_icon} #{t['id']} [{t['priority']}] {t['title']}")
        elif cmd == "stats":
            s = runner.stats()
            print(f"Tasks: {s['pending']} pending, {s['in_progress']} in progress, {s['completed']} completed")
        elif cmd == "create" and len(sys.argv) > 2:
            task = runner.create_task(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
            print(f"Created task #{task['id']}: {task['title']}")
        elif cmd == "complete" and len(sys.argv) > 2:
            result = runner.complete_task(int(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else "")
            if result:
                print(f"Completed task #{result['id']}")
        else:
            print("Commands: list, stats, create <title> [desc], complete <id> [output]")
    else:
        print("Usage: python3 task_runner.py <command>")
        print("Commands: list, stats, create, complete")
