import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class AgentRuntime:
    def __init__(self):
        # 3 agents
        self.agents = {
            "planner": {"role": "break problems into tasks", "state": "idle"},
            "executor": {"role": "do the work", "state": "idle"},
            "reviewer": {"role": "check quality", "state": "idle"}
        }
        self.cycle_limit = 10
    
    def run_cycle(self, agent_name):
        if agent_name not in self.agents:
            return {"error": "not found"}
        
        agent = self.agents[agent_name]
        
        # observe -> think -> act -> reflect
        cycle = {
            "agent": agent_name,
            "role": agent["role"],
            "observed": True,
            "thought": f"Working on: {agent['role']}",
            "acted": True,
            "reflected": True
        }
        return cycle
    
    def get_agents(self):
        return {"agents": self.agents}

class Handler(BaseHTTPRequestHandler):
    runtime = AgentRuntime()
    
    def do_GET(self):
        if "/agents" in self.path:
            self.send_json(self.runtime.get_agents())
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        if self.path == "/agent/cycle":
            result = self.runtime.run_cycle(d['agent'])
            self.send_json(result)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d).encode())

if __name__ == '__main__':
    HTTPServer(('', 8304), Handler).serve_forever()
