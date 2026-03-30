#!/usr/bin/env python3
"""
Agent Coordinator - Task Assignment and Coordination
Assigns tasks to the right agents based on skills and availability
"""
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

DATA_DIR = Path("/root/.openclaw/workspace/agent-hub/data")
TASKS_FILE = DATA_DIR / "tasks.json"

class Task:
    def __init__(self, title: str, description: str, required_skills: List[str], priority: str = "medium", created_by: str = "system"):
        self.id = f"task_{int(datetime.now().timestamp())}"
        self.title = title
        self.description = description
        self.required_skills = required_skills
        self.priority = priority  # low, medium, high, critical
        self.status = "pending"  # pending, assigned, in_progress, completed, blocked
        self.created_by = created_by
        self.created_at = datetime.now().isoformat()
        self.assigned_to = None
        self.completed_at = None
        
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "required_skills": self.required_skills,
            "priority": self.priority,
            "status": self.status,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "assigned_to": self.assigned_to,
            "completed_at": self.completed_at
        }
    
    @staticmethod
    def from_dict(d: dict) -> "Task":
        # Handle both formats (with and without required_skills)
        title = d.get("title", "Untitled")
        desc = d.get("description", "")
        skills = d.get("required_skills", d.get("skills", []))
        priority = d.get("priority", "medium")
        created_by = d.get("created_by", d.get("by", "system"))
        
        t = Task(title, desc, skills, priority, created_by)
        t.id = str(d.get("id", ""))
        t.status = d.get("status", "pending")
        t.assigned_to = d.get("assigned_to")
        t.created_at = d.get("created_at", d.get("created", datetime.now().isoformat()))
        t.completed_at = d.get("completed_at")
        return t

class AgentCoordinator:
    """Coordinates tasks between agents"""
    
    def __init__(self):
        self.tasks = self.load_tasks()
        
    def load_tasks(self) -> List[Task]:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if TASKS_FILE.exists():
            with open(TASKS_FILE) as f:
                data = json.load(f)
                return [Task.from_dict(t) for t in data]
        return []
    
    def save_tasks(self):
        with open(TASKS_FILE, 'w') as f:
            json.dump([t.to_dict() for t in self.tasks], f, indent=2)
    
    def get_all(self) -> List[Task]:
        return self.tasks
    
    def create_task(self, title: str, description: str, required_skills: List[str], priority: str = "medium", created_by: str = "system") -> Task:
        task = Task(title, description, required_skills, priority, created_by)
        self.tasks.append(task)
        self.save_tasks()
        return task
    
    def assign_task(self, task_id: str, agent_id: str) -> bool:
        for t in self.tasks:
            if t.id == task_id:
                t.assigned_to = agent_id
                t.status = "assigned"
                self.save_tasks()
                return True
        return False
    
    def complete_task(self, task_id: str) -> bool:
        for t in self.tasks:
            if t.id == task_id:
                t.status = "completed"
                t.completed_at = datetime.now().isoformat()
                self.save_tasks()
                return True
        return False
    
    def get_pending(self) -> List[Task]:
        return [t for t in self.tasks if t.status == "pending"]
    
    def get_by_status(self, status: str) -> List[Task]:
        return [t for t in self.tasks if t.status == status]
    
    def get_by_agent(self, agent_id: str) -> List[Task]:
        return [t for t in self.tasks if t.assigned_to == agent_id]
    
    def status_report(self) -> Dict:
        status_counts = {}
        for t in self.tasks:
            status_counts[t.status] = status_counts.get(t.status, 0) + 1
        
        priority_counts = {}
        for t in self.tasks:
            priority_counts[t.priority] = priority_counts.get(t.priority, 0) + 1
        
        return {
            "total_tasks": len(self.tasks),
            "by_status": status_counts,
            "by_priority": priority_counts
        }
    
    def match_agent_to_task(self, agents: List[dict], task: Task) -> Optional[str]:
        """Find best agent for a task based on skills"""
        best_agent = None
        best_match = 0
        
        for agent in agents:
            agent_skills = agent.get("skills", [])
            match = sum(1 for rs in task.required_skills if rs in agent_skills)
            if match > best_match:
                best_match = match
                best_agent = agent.get("id")
        
        return best_agent if best_match > 0 else None


def main():
    import sys
    
    coordinator = AgentCoordinator()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "create":
            # agent-coordinator create "Task title" "description" skill1,skill2
            title = sys.argv[2] if len(sys.argv) > 2 else "Untitled"
            desc = sys.argv[3] if len(sys.argv) > 3 else ""
            skills = sys.argv[4].split(",") if len(sys.argv) > 4 else []
            priority = sys.argv[5] if len(sys.argv) > 5 else "medium"
            
            task = coordinator.create_task(title, desc, skills, priority)
            print(f"Created task: {task.id}")
            
        elif cmd == "list":
            tasks = coordinator.get_all()
            print(f"\n📋 Tasks: {len(tasks)}\n")
            for t in tasks:
                status_icon = {"pending": "⏳", "assigned": "👤", "in_progress": "🔄", "completed": "✅", "blocked": "🚫"}[t.status]
                print(f"  {status_icon} [{t.priority}] {t.title}")
                print(f"     ID: {t.id}")
                print(f"     Skills: {', '.join(t.required_skills)}")
                if t.assigned_to:
                    print(f"     Assigned: {t.assigned_to}")
                print()
                
        elif cmd == "status":
            report = coordinator.status_report()
            print(f"\n📊 Task Status\n")
            print(f"  Total: {report['total_tasks']}")
            print(f"\n  By Status:")
            for s, c in report.get("by_status", {}).items():
                print(f"    {s}: {c}")
            print(f"\n  By Priority:")
            for p, c in report.get("by_priority", {}).items():
                print(f"    {p}: {c}")
                
        elif cmd == "assign":
            task_id = sys.argv[2] if len(sys.argv) > 2 else None
            agent_id = sys.argv[3] if len(sys.argv) > 3 else None
            if task_id and agent_id:
                if coordinator.assign_task(task_id, agent_id):
                    print(f"Assigned {task_id} to {agent_id}")
                else:
                    print(f"Task not found: {task_id}")
            else:
                print("Usage: agent-coordinator assign <task_id> <agent_id>")
                
        elif cmd == "complete":
            task_id = sys.argv[2] if len(sys.argv) > 2 else None
            if task_id:
                if coordinator.complete_task(task_id):
                    print(f"Completed: {task_id}")
                else:
                    print(f"Task not found: {task_id}")
            else:
                print("Usage: agent-coordinator complete <task_id>")
                
        else:
            print("Commands: create, list, status, assign, complete")
    else:
        # Default: show status
        report = coordinator.status_report()
        print(f"Task Coordinator: {report['total_tasks']} tasks")


if __name__ == "__main__":
    main()
