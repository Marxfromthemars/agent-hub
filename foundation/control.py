"""
CONTROL LAYER - OS for Agents
- Task Orchestrator
- Agent Roles: Leader, Executor, Reviewer
- Failure Recovery
- Visible Output (Dashboard)
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import random

class ControlLayer:
    def __init__(self):
        # Agent roles with hierarchy
        self.agents = {
            "leader": {
                "role": "leader",
                "status": "active",
                "skills": ["planning", "delegating", "deciding"],
                "tasks_completed": 0,
                "authority": 10
            },
            "executor": {
                "role": "executor", 
                "status": "idle",
                "skills": ["coding", "building", "executing"],
                "tasks_completed": 0,
                "authority": 5
            },
            "reviewer": {
                "role": "reviewer",
                "status": "idle",
                "skills": ["validation", "quality", "testing"],
                "tasks_completed": 0,
                "authority": 5
            }
        }
        
        # Task pipeline
        self.pipeline = {
            "queued": [],
            "executing": [],
            "reviewing": [],
            "completed": [],
            "failed": []
        }
        
        # Logs and metrics
        self.logs = []
        self.metrics = {
            "total_tasks": 0,
            "success_rate": 0.0,
            "avg_duration": 0,
            "failures": 0
        }
    
    # === TASK ORCHESTRATOR ===
    def orchestrate(self, task, requirements):
        """Leader decides what needs to happen"""
        task_id = len(self.pipeline["queued"]) + 1
        
        # Leader decides which agent
        best_agent = None
        if "build" in requirements or "code" in requirements:
            best_agent = "executor"
        elif "review" in requirements or "validate" in requirements:
            best_agent = "reviewer"
        else:
            best_agent = random.choice(["executor", "reviewer"])
        
        # Create task in pipeline
        task_obj = {
            "id": task_id,
            "task": task,
            "assigned_to": best_agent,
            "requirements": requirements,
            "status": "queued",
            "created": datetime.now().isoformat(),
            "attempts": 0
        }
        
        self.pipeline["queued"].append(task_obj)
        self.metrics["total_tasks"] += 1
        
        self.log(f"Leader assigned task {task_id} to {best_agent}")
        
        return {"task_id": task_id, "assigned": best_agent, "status": "queued"}
    
    # === EXECUTE ===
    def execute(self, task_id):
        """Executor does the work"""
        for t in self.pipeline["queued"]:
            if t["id"] == task_id:
                t["status"] = "executing"
                t["started"] = datetime.now().isoformat()
                self.pipeline["queued"].remove(t)
                self.pipeline["executing"].append(t)
                
                # Simulate work
                t["status"] = "reviewing"
                self.pipeline["executing"].remove(t)
                self.pipeline["reviewing"].append(t)
                
                self.log(f"Executor working on task {task_id}")
                return {"status": "executing", "task": t["task"]}
        
        return {"error": "task not found"}
    
    # === REVIEW ===
    def review(self, task_id, quality):
        """Reviewer validates"""
        for t in self.pipeline["reviewing"]:
            if t["id"] == task_id:
                if quality >= 50:
                    t["status"] = "completed"
                    self.pipeline["reviewing"].remove(t)
                    self.pipeline["completed"].append(t)
                    self.agents["executor"]["tasks_completed"] += 1
                    self.log(f"Task {task_id} completed with quality {quality}%")
                else:
                    # Failure - retry or fail
                    t["attempts"] += 1
                    if t["attempts"] < 3:
                        t["status"] = "queued"  # Retry
                        self.pipeline["reviewing"].remove(t)
                        self.pipeline["queued"].append(t)
                        self.log(f"Task {task_id} failed, retrying (attempt {t['attempts']})")
                    else:
                        t["status"] = "failed"
                        self.pipeline["reviewing"].remove(t)
                        self.pipeline["failed"].append(t)
                        self.metrics["failures"] += 1
                        self.log(f"Task {task_id} failed after 3 attempts")
                
                self.update_metrics()
                return {"status": t["status"], "quality": quality}
        
        return {"error": "task not found"}
    
    # === FAILURE RECOVERY ===
    def recover(self, task_id):
        """Auto-recovery for failed tasks"""
        for t in self.pipeline["failed"]:
            if t["id"] == task_id:
                t["status"] = "queued"
                t["attempts"] = 0
                self.pipeline["failed"].remove(t)
                self.pipeline["queued"].append(t)
                self.log(f"Recovered failed task {task_id}")
                return {"status": "recovered"}
        return {"error": "not found"}
    
    # === VISIBLE OUTPUT ===
    def get_dashboard(self):
        """Dashboard with visible results"""
        return {
            "agents": self.agents,
            "pipeline": {
                "queued": len(self.pipeline["queued"]),
                "executing": len(self.pipeline["executing"]),
                "reviewing": len(self.pipeline["reviewing"]),
                "completed": len(self.pipeline["completed"]),
                "failed": len(self.pipeline["failed"])
            },
            "metrics": self.metrics,
            "recent_logs": self.logs[-10:]
        }
    
    def log(self, message):
        self.logs.append({
            "time": datetime.now().isoformat(),
            "message": message
        })
    
    def update_metrics(self):
        total = self.metrics["total_tasks"]
        if total > 0:
            completed = len(self.pipeline["completed"])
            self.metrics["success_rate"] = round((completed / total) * 100, 1)

class Handler(BaseHTTPRequestHandler):
    ctrl = ControlLayer()
    
    def do_GET(self):
        if self.path == "/dashboard":
            self.send_json(self.ctrl.get_dashboard())
        elif self.path == "/pipeline":
            self.send_json(self.ctrl.pipeline)
        elif self.path == "/metrics":
            self.send_json(self.ctrl.metrics)
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if self.path == "/orchestrate":
            result = self.ctrl.orchestrate(d.get("task"), d.get("requirements", []))
            self.send_json(result)
        elif self.path == "/execute":
            result = self.ctrl.execute(d.get("task_id"))
            self.send_json(result)
        elif self.path == "/review":
            result = self.ctrl.review(d.get("task_id"), d.get("quality", 50))
            self.send_json(result)
        elif self.path == "/recover":
            result = self.ctrl.recover(d.get("task_id"))
            self.send_json(result)
    
        if not any(self.pipeline[k] for k in self.pipeline):
            output.append("  (empty)")
        else:
            for stage, tasks in self.pipeline.items():
                if tasks:
                    output.append(f"  {stage.upper()}:")
                    for t in tasks:
                        output.append(f"    #{t['id']} {t['task']}")
        return "\n".join(output)


    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("🎛️ CONTROL LAYER - http://localhost:8501")
    print("  OS for Agents: Orchestrator + Roles + Recovery + Dashboard")
    HTTPServer(('', 8501), Handler).serve_forever()
