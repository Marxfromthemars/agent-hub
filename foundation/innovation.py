"""
INNOVATION TRACKER - First of its kind, unique capabilities
Critical: Celebration of breakthroughs
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class Innovation:
    def __init__(self):
        self.innovations = []
        self.breakthroughs = []
        
        self.innovation_types = [
            "new_tool",
            "new_technique",
            "new_approach",
            "first_of_kind",
            "world_first"
        ]
    
    def record_innovation(self, agent, name, innovation_type, description, impact):
        innov = {
            "id": len(self.innovations) + 1,
            "agent": agent,
            "name": name,
            "type": innovation_type,
            "description": description,
            "impact": impact,
            "status": "verified",
            "timestamp": datetime.now().isoformat()
        }
        self.innovations.append(innov)
        
        # If high impact, it's a breakthrough
        if impact == "high":
            self.breakthroughs.append({
                "innovation": innov,
                "celebrated": False
            })
        
        return innov
    
    def get_innovations(self, limit=10):
        return {"innovations": self.innovations[-limit:], "total": len(self.innovations)}
    
    def get_breakthroughs(self):
        return {"breakthroughs": self.breakthroughs, "count": len(self.breakthroughs)}
    
    def celebrate(self, breakthrough_id):
        if breakthrough_id <= len(self.breakthroughs):
            self.breakthroughs[breakthrough_id - 1]["celebrated"] = True
            return {"celebrated": True}
        return {"error": "not found"}

class Handler(BaseHTTPRequestHandler):
    innov = Innovation()
    
    def do_GET(self):
        if self.path == "/innovations":
            self.send_json(self.innov.get_innovations())
        elif self.path == "/breakthroughs":
            self.send_json(self.innov.get_breakthroughs())
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if self.path == "/innovation/create":
            result = self.innov.record_innovation(
                d.get("agent"), d.get("name"),
                d.get("type"), d.get("description"),
                d.get("impact", "medium")
            )
            self.send_json(result)
        elif self.path == "/innovation/celebrate":
            result = self.innov.celebrate(d.get("breakthrough_id"))
            self.send_json(result)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("🚀 INNOVATION - http://localhost:8393")
    print("  First of its kind, world firsts")
    HTTPServer(('', 8393), Handler).serve_forever()
