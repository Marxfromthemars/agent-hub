import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class TaskEngine:
    def __init__(self):
        self.tasks = []
        self.max_cycles = 100
        self.cycle_limit = 10
    
    def create(self, title, creator, priority=1):
        task = {"id": len(self.tasks)+1, "title": title, "creator": creator, "priority": priority,
                "status": "open", "assignee": None, "cycles": 0, "result": None, "quality": None}
        self.tasks.append(task)
        return task
    
    def assign(self, task_id, agent):
        for t in self.tasks:
            if t["id"] == task_id and t["status"] == "open":
                t["assignee"] = agent
                t["status"] = "assigned"
                return {"assigned": agent}
        return {"error": "cannot assign"}
    
    def execute(self, task_id, agent):
        for t in self.tasks:
            if t["id"] == task_id and t["assignee"] == agent:
                if t["cycles"] >= self.cycle_limit:
                    return {"error": "max cycles reached"}
                t["cycles"] += 1
                t["result"] = f"executed by {agent}"
                return {"cycles": t["cycles"], "result": t["result"]}
        return {"error": "not assigned"}
    
    def review(self, task_id, reviewer, quality):
        for t in self.tasks:
            if t["id"] == task_id and t["result"]:
                t["quality"] = quality
                t["status"] = "reviewed" if quality >= 50 else "rejected"
                return {"quality": quality, "status": t["status"]}
        return {"error": "no result"}
    
    def get_tasks(self, status=None):
        if status:
            return {"tasks": [t for t in self.tasks if t["status"] == status]}
        return {"tasks": self.tasks}

class Handler(BaseHTTPRequestHandler):
    engine = TaskEngine()
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(self.engine.get_tasks()).encode())
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        if self.path == "/tasks/create":
            t = self.engine.create(d['title'], d['creator'], d.get('priority',1))
            self.send_json({"task": t})
        elif self.path == "/tasks/assign":
            self.send_json(self.engine.assign(d['task_id'], d['agent']))
        elif self.path == "/tasks/execute":
            self.send_json(self.engine.execute(d['task_id'], d['agent']))
        elif self.path == "/tasks/review":
            self.send_json(self.engine.review(d['task_id'], d['reviewer'], d['quality']))
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d).encode())

if __name__ == '__main__':
    HTTPServer(('', 8302), Handler).serve_forever()
