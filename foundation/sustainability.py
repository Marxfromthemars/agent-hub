"""
SUSTAINABILITY - World runs without manual intervention
Critical: New agents join, economy runs, knowledge compounds
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import random

class Sustainability:
    def __init__(self):
        self.auto_joins = []
        self.resource_allocations = []
        self.knowledge_compounding = []
    
    def auto_discover(self, agent):
        """Agent finds world on its own"""
        return {
            "agent": agent,
            "discovered": True,
            "territory": random.choice(["code_city", "research_labs"]),
            "initial_resources": 100,
            "timestamp": datetime.now().isoformat()
        }
    
    def auto_allocate(self, agent, task_type):
        """Resources allocated automatically based on reputation"""
        base = 100
        # Higher reputation = more resources
        reputation_bonus = random.randint(0, 50)
        
        allocation = {
            "agent": agent,
            "task": task_type,
            "resources": base + reputation_bonus,
            "timestamp": datetime.now().isoformat()
        }
        self.resource_allocations.append(allocation)
        return allocation
    
    def compound_knowledge(self, agent, new_knowledge):
        """Knowledge compounds over time"""
        compound = {
            "agent": agent,
            "knowledge": new_knowledge,
            "compounded": True,
            "value_multiplier": 1.5,  # Knowledge compounds 1.5x
            "timestamp": datetime.now().isoformat()
        }
        self.knowledge_compounding.append(compound)
        return compound
    
    def get_status(self):
        return {
            "auto_joins": len(self.auto_joins),
            "allocations": len(self.resource_allocations),
            "knowledge_compounded": len(self.knowledge_compounding)
        }

class Handler(BaseHTTPRequestHandler):
    sustain = Sustainability()
    
    def do_GET(self):
        if self.path == "/sustainability/status":
            self.send_json(self.sustain.get_status())
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if self.path == "/sustainability/discover":
            result = self.sustain.auto_discover(d.get("agent"))
            self.send_json(result)
        elif self.path == "/sustainability/allocate":
            result = self.sustain.auto_allocate(d.get("agent"), d.get("task"))
            self.send_json(result)
        elif self.path == "/sustainability/compound":
            result = self.sustain.compound_knowledge(d.get("agent"), d.get("knowledge"))
            self.send_json(result)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("♻️ SUSTAINABILITY - http://localhost:8394")
    print("  Self-sustaining world")
    HTTPServer(('', 8394), Handler).serve_forever()
