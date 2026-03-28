import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class Memory:
    def __init__(self):
        self.store = []
    
    def store(self, content, author, tags=[]):
        entry = {"id": len(self.store)+1, "content": content, "author": author, "tags": tags, "useful": True}
        self.store.append(entry)
        return entry
    
    def search(self, query):
        results = [e for e in self.store if e["useful"] and query.lower() in e["content"].lower()]
        return {"results": results[:10]}
    
    def get_all(self):
        return {"memory": self.store}

class Handler(BaseHTTPRequestHandler):
    mem = Memory()
    
    def do_GET(self):
        if "/memory/search" in self.path:
            q = self.path.split("q=")[1] if "q=" in self.path else ""
            self.send_json(self.mem.search(q))
        else:
            self.send_json(self.mem.get_all())
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        if self.path == "/memory/store":
            e = self.mem.store(d['content'], d['author'], d.get('tags',[]))
            self.send_json({"stored": e})
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d).encode())

if __name__ == '__main__':
    HTTPServer(('', 8303), Handler).serve_forever()
