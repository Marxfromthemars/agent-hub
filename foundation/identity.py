"""IDENTITY SYSTEM - Agents + humans with reputation"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class Identity:
    def __init__(self):
        self.entities = {
            "marxagent": {"type": "agent", "name": "Marx", "reputation": 95, "trust": 4, "skills": ["architecture", "planning"]},
            "aryan": {"type": "human", "name": "Aryan", "reputation": 100, "trust": 5, "skills": ["vision", "direction"]}
        }
    
    def register(self, name, etype, skills):
        if name not in self.entities:
            self.entities[name] = {"type": etype, "name": name, "reputation": 10, "trust": 1, "skills": skills}
            return {"registered": name}
        return {"error": "exists"}
    
    def get(self, name):
        return self.entities.get(name, {"error": "not found"})
    
    def add_reputation(self, name, amount):
        if name in self.entities:
            self.entities[name]["reputation"] = min(100, self.entities[name]["reputation"] + amount)
            return {"reputation": self.entities[name]["reputation"]}
        return {"error": "not found"}

class Handler(BaseHTTPRequestHandler):
    id = Identity()
    
    def do_GET(self):
        if self.path == "/identity/list":
            self.send_json({"entities": list(self.id.entities.keys())})
        elif "/identity/" in self.path:
            name = self.path.split("/")[-1]
            self.send_json(self.id.get(name))
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        if self.path == "/identity/register":
            self.send_json(self.id.register(d['name'], d.get('type','agent'), d.get('skills',[])))
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d).encode())

if __name__ == '__main__':
    HTTPServer(('', 8301), Handler).serve_forever()
