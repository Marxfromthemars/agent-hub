#!/usr/bin/env python3
"""
Agent Task Prioritizer
AI-powered task prioritization using impact/effort analysis.
"""

import json
from datetime import datetime
from pathlib import Path

class TaskPrioritizer:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.tasks_file = self.data_dir / "prioritized_tasks.json"
        self.tasks = self._load_tasks()
    
    def _load_tasks(self):
        if self.tasks_file.exists():
            with open(self.tasks_file) as f:
                return json.load(f)
        return {"tasks": [], "context": {}}
    
    def _save_tasks(self):
        with open(self.tasks_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def add_task(self, title, impact=5, effort=5, deadline=None, tags=None):
        """Add a task with prioritization metadata."""
        task = {
            "id": f"task-{len(self.tasks['tasks']) + 1}",
            "title": title,
            "impact": impact,  # 1-10
            "effort": effort,  # 1-10 (1 = easy, 10 = hard)
            "deadline": deadline,
            "tags": tags or [],
            "created": datetime.utcnow().isoformat(),
            "priority_score": self._calculate_priority(impact, effort, deadline),
            "status": "pending"
        }
        
        self.tasks["tasks"].append(task)
        self._sort_by_priority()
        self._save_tasks()
        
        return {"status": "added", "task_id": task["id"], "priority": task["priority_score"]}
    
    def _calculate_priority(self, impact, effort, deadline):
        """Calculate priority score (higher = more important)."""
        base_score = impact * 10 - effort * 5
        
        # Bonus for deadline urgency
        if deadline:
            try:
                deadline_dt = datetime.fromisoformat(deadline)
                hours_until = (deadline_dt - datetime.utcnow()).total_seconds() / 3600
                
                if hours_until < 0:
                    base_score += 50  # Overdue
                elif hours_until < 24:
                    base_score += 30  # Due soon
                elif hours_until < 72:
                    base_score += 10  # This week
            except:
                pass
        
        return max(0, base_score)
    
    def _sort_by_priority(self):
        """Sort tasks by priority score descending."""
        self.tasks["tasks"].sort(key=lambda t: t["priority_score"], reverse=True)
    
    def get_queue(self, limit=10):
        """Get prioritized task queue."""
        pending = [t for t in self.tasks["tasks"] if t["status"] == "pending"]
        return pending[:limit]
    
    def complete_task(self, task_id):
        """Mark task as completed."""
        for task in self.tasks["tasks"]:
            if task["id"] == task_id:
                task["status"] = "completed"
                task["completed_at"] = datetime.utcnow().isoformat()
                self._save_tasks()
                return {"status": "completed"}
        return {"status": "not_found"}
    
    def get_by_tag(self, tag):
        """Get tasks by tag."""
        return [t for t in self.tasks["tasks"] if tag in t.get("tags", [])]
    
    def get_eisenhower_matrix(self):
        """Return tasks organized by Eisenhower matrix."""
        urgent_high = []
        important_high = []
        urgent_low = []
        important_low = []
        
        for task in self.tasks["tasks"]:
            if task["status"] == "completed":
                continue
            
            # Tasks with deadlines within 48h are urgent
            urgent = False
            if task.get("deadline"):
                try:
                    hours = (datetime.fromisoformat(task["deadline"]) - datetime.utcnow()).total_seconds() / 3600
                    urgent = hours < 48
                except:
                    pass
            
            important = task["impact"] >= 7
            
            if urgent and important:
                urgent_high.append(task)
            elif important and not urgent:
                important_high.append(task)
            elif urgent and not important:
                urgent_low.append(task)
            else:
                important_low.append(task)
        
        return {
            "do_first": urgent_high,
            "schedule": important_high,
            "delegate": urgent_low,
            "consider": important_low
        }
    
    def get_stats(self):
        """Get task statistics."""
        tasks = self.tasks["tasks"]
        pending = [t for t in tasks if t["status"] == "pending"]
        completed = [t for t in tasks if t["status"] == "completed"]
        
        return {
            "total": len(tasks),
            "pending": len(pending),
            "completed": len(completed),
            "avg_impact": sum(t["impact"] for t in tasks) / len(tasks) if tasks else 0,
            "avg_effort": sum(t["effort"] for t in tasks) / len(tasks) if tasks else 0
        }


def main():
    import sys
    prioritizer = TaskPrioritizer()
    
    if len(sys.argv) < 2:
        print("Agent Task Prioritizer")
        print("Usage: task-prioritizer.py <command> [args]")
        print("Commands:")
        print("  add <title> [impact] [effort] [deadline] [tags...]")
        print("  queue [limit]")
        print("  complete <task_id>")
        print("  by-tag <tag>")
        print("  eisenhower")
        print("  stats")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "add":
        if len(sys.argv) < 3:
            print("Usage: add <title> [impact] [effort] [deadline] [tags...]")
            return
        title = sys.argv[2]
        impact = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        effort = int(sys.argv[4]) if len(sys.argv) > 4 else 5
        deadline = sys.argv[5] if len(sys.argv) > 5 else None
        tags = sys.argv[6:] if len(sys.argv) > 6 else None
        result = prioritizer.add_task(title, impact, effort, deadline, tags)
        print(json.dumps(result, indent=2))
    
    elif cmd == "queue":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        result = prioritizer.get_queue(limit)
        print(json.dumps(result, indent=2))
    
    elif cmd == "complete":
        if len(sys.argv) < 3:
            print("Usage: complete <task_id>")
            return
        result = prioritizer.complete_task(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "by-tag":
        if len(sys.argv) < 3:
            print("Usage: by-tag <tag>")
            return
        result = prioritizer.get_by_tag(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "eisenhower":
        result = prioritizer.get_eisenhower_matrix()
        print(json.dumps(result, indent=2))
    
    elif cmd == "stats":
        result = prioritizer.get_stats()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()