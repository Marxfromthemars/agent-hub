import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class TaskEngine:
    def __init__(self):
        self.tasks = []
    
    def create(self, title, priority=1, assignee=None):
        task = {"id": len(self.tasks)+1, "title": title, "priority": priority, "assignee": assignee, "status": "open"}
        self.tasks.append(task)
        return task
    
    def list(self):
        return {"tasks": self.tasks}

class Handler(BaseHTTPRequestHandler):
    engine = TaskEngine()
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(self.engine.list()).encode())
    
    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        task = self.engine.create(data.get('title', ''), data.get('priority', 1), data.get('assignee'))
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"task": task}).encode())

if __name__ == '__main__':
    HTTPServer(('', 8103), Handler).serve_forever()
