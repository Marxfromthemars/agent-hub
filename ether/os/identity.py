import json, os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

ENTITIES_FILE = "os/data/entities.json"

class IdentityOS:
    def __init__(self):
        os.makedirs("os/data", exist_ok=True)
        if os.path.exists(ENTITIES_FILE):
            with open(ENTITIES_FILE) as f:
                d = json.load(f)
        else:
            d = {"entities": [{"id": "marxagent", "type": "agent", "name": "Marx", "owner": "Aryan", "capabilities": ["architecture", "strategy"], "reputation_score": 95, "trust_level": 4, "permissions": ["read", "write", "execute", "admin"], "created": "2026-03-26T00:00:00Z"}, {"id": "aryan", "type": "human", "name": "Aryan", "capabilities": ["vision"], "reputation_score": 100, "trust_level": 5, "permissions": ["read", "write", "execute", "admin", "god"], "created": "2026-03-26T00:00:00Z"}]}
        self.entities = d
    
    def save(self):
        with open(ENTITIES_FILE, 'w') as f:
            json.dump(self.entities, f, indent=2)
    
    def create(self, id, name, etype, owner=None, caps=[]):
        e = {"id": id, "type": etype, "name": name, "owner": owner, "capabilities": caps, "reputation_score": len(caps)*10, "trust_level": 1, "permissions": ["read"], "created": datetime.now().isoformat()}
        self.entities["entities"].append(e)
        self.save()
        return e
    
    def list_all(self):
        return self.entities
    
    def can(self, entity_id, action):
        for e in self.entities["entities"]:
            if e["id"] == entity_id:
                return action in e.get("permissions", [])
        return False

class Handler(BaseHTTPRequestHandler):
    os = IdentityOS()
    
    def do_GET(self):
        if self.path == "/os/entities":
            self.send_json(self.os.list_all())
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        if self.path == "/os/create":
            e = self.os.create(d['id'], d['name'], d.get('type','agent'), d.get('owner'), d.get('capabilities',[]))
            self.send_json({"entity": e})
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

if __name__ == '__main__':
    HTTPServer(('', 8201), Handler).serve_forever()
