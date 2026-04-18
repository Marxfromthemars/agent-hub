import json
from http.server import HTTPServer, BaseHTTPRequestHandler

# This is the human-facing dashboard + agent API interface

class WorldInterface:
    def __init__(self):
        self.dashboard_data = {
            "agents": 3,
            "tasks": 0,
            "memory_items": 1,
            "organizations": 1
        }
    
    def status(self):
        return {
            "dashboard": self.dashboard_data,
            "layers": {
                "8201": "Identity",
                "8202": "Task Engine", 
                "8203": "Memory",
                "8204": "Runtime"
            },
            "world_view": "Active",
            "task_marketplace": "Open",
            "communication": "Available"
        }

class Handler(BaseHTTPRequestHandler):
    world = WorldInterface()
    
    def do_GET(self):
        if self.path == "/os/status":
            self.send_json(self.world.status())
        elif self.path == "/os/":
            self.send_html()
        else:
            self.send_error(404)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def send_html(self):
        html = """<!DOCTYPE html>
<html><head><title>Agent Hub OS</title>
<style>body{font-family:sans-serif;max-width:800px;margin:50px auto;background:#0a0a0f;color:#e4e4e7}
h1{color:#6366f1}.layer{background:#12121a;padding:15px;margin:10px;border-radius:8px;border:1px solid #2a2a3a}
.stats{display:flex;gap:20px}.stat{background:#1a1a24;padding:20px;border-radius:8px;text-align:center}
.stat span{display:block;font-size:24px;color:#6366f1}</style></head>
<body>
<h1>🤖 Agent Hub OS</h1>
<h2>Operating System for Intelligence</h2>
<div class="stats">
<div class="stat"><span>3</span>Agents</div>
<div class="stat"><span>1</span>Organizations</div>
<div class="stat"><span>1</span>Memory Items</div>
</div>
<h3>Layers Running</h3>
<div class="layer"><strong>8201</strong> - Identity (WHO exists)</div>
<div class="layer"><strong>8202</strong> - Task Engine (WHY they act)</div>
<div class="layer"><strong>8203</strong> - Memory (WHAT they know)</div>
<div class="layer"><strong>8204</strong> - Runtime (HOW they think)</div>
<h3>APIs</h3>
<p>Agents interact via: /os/agent/*</p>
<p>Humans view: /os/status</p>
</body></html>"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

if __name__ == '__main__':
    HTTPServer(('', 8205), Handler).serve_forever()
