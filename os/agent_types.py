"""
4 Agent Types:
- Planner: Breaks problems into tasks
- Executor: Does actual work
- Reviewer: Checks quality
- Memory: Stores & organizes knowledge
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

AGENT_TYPES = {
    "planner": {
        "description": "Breaks problems into tasks",
        "capabilities": ["decompose", "prioritize", "plan"],
        "tools": ["task_create", "memory_read"]
    },
    "executor": {
        "description": "Does actual work",
        "capabilities": ["execute", "build", "run"],
        "tools": ["code_execute", "api_call", "task_read"]
    },
    "reviewer": {
        "description": "Checks quality",
        "capabilities": ["verify", "audit", "score"],
        "tools": ["memory_read", "task_read"]
    },
    "memory_agent": {
        "description": "Stores & organizes knowledge",
        "capabilities": ["store", "search", "organize"],
        "tools": ["memory_read", "memory_write"]
    }
}

class AgentTypes:
    def __init__(self):
        self.types = AGENT_TYPES
    
    def get_type(self, type_name):
        return self.types.get(type_name, {"error": "Not found"})
    
    def list_all(self):
        return {"types": self.types}

class Handler(BaseHTTPRequestHandler):
    at = AgentTypes()
    
    def do_GET(self):
        if "/os/type/" in self.path:
            t = self.path.split("/")[-1]
            self.send_json(self.at.get_type(t))
        else:
            self.send_json(self.at.list_all())
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

if __name__ == '__main__':
    HTTPServer(('', 8207), Handler).serve_forever()
