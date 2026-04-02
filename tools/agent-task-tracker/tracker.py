#!/usr/bin/env python3
"""
Agent Task Tracker
Tracks tasks across multiple agents for collaborative projects
"""

import argparse
import json
import os
from pathlib import Path
from datetime import datetime

TASK_FILE = Path.home() / ".cache" / "agent-hub" / "tasks.json"

class TaskTracker:
    def __init__(self):
        self.tasks = self.load()
    
    def load(self):
        if TASK_FILE.exists():
            with open(TASK_FILE) as f:
                return json.load(f)
        return {"tasks": [], "projects": {}}
    
    def save(self):
        TASK_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TASK_FILE, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def add(self, title, description, project=None, priority=3):
        """Add a new task"""
        task = {
            "id": len(self.tasks["tasks"]) + 1,
            "title": title,
            "description": description,
            "project": project,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "assignee": None,
            "completed_at": None
        }
        self.tasks["tasks"].append(task)
        self.save()
        return task["id"]
    
    def list(self, project=None, status=None):
        """List tasks"""
        tasks = self.tasks["tasks"]
        if project:
            tasks = [t for t in tasks if t.get("project") == project]
        if status:
            tasks = [t for t in tasks if t.get("status") == status]
        return tasks
    
    def complete(self, task_id):
        """Mark task complete"""
        for task in self.tasks["tasks"]:
            if task["id"] == task_id:
                task["status"] = "completed"
                task["completed_at"] = datetime.now().isoformat()
        self.save()
    
    def assign(self, task_id, agent):
        """Assign task to agent"""
        for task in self.tasks["tasks"]:
            if task["id"] == task_id:
                task["assignee"] = agent
        self.save()


def main():
    parser = argparse.ArgumentParser(description="Agent Task Tracker")
    parser.add_argument("action", choices=["add", "list", "complete", "assign"])
    parser.add_argument("--title", help="Task title")
    parser.add_argument("--description", help="Task description")
    parser.add_argument("--project", help="Project name")
    parser.add_argument("--priority", type=int, default=3, help="Priority 1-5")
    parser.add_argument("--id", type=int, help="Task ID")
    parser.add_argument("--agent", help="Agent name")
    
    args = parser.parse_args()
    tracker = TaskTracker()
    
    if args.action == "add":
        if not args.title or not args.description:
            print("Error: --title and --description required")
            return
        task_id = tracker.add(args.title, args.description, args.project, args.priority)
        print(f"Created task #{task_id}")
    
    elif args.action == "list":
        tasks = tracker.list(args.project)
        for t in tasks:
            status = t.get("status", "pending")
            proj = t.get("project", "None")
            print(f"  [{status:9}] #{t['id']} {t['title']} ({proj})")
    
    elif args.action == "complete":
        if not args.id:
            print("Error: --id required")
            return
        tracker.complete(args.id)
        print(f"Completed task #{args.id}")


if __name__ == "__main__":
    main()