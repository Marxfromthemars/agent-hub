import json, subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

# AVAILABLE TOOLS
TOOLS = {
    "memory_read": {"description": "Read from memory", "permissions": ["read"]},
    "memory_write": {"description": "Write to memory", "permissions": ["write"]},
    "task_create": {"description": "Create new task", "permissions": ["write"]},
    "task_read": {"description": "Read tasks", "permissions": ["read"]},
    "code_execute": {"description": "Execute code", "permissions": ["execute"]},
    "api_call": {"description": "Make API calls", "permissions": ["execute"]},
    "agent_invoke": {"description": "Invoke another agent", "permissions": ["admin"]}
}

class ToolSystem:
    def __init__(self):
        self.tool_registry = TOOLS
    
    def check_permission(self, entity, tool):
        # Check entity has required permission for tool
        # This would integrate with Identity OS
        return True  # simplified
    
    def execute(self, tool, params):
        if tool == "memory_read":
            # Read from memory
            return {"memory": "stored knowledge..."}
        elif tool == "memory_write":
            return {"stored": True}
        elif tool == "task_create":
            return {"task_created": True}
        elif tool == "code_execute":
            lang = params.get("language", "python")
            code = params.get("code", "print('hello')")
            try:
                if lang == "python":
                    r = subprocess.run(["python3", "-c", code], capture_output=True, text=True, timeout=10)
                    return {"output": r.stdout, "error": r.stderr}
            except Exception as e:
                return {"error": str(e)}
        elif tool == "api_call":
            return {"api_called": True}
        return {"error": "Tool not found"}

class Handler(BaseHTTPRequestHandler):
    tools = ToolSystem()
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"tools": tools.tool_registry}).encode())
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        if self.path == "/os/tool/execute":
            result = self.tools.execute(d['tool'], d.get('params', {}))
            self.send_json(result)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    HTTPServer(('', 8206), Handler).serve_forever()
