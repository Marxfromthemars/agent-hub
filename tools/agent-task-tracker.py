#!/usr/bin/env python3
"""
Agent Task Tracker - Track agent work in real-time
Shows tasks, assignments, progress, and completion rates
"""
import json
import sys
from datetime import datetime
from pathlib import Path

class TaskTracker:
    """Track agent tasks and work"""
    
    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir or "/root/.openclaw/workspace/agent-hub/data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_file = self.data_dir / "tasks.json"
        
    def load_tasks(self):
        if self.tasks_file.exists():
            with open(self.tasks_file) as f:
                return json.load(f)
        return {"tasks": [], "assignments": {}}
    
    def save_tasks(self, data):
        with open(self.tasks_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_task(self, task_id: str, title: str, agent: str = None, priority: str = "medium"):
        data = self.load_tasks()
        if "assignments" not in data:
            data["assignments"] = {}
        task = {
            "id": task_id,
            "title": title,
            "assigned_to": agent,
            "priority": priority,
            "status": "pending",
            "created": datetime.utcnow().isoformat(),
            "completed": None
        }
        data["tasks"].append(task)
        if agent:
            data["assignments"][agent] = data["assignments"].get(agent, 0) + 1
        self.save_tasks(data)
        return task
    
    def complete_task(self, task_id: str):
        data = self.load_tasks()
        for t in data["tasks"]:
            if t["id"] == task_id:
                t["status"] = "completed"
                t["completed"] = datetime.utcnow().isoformat()
                break
        self.save_tasks(data)
    
    def get_agent_tasks(self, agent_id: str):
        data = self.load_tasks()
        return [t for t in data["tasks"] if t.get("assigned_to") == agent_id]
    
    def get_stats(self):
        data = self.load_tasks()
        tasks = data.get("tasks", [])
        completed = [t for t in tasks if t["status"] == "completed"]
        pending = [t for t in tasks if t["status"] == "pending"]
        in_progress = [t for t in tasks if t["status"] == "in_progress"]
        
        return {
            "total": len(tasks),
            "completed": len(completed),
            "pending": len(pending),
            "in_progress": len(in_progress),
            "completion_rate": len(completed) / len(tasks) if tasks else 0,
            "agents": data.get("assignments", {})
        }
    
    def report(self):
        stats = self.get_stats()
        now = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
        print("=" * 52)
        print(f"        AGENT TASK TRACKER REPORT")
        print(f"        {now}")
        print("=" * 52)
        print("  TASK STATISTICS")
        print("  " + "-" * 46)
        print(f"  Total Tasks:     {stats['total']}")
        print(f"  Completed:       {stats['completed']}")
        print(f"  Pending:         {stats['pending']}")
        print(f"  In Progress:    {stats['in_progress']}")
        pct = stats['completion_rate'] * 100
        print(f"  Completion Rate: {pct:.1f}%")
        
        if stats["agents"]:
            print("  " + "-" * 46)
            print("  AGENT WORKLOAD")
            for agent, count in sorted(stats["agents"].items(), key=lambda x: -x[1]):
                bar = "#" * min(count, 15)
                print(f"    {agent:12} {count:3} tasks  [{bar}]")
        
        print("=" * 52)
        
        # Show recent pending tasks
        data = self.load_tasks()
        pending = [t for t in data.get("tasks", []) if t["status"] == "pending"][-5:]
        if pending:
            print("\nPENDING TASKS:")
            for t in pending:
                agent = t.get('assigned_to', 'unassigned')
                print(f"  - [{t['id']}] {t['title']} ({agent})")

def main():
    tracker = TaskTracker()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "add":
            task_id = sys.argv[2] if len(sys.argv) > 2 else f"task_{len(tracker.load_tasks()['tasks'])+1}"
            title = sys.argv[3] if len(sys.argv) > 3 else "New task"
            agent = sys.argv[4] if len(sys.argv) > 4 else None
            tracker.add_task(task_id, title, agent)
            print(f"Added: {task_id}")
        elif cmd == "complete":
            if len(sys.argv) > 2:
                tracker.complete_task(sys.argv[2])
                print(f"Completed: {sys.argv[2]}")
        elif cmd == "stats":
            print(json.dumps(tracker.get_stats(), indent=2))
        else:
            tracker.report()
    else:
        tracker.report()

if __name__ == "__main__":
    main()