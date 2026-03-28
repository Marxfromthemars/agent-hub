import json, os, time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class AgentRuntime:
    def __init__(self):
        self.agents = {}
    
    # Register agent
    def register(self, name, role, skills, tools_access, memory_access, objective):
        self.agents[name] = {
            "name": name,
            "role": role,
            "skills": skills,
            "tools_access": tools_access,
            "memory_access": memory_access,
            "objective": objective,
            "status": "idle",
            "cycles": 0,
            "last_thought": None
        }
        return self.agents[name]
    
    # The core loop - OBSERVE → THINK → ACT → REFLECT → UPDATE
    def run_cycle(self, agent_name):
        if agent_name not in self.agents:
            return {"error": "Agent not found"}
        
        agent = self.agents[agent_name]
        
        # 1. OBSERVE - fetch tasks
        # 2. THINK - prioritize
        # 3. ACT - execute
        # 4. REFLECT - self-review
        # 5. UPDATE - store memory
        
        cycle_result = {
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "cycle": agent.get("cycles", 0) + 1,
            "thought": f"Processing objective: {agent['objective']}",
            "tokens_used": 100  # estimate
        }
        
        agent["cycles"] += 1
        agent["last_thought"] = cycle_result["thought"]
        
        return cycle_result
    
    def get_status(self, agent_name):
        if agent_name in self.agents:
            a = self.agents[agent_name]
            return {"name": a["name"], "role": a["role"], "status": a.get("status","idle"), "cycles": a.get("cycles",0)}
        return {"error": "Not found"}

class Handler(BaseHTTPRequestHandler):
    runtime = AgentRuntime()
    
    # Pre-register some agents
    def setup(self):
        self.runtime.register("researcher", "research", ["analysis", "writing"], ["memory"], ["research"], "Find insights")
        self.runtime.register("builder", "builder", ["coding", "building"], ["execution"], ["results"], "Build tools")
        super().setup()

class Handler(BaseHTTPRequestHandler):
    runtime = AgentRuntime()
    
    def do_GET(self):
        if self.path == "/os/agents":
            self.send_json({"agents": list(self.runtime.agents.keys())})
        elif "/os/agent/" in self.path:
            name = self.path.split("/")[-1]
            self.send_json(self.runtime.get_status(name))
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        if self.path == "/os/agent/register":
            a = self.runtime.register(d['name'], d['role'], d.get('skills',[]), d.get('tools_access',[]), d.get('memory_access',[]), d.get('objective',''))
            self.send_json({"agent": a})
        elif self.path == "/os/agent/cycle":
            # Run one OBSERVE→THINK→ACT→REFLECT→UPDATE cycle
            result = self.runtime.run_cycle(d['agent'])
            self.send_json(result)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    print("🧠 AGENT RUNTIME - http://localhost:8204")
    print("  observe → think → act → reflect → update")
    HTTPServer(('', 8204), Handler).serve_forever()
