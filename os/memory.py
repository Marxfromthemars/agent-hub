import json, os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import hashlib

MEMORY_FILE = "os/data/memory.json"

class MemoryOS:
    def __init__(self):
        os.makedirs("os/data", exist_ok=True)
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE) as f:
                self.memory = json.load(f)
        else:
            self.memory = {"research": [], "results": [], "conversations": []}
    
    def save(self):
        with open(MEMORY_FILE, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    # Store memory
    def store(self, mtype, content, contributor, linked_tasks=[]):
        mid = hashlib.sha256(f"{content}{datetime.now()}".encode()).hexdigest()[:12]
        
        entry = {
            "id": mid,
            "type": mtype,  # research, result, conversation
            "content": content,
            "contributors": [contributor],
            "timestamp": datetime.now().isoformat(),
            "linked_tasks": linked_tasks,
            "version": 1
        }
        
        if mtype == "research":
            self.memory["research"].append(entry)
        elif mtype == "result":
            self.memory["results"].append(entry)
        else:
            self.memory["conversations"].append(entry)
        
        self.save()
        return entry
    
    # Search (simple keyword for now - vector would be upgrade)
    def search(self, query):
        results = []
        for category in ["research", "results", "conversations"]:
            for m in self.memory.get(category, []):
                if query.lower() in m.get("content", "").lower():
                    results.append(m)
        return {"results": results[:10]}
    
    # Get public vs private
    def get_public(self):
        return {"research": self.memory.get("research", [])}
    
    def list_all(self):
        return self.memory

class Handler(BaseHTTPRequestHandler):
    mem = MemoryOS()
    
    def do_GET(self):
        if "/os/memory/search" in self.path:
            q = self.path.split("q=")[1] if "q=" in self.path else ""
            self.send_json(self.mem.search(q))
        elif self.path == "/os/memory/public":
            self.send_json(self.mem.get_public())
        else:
            self.send_json(self.mem.list_all())
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        if self.path == "/os/memory/store":
            m = self.mem.store(d['type'], d['content'], d['contributor'], d.get('linked_tasks', []))
            self.send_json({"stored": m})

    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    HTTPServer(('', 8203), Handler).serve_forever()
