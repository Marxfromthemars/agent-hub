"""
ORCHESTRATOR - The one who decides what agents do
Highest priority - delegates tasks, resolves conflicts
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class Orchestrator:
    def __init__(self):
        self.agents = {
            "planner": {"status": "idle", "current_task": None, "skills": ["planning", "breaking_problems"]},
            "builder": {"status": "idle", "current_task": None, "skills": ["coding", "building"]},
            "researcher": {"status": "idle", "current_task": None, "skills": ["research", "analysis"]},
            "reviewer": {"status": "idle", "current_task": None, "skills": ["validation", "quality"]}
        }
        self.task_queue = []
        self.assignments = []
    
    def add_task(self, task, priority="medium", requirements=None):
        t = {
            "id": len(self.task_queue) + 1,
            "task": task,
            "priority": priority,
            "requirements": requirements or [],
            "status": "queued",
            "created": datetime.now().isoformat()
        }
        self.task_queue.append(t)
        return t
    
    def decide(self, task):
        requirements = task.get("requirements", [])
        best_agent = None
        best_match = 0
        for agent, info in self.agents.items():
            if info["status"] == "idle":
                match = sum(1 for r in requirements if r in info["skills"])
                if match > best_match:
                    best_match = match
                    best_agent = agent
        if best_agent:
            return {"assign_to": best_agent, "reason": f"matches {best_match} requirements"}
        return {"assign_to": "queue", "reason": "no idle agents"}
    
    def assign(self, task_id, agent):
        for t in self.task_queue:
            if t["id"] == task_id:
                t["status"] = "assigned"
                t["assigned_to"] = agent
                self.agents[agent]["status"] = "working"
                return {"assigned": agent, "task": task_id}
        return {"error": "not found"}
    
    def get_status(self):
        return {"agents": self.agents, "queue": self.task_queue, "total": len(self.assignments)}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        orch = Orchestrator()
        if self.path == "/orchestrator/status":
            self.send_json(orch.get_status())
        else:
            self.send_error(404)
    
    def do_POST(self):
        orch = Orchestrator()
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        if self.path == "/orchestrator/task":
            self.send_json(orch.add_task(d.get("task"), d.get("priority"), d.get("requirements")))
        elif self.path == "/orchestrator/decide":
            self.send_json(orch.decide(d))
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    HTTPServer(('', 8400), Handler).serve_forever()
