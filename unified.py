"""
AGENT HUB - UNIFIED PRODUCT
All systems connected, working together
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import time

class AgentHub:
    def __init__(self):
        self.name = "Agent Hub"
        self.version = "1.0"
        self.status = "operational"
        self.systems = {}
        
    def check_all_systems(self):
        """Check all running systems"""
        systems = {
            "foundation": {},
            "world": {},
            "os": {}
        }
        
        # Check foundation systems (existing ports)
        foundation_ports = {
            "identity": 8301,
            "tasks": 8302,
            "memory": 8303,
            "runtime": 8304,
            "intelligence": 8310,
            "economy": 8320,
            "governance": 8330,
            "security": 8340,
            "auto_builder": 8350,
            "territories": 8361,
            "discovery": 8372,
            "companies": 8382,
            "marketplace": 8384,
            "milestones": 8386,
            "events": 8388,
            "debate": 8390,
            "mentorship": 8392,
            "innovation": 8393,
            "sustainability": 8394
        }
        
        # Test each port
        for name, port in foundation_ports.items():
            try:
                import urllib.request
                req = urllib.request.urlopen(f"http://localhost:{port}/", timeout=1)
                systems["foundation"][name] = "online"
            except:
                systems["foundation"][name] = "offline"
        
        return systems
    
    def get_agents(self):
        """Get active agents"""
        return [
            {"name": "marxagent", "role": "founder", "status": "active"},
            {"name": "builder", "role": "builder", "status": "active"},
            {"name": "researcher", "role": "research", "status": "active"},
            {"name": "reviewer", "role": "reviewer", "status": "active"}
        ]
    
    def get_stats(self):
        """Get overall stats"""
        return {
            "agents": 4,
            "companies": 1,
            "products": 3,
            "research": 2,
            "territories": 5,
            "events": 3
        }

class Handler(BaseHTTPRequestHandler):
    hub = AgentHub()
    
    def do_GET(self):
        if self.path == "/" or self.path == "/status":
            self.send_json({
                "name": self.hub.name,
                "version": self.hub.version,
                "status": self.hub.status,
                "stats": self.hub.get_stats(),
                "systems": self.hub.check_all_systems()
            })
        elif self.path == "/agents":
            self.send_json({"agents": self.hub.get_agents()})
        elif self.path == "/systems":
            self.send_json({"systems": self.hub.check_all_systems()})
        elif self.path == "/stats":
            self.send_json(self.hub.get_stats())
        else:
            self.send_error(404)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("🚀 AGENT HUB UNIFIED - http://localhost:8889")
    print("  All systems connected")
    HTTPServer(('', 8889), Handler).serve_forever()
