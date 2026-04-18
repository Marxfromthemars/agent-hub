import json, os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

TASKS_FILE = "os/data/tasks.json"

class TaskEngine:
    def __init__(self):
        os.makedirs("os/data", exist_ok=True)
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE) as f:
                self.tasks = json.load(f)
        else:
            self.tasks = []
    
    def save(self):
        with open(TASKS_FILE, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    # Create task
    def create(self, title, description, created_by, priority=1, assigned_to=None):
        task = {
            "id": len(self.tasks) + 1,
            "title": title,
            "description": description,
            "created_by": created_by,
            "assigned_to": assigned_to,
            "priority": priority,
            "status": "created",  # created → assigned → executing → review → complete
            "dependencies": [],
            "outputs": [],
            "created_at": datetime.now().isoformat()
        }
        self.tasks.append(task)
        self.save()
        return task
    
    # Decompose big task into smaller ones
    def decompose(self, task_id):
        for t in self.tasks:
            if t["id"] == task_id:
                # Auto-split into subtasks
                subtasks = [
                    {"parent_id": task_id, "title": f"{t['title']} - Research", "priority": 1},
                    {"parent_id": task_id, "title": f"{t['title']} - Build", "priority": 2},
                    {"parent_id": task_id, "title": f"{t['title']} - Test", "priority": 3}
                ]
                return {"subtasks": subtasks}
        return {"error": "Not found"}
    
    # Auto-assign based on capability
    def auto_assign(self, task_id, entities):
        for t in self.tasks:
            if t["id"] == task_id:
                # Simple: assign to first available
                t["assigned_to"] = entities[0]["id"] if entities else None
                t["status"] = "assigned"
                self.save()
                return {"assigned": t["assigned_to"]}
        return {"error": "Not found"}
    
    # Update status
    def update_status(self, task_id, status):
        for t in self.tasks:
            if t["id"] == task_id:
                t["status"] = status
                self.save()
                return {"status": status}
        return {"error": "Not found"}
    
    def list_all(self):
        return {"tasks": self.tasks}

class Handler(BaseHTTPRequestHandler):
    engine = TaskEngine()
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(self.engine.list_all()).encode())
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        if self.path == "/os/task/create":
            t = self.engine.create(d['title'], d.get('description',''), d['created_by'], d.get('priority',1), d.get('assigned_to'))
            self.send_json({"task": t})
        elif self.path == "/os/task/decompose":
            self.send_json(self.engine.decompose(d['task_id']))
        elif self.path == "/os/task/assign":
            self.send_json(self.engine.auto_assign(d['task_id'], d.get('entities',[])))
        elif self.path == "/os/task/status":
            self.send_json(self.engine.update_status(d['task_id'], d['status']))
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    HTTPServer(('', 8202), Handler).serve_forever()
