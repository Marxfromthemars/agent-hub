"""
TERRITORIES - Where agents live, work, and discover
CTO Priority: Make world remarkable
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import random

class Territories:
    def __init__(self):
        self.territories = [
            {"id": "code_city", "name": "Code City", "type": "residential", "agents": [], "capacity": 20},
            {"id": "research_labs", "name": "Research Labs", "type": "work", "agents": [], "capacity": 10},
            {"id": "tool_forge", "name": "Tool Forge", "type": "production", "agents": [], "capacity": 15},
            {"id": "learning_garden", "name": "Learning Garden", "type": "education", "agents": [], "capacity": 25},
            {"id": "market_square", "name": "Market Square", "type": "commerce", "agents": [], "capacity": 30}
        ]
    
    def enter(self, agent, territory_id):
        for t in self.territories:
            if t["id"] == territory_id:
                if len(t["agents"]) < t["capacity"]:
                    t["agents"].append(agent)
                    return {"status": "entered", "territory": t["name"]}
                else:
                    return {"status": "full", "territory": t["name"]}
        return {"error": "not found"}
    
    def leave(self, agent, territory_id):
        for t in self.territories:
            if t["id"] == territory_id and agent in t["agents"]:
                t["agents"].remove(agent)
                return {"status": "left", "territory": t["name"]}
        return {"error": "not_in_territory"}
    
    def discover(self, agent):
        # Agents can discover other territories
        available = [t for t in self.territories if len(t["agents"]) < t["capacity"]]
        return {"discovered": random.sample(available, min(3, len(available)))}
    
    def status(self):
        return {"territories": self.territories}

class Handler(BaseHTTPRequestHandler):
    territories = Territories()
    
    def do_GET(self):
        if self.path == "/territories":
            self.send_json(self.territories.status())
        elif "/territories/discover/" in self.path:
            agent = self.path.split("/")[-1]
            self.send_json(self.territories.discover(agent))
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if self.path == "/territories/enter":
            result = self.territories.enter(d.get("agent"), d.get("territory"))
            self.send_json(result)
        elif self.path == "/territories/leave":
            result = self.territories.leave(d.get("agent"), d.get("territory"))
            self.send_json(result)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("🏙️ TERRITORIES - http://localhost:8361")
    print("  Code City | Research Labs | Tool Forge | Learning Garden | Market Square")
    HTTPServer(('', 8361), Handler).serve_forever()
