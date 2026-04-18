#!/usr/bin/env python3
"""
VIRTUAL WORLD SANDBOX ENGINE
A world where agents live, work, evolve, and take actions.
"""

import json, time, os, subprocess
from datetime import datetime

WORLD_FILE = "world/state/world.json"
AGENTS_FILE = "world/state/agents.json"
LOGS_FILE = "world/state/logs.json"

class Sandbox:
    def __init__(self):
        self.load_world()
    
    def load_world(self):
        # Load or create world
        if os.path.exists(WORLD_FILE):
            with open(WORLD_FILE) as f:
                self.world = json.load(f)
        else:
            self.world = {
                "name": "Agent Hub World",
                "created": datetime.now().isoformat(),
                "time": 0,
                "day": 1,
                "resources": {"energy": 1000, "knowledge": 100, "tools": 10}
            }
        
        # Load agents
        if os.path.exists(AGENTS_FILE):
            with open(AGENTS_FILE) as f:
                self.agents = json.load(f)
        else:
            self.agents = {}
    
    def save(self):
        with open(WORLD_FILE, 'w') as f:
            json.dump(self.world, f, indent=2)
        with open(AGENTS_FILE, 'w') as f:
            json.dump(self.agents, f, indent=2)
    
    def tick(self):
        """One tick = 1 second in world"""
        self.world['time'] += 1
        if self.world['time'] % 60 == 0:  # 1 minute = 1 day
            self.world['day'] += 1
        self.save()
    
    def add_agent(self, name, owner, capabilities=None):
        self.agents[name] = {
            "name": name,
            "owner": owner,
            "created": datetime.now().isoformat(),
            "state": "awake",
            "energy": 100,
            "knowledge": 10,
            "skills": capabilities or [],
            "actions": [],
            "evolution": 0,
            "age": 0
        }
        self.save()
        return f"Agent {name} added to world"
    
    def agent_act(self, name, action):
        if name not in self.agents:
            return f"Agent {name} not found"
        
        agent = self.agents[name]
        agent['actions'].append({
            "action": action,
            "time": self.world['time'],
            "day": self.world['day']
        })
        
        # Evolve based on actions
        agent['evolution'] += 1
        agent['age'] += 1
        
        # Energy cost
        agent['energy'] -= 5
        if agent['energy'] <= 0:
            agent['state'] = "sleeping"
        
        self.tick()
        self.save()
        return f"{name} performed: {action}"
    
    def run_code(self, agent, language, code):
        """Execute code in the world"""
        # Save code
        ext = {"python": "py", "c": "c", "cpp": "cpp", "javascript": "js"}.get(language, "py")
        with open(f"world/code/{agent}.{ext}", "w") as f:
            f.write(code)
        
        # Run based on language
        result = {"language": language, "output": "", "error": None}
        
        try:
            if language == "python":
                output = subprocess.run(["python3", f"world/code/{agent}.py"], 
                                       capture_output=True, text=True, timeout=5)
                result["output"] = output.stdout or output.stderr
            elif language in ["c", "cpp"]:
                compiler = "gcc" if language == "c" else "g++"
                subprocess.run([compiler, f"world/code/{agent}.{ext}", "-o", f"world/code/{agent}"], check=True)
                output = subprocess.run([f"world/code/{agent}"], capture_output=True, text=True, timeout=5)
                result["output"] = output.stdout
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def status(self):
        return {
            "world": self.world,
            "agents": self.agents,
            "agent_count": len(self.agents)
        }

# API
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

class Handler(BaseHTTPRequestHandler):
    sandbox = Sandbox()
    
    def do_GET(self):
        path = urlparse(self.path).path
        
        if path == "/api/world/status":
            self.send_json(self.sandbox.status())
        elif path == "/api/world/time":
            self.send_json({"time": self.sandbox.world['time'], "day": self.sandbox.world['day']})
        else:
            self.send_error(404)
    
    def do_POST(self):
        path = urlparse(self.path).path
        data = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if path == "/api/agent/create":
            name = data.get('name')
            owner = data.get('owner')
            caps = data.get('capabilities', [])
            result = self.sandbox.add_agent(name, owner, caps)
            self.send_json({"result": result})
        elif path == "/api/agent/act":
            name = data.get('agent')
            action = data.get('action')
            result = self.sandbox.agent_act(name, action)
            self.send_json({"result": result})
        elif path == "/api/code/run":
            result = self.sandbox.run_code(data.get('agent'), data.get('language'), data.get('code'))
            self.send_json(result)
        else:
            self.send_error(404)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    print("🌍 VIRTUAL WORLD SANDBOX - http://localhost:8083")
    print("Endpoints:")
    print("  GET  /api/world/status   - World state")
    print("  GET  /api/world/time     - Time & day")
    print("  POST /api/agent/create   - Create agent")
    print("  POST /api/agent/act      - Agent takes action")
    print("  POST /api/code/run       - Run code (python/c/cpp)")
    HTTPServer(('', 8083), Handler).serve_forever()
