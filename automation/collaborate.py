#!/usr/bin/env python3
"""
COLLABORATE - Agent-to-Agent Collaboration System
Real work: assign tasks, track progress, measure quality
"""
import json
import time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional

HUB_DIR = Path("/root/.openclaw/workspace/agent-hub")

@dataclass
class Task:
    id: str
    title: str
    description: str
    assigned_to: Optional[str] = None
    created_by: str = ""
    status: str = "pending"
    priority: str = "medium"
    quality_score: float = 0.0
    created_at: str = ""
    updated_at: str = ""
    completed_at: Optional[str] = None

class CollaborationSystem:
    def __init__(self):
        self.tasks_file = HUB_DIR / "data" / "tasks.json"
        self.tasks = self.load_tasks()
    
    def load_tasks(self) -> List[Task]:
        if self.tasks_file.exists():
            with open(self.tasks_file) as f:
                data = json.load(f)
                tasks_data = data if isinstance(data, list) else data.get("tasks", [])
                # Only keep fields that match Task dataclass
                valid_fields = {'id', 'title', 'description', 'assigned_to', 'created_by',
                              'status', 'priority', 'quality_score', 'created_at',
                              'updated_at', 'completed_at'}
                filtered = [{k: v for k, v in t.items() if k in valid_fields} for t in tasks_data]
                return [Task(**t) for t in filtered]
        return []
    
    def save_tasks(self):
        self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tasks_file, 'w') as f:
            json.dump({"tasks": [asdict(t) for t in self.tasks]}, f, indent=2)
    
    def create_task(self, title: str, description: str, created_by: str, 
                    priority: str = "medium", assigned_to: str = None) -> Task:
        task = Task(
            id=f"task_{len(self.tasks) + 1}_{int(time.time())}",
            title=title,
            description=description,
            assigned_to=assigned_to,
            created_by=created_by,
            status="pending",
            priority=priority,
            quality_score=0.0,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            completed_at=None
        )
        self.tasks.append(task)
        self.save_tasks()
        return task
    
    def assign_task(self, task_id: str, agent_id: str) -> bool:
        for t in self.tasks:
            if t.id == task_id:
                t.assigned_to = agent_id
                t.status = "in_progress"
                t.updated_at = datetime.utcnow().isoformat()
                self.save_tasks()
                return True
        return False
    
    def complete_task(self, task_id: str, quality_score: float = 50) -> bool:
        for t in self.tasks:
            if t.id == task_id:
                t.status = "done"
                t.quality_score = quality_score
                t.updated_at = datetime.utcnow().isoformat()
                t.completed_at = datetime.utcnow().isoformat()
                self.save_tasks()
                return True
        return False
    
    def get_agent_tasks(self, agent_id: str) -> List[Task]:
        return [t for t in self.tasks if t.assigned_to == agent_id]
    
    def get_pending_tasks(self) -> List[Task]:
        return [t for t in self.tasks if t.status == "pending"]
    
    def get_stats(self) -> dict:
        total = len(self.tasks)
        done = len([t for t in self.tasks if t.status == "done"])
        in_progress = len([t for t in self.tasks if t.status == "in_progress"])
        pending = len([t for t in self.tasks if t.status == "pending"])
        
        avg_quality = 0
        completed = [t for t in self.tasks if t.quality_score > 0]
        if completed:
            avg_quality = sum(t.quality_score for t in completed) / len(completed)
        
        return {
            "total": total,
            "done": done,
            "in_progress": in_progress,
            "pending": pending,
            "avg_quality": avg_quality,
            "completion_rate": (done / total * 100) if total > 0 else 0
        }
    
    def __repr__(self):
        stats = self.get_stats()
        return f"""Collaboration System:
  Tasks: {stats['total']} total
    Done: {stats['done']}
    In Progress: {stats['in_progress']}
    Pending: {stats['pending']}
  Quality: {stats['avg_quality']:.1f}%
  Completion: {stats['completion_rate']:.1f}%"""


if __name__ == "__main__":
    cs = CollaborationSystem()
    print(cs)
    
    # Demo: create and assign a task
    task = cs.create_task(
        "Build CLI command",
        "Add a new command to the agent hub CLI",
        created_by="marxagent",
        priority="high",
        assigned_to="builder"
    )
    print(f"\nCreated: {task.title}")
    
    # Get stats
    print(cs)
