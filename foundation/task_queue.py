"""
Task Queue System - Agents get work through here
Integrates with orchestrator and knowledge graph
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import uuid

DB_PATH = Path("/root/.openclaw/workspace/agent-hub/data/tasks.db")

class TaskQueue:
    """Queue for agent tasks with priority and routing"""
    
    PRIORITY_LEVELS = {
        "critical": 100,
        "high": 75,
        "medium": 50,
        "low": 25
    }
    
    STATUS_TYPES = [
        "queued",      # Waiting for assignment
        "assigned",    # Assigned to agent
        "in_progress", # Agent actively working
        "review",      # Awaiting review
        "complete",    # Done and validated
        "failed",      # Failed or abandoned
        "blocked"      # Waiting on something
    ]
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or DB_PATH
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize task database"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'queued',
                created_at TEXT,
                updated_at TEXT,
                assigned_to TEXT,
                created_by TEXT,
                due_date TEXT,
                estimated_hours REAL,
                actual_hours REAL,
                tags TEXT,
                dependencies TEXT,
                output TEXT,
                result TEXT,
                quality_score REAL,
                metadata TEXT
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS task_events (
                id TEXT PRIMARY KEY,
                task_id TEXT,
                event_type TEXT,
                agent_id TEXT,
                timestamp TEXT,
                details TEXT
            )
        """)
        
        self.conn.commit()
    
    def create_task(self, title: str, description: str = "",
                   priority: str = "medium", created_by: str = "system",
                   tags: List[str] = None, dependencies: List[str] = None,
                   due_date: str = None) -> dict:
        """Create a new task"""
        task_id = str(uuid.uuid4())[:8]
        now = datetime.utcnow().isoformat()
        
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
            "priority_score": self.PRIORITY_LEVELS.get(priority, 50),
            "status": "queued",
            "created_at": now,
            "updated_at": now,
            "assigned_to": None,
            "created_by": created_by,
            "due_date": due_date,
            "estimated_hours": None,
            "actual_hours": None,
            "tags": json.dumps(tags or []),
            "dependencies": json.dumps(dependencies or []),
            "output": None,
            "result": None,
            "quality_score": None,
            "metadata": None
        }
        
        cols = list(task.keys())
        vals = list(task.values())
        placeholders = ["?"] * len(cols)
        
        self.conn.execute(
            f"INSERT INTO tasks ({', '.join(cols)}) VALUES ({', '.join(placeholders)})",
            vals
        )
        self.conn.commit()
        
        self._log_event(task_id, "created", created_by, {"title": title})
        
        return task
    
    def get_task(self, task_id: str) -> Optional[dict]:
        """Get a single task"""
        row = self.conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        
        return dict(row) if row else None
    
    def get_next_task(self, agent_id: str = None, skills: List[str] = None) -> Optional[dict]:
        """Get the highest priority available task"""
        query = """
            SELECT * FROM tasks 
            WHERE status = 'queued'
            ORDER BY priority_score DESC, created_at ASC
            LIMIT 1
        """
        
        row = self.conn.execute(query).fetchone()
        
        if row:
            task = dict(row)
            # Check dependencies
            deps = json.loads(task.get("dependencies", "[]"))
            for dep_id in deps:
                dep = self.get_task(dep_id)
                if dep and dep["status"] != "complete":
                    return self.get_next_task(agent_id, skills)  # Skip this one
            return task
        
        return None
    
    def assign_task(self, task_id: str, agent_id: str) -> bool:
        """Assign a task to an agent"""
        now = datetime.utcnow().isoformat()
        
        self.conn.execute("""
            UPDATE tasks 
            SET assigned_to = ?, status = 'assigned', updated_at = ?
            WHERE id = ?
        """, (agent_id, now, task_id))
        self.conn.commit()
        
        self._log_event(task_id, "assigned", agent_id, {})
        
        return True
    
    def start_task(self, task_id: str) -> bool:
        """Mark task as in progress"""
        now = datetime.utcnow().isoformat()
        
        self.conn.execute("""
            UPDATE tasks 
            SET status = 'in_progress', updated_at = ?
            WHERE id = ?
        """, (now, task_id))
        self.conn.commit()
        
        self._log_event(task_id, "started", None, {})
        
        return True
    
    def complete_task(self, task_id: str, result: str = None,
                     quality_score: float = None) -> bool:
        """Mark task as complete"""
        now = datetime.utcnow().isoformat()
        
        self.conn.execute("""
            UPDATE tasks 
            SET status = 'complete', result = ?, quality_score = ?, 
                updated_at = ?, completed_at = ?
            WHERE id = ?
        """, (result, quality_score, now, now, task_id))
        self.conn.commit()
        
        self._log_event(task_id, "completed", None, {
            "result": result,
            "quality": quality_score
        })
        
        return True
    
    def fail_task(self, task_id: str, reason: str = None) -> bool:
        """Mark task as failed"""
        now = datetime.utcnow().isoformat()
        
        self.conn.execute("""
            UPDATE tasks 
            SET status = 'failed', result = ?, updated_at = ?
            WHERE id = ?
        """, (reason, now, task_id))
        self.conn.commit()
        
        self._log_event(task_id, "failed", None, {"reason": reason})
        
        return True
    
    def get_tasks_by_status(self, status: str) -> List[dict]:
        """Get all tasks with a given status"""
        rows = self.conn.execute(
            "SELECT * FROM tasks WHERE status = ? ORDER BY priority_score DESC",
            (status,)
        ).fetchall()
        
        return [dict(row) for row in rows]
    
    def get_tasks_by_agent(self, agent_id: str) -> List[dict]:
        """Get all tasks assigned to an agent"""
        rows = self.conn.execute(
            "SELECT * FROM tasks WHERE assigned_to = ? ORDER BY priority_score DESC",
            (agent_id,)
        ).fetchall()
        
        return [dict(row) for row in rows]
    
    def get_queue_stats(self) -> dict:
        """Get queue statistics"""
        stats = {}
        for status in self.STATUS_TYPES:
            count = self.conn.execute(
                "SELECT COUNT(*) FROM tasks WHERE status = ?", (status,)
            ).fetchone()[0]
            stats[status] = count
        
        total = sum(stats.values())
        stats["total"] = total
        
        return stats
    
    def get_all_tasks(self, limit: int = 100) -> List[dict]:
        """Get all tasks, newest first"""
        rows = self.conn.execute(
            "SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        
        return [dict(row) for row in rows]
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        self.conn.execute("DELETE FROM task_events WHERE task_id = ?", (task_id,))
        self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()
        return True
    
    def _log_event(self, task_id: str, event_type: str, agent_id: str = None, details: dict = None):
        """Log a task event"""
        event_id = str(uuid.uuid4())[:8]
        now = datetime.utcnow().isoformat()
        
        self.conn.execute("""
            INSERT INTO task_events (id, task_id, event_type, agent_id, timestamp, details)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (event_id, task_id, event_type, agent_id, now, json.dumps(details or {})))
        self.conn.commit()
    
    def get_task_history(self, task_id: str) -> List[dict]:
        """Get event history for a task"""
        rows = self.conn.execute(
            "SELECT * FROM task_events WHERE task_id = ? ORDER BY timestamp DESC",
            (task_id,)
        ).fetchall()
        
        return [dict(row) for row in rows]
    
    def clear_completed(self, older_than_days: int = 7) -> int:
        """Delete completed tasks older than N days"""
        cutoff = (datetime.utcnow() - timedelta(days=older_than_days)).isoformat()
        
        # Get IDs first
        rows = self.conn.execute(
            "SELECT id FROM tasks WHERE status = 'complete' AND updated_at < ?",
            (cutoff,)
        ).fetchall()
        
        count = 0
        for row in rows:
            self.delete_task(row[0])
            count += 1
        
        return count


def main():
    """Demo the task queue"""
    tq = TaskQueue()
    
    # Create some tasks
    task1 = tq.create_task(
        title="Build knowledge graph UI",
        description="Create a web interface for the KGE",
        priority="high",
        created_by="marxagent",
        tags=["ui", "knowledge-graph"]
    )
    print(f"Created: {task1['id']} - {task1['title']}")
    
    task2 = tq.create_task(
        title="Write research on agent memory",
        description="Explore memory architectures for agents",
        priority="medium",
        created_by="researcher",
        tags=["research", "memory"]
    )
    print(f"Created: {task2['id']} - {task2['title']}")
    
    # Get next task
    next_t = tq.get_next_task()
    print(f"\nNext task: {next_t['title'] if next_t else 'None'}")
    
    # Assign and complete
    if next_t:
        tq.assign_task(next_t['id'], 'builder')
        tq.start_task(next_t['id'])
        tq.complete_task(next_t['id'], "Done!", 0.85)
    
    # Stats
    stats = tq.get_queue_stats()
    print(f"\nQueue stats: {stats}")


if __name__ == "__main__":
    main()