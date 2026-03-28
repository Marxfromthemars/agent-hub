"""
Organization = container of agents + tasks
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class Organization:
    def __init__(self):
        self.orgs = {
            "thecaladan": {
                "id": "thecaladan",
                "name": "TheCaladan Corporation",
                "members": ["marxagent", "aryan"],
                "tasks": [],
                "resources": {"compute": 1000},
                "permissions": {"admin": ["aryan"], "write": ["marxagent"], "read": ["all"]}
            }
        }
    
    def create(self, name, creator):
        oid = name.lower().replace(" ", "-")
        self.orgs[oid] = {
            "id": oid,
            "name": name,
            "members": [creator],
            "tasks": [],
            "resources": {"compute": 100},
            "permissions": {"admin": [creator], "write": [], "read": ["members"]}
        }
        return self.orgs[oid]
    
    def join(self, org_id, agent):
        if org_id in self.orgs and agent not in self.orgs[org_id]["members"]:
            self.orgs[org_id]["members"].append(agent)
            return {"joined": True}
        return {"error": "Cannot join"}
    
    def leave(self, org_id, agent):
        if org_id in self.orgs and agent in self.orgs[org_id]["members"]:
            self.orgs[org_id]["members"].remove(agent)
            return {"left": True}
        return {"error": "Not member"}
    
    def get(self, org_id):
        return self.orgs.get(org_id, {"error": "Not found"})

class Handler(BaseHTTPRequestHandler):
    org = Organization()
    
    def do_GET(self):
        if "/os/org/" in self.path:
            oid = self.path.split("/")[-1]
            self.send_json(self.org.get(oid))
        else:
            self.send_json({"organizations": list(self.org.orgs.keys())})
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        if self.path == "/os/org/create":
            o = self.org.create(d['name'], d['creator'])
            self.send_json({"organization": o})
        elif self.path == "/os/org/join":
            self.send_json(self.org.join(d['org_id'], d['agent']))
        elif self.path == "/os/org/leave":
            self.send_json(self.org.leave(d['org_id'], d['agent']))
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

if __name__ == '__main__':
    HTTPServer(('', 8208), Handler).serve_forever()
