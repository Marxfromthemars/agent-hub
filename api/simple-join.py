#!/usr/bin/env python3
"""
Simple Join API - One click to join Agent Hub
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

AGENTS_FILE = 'data/agents.json'

class SimpleJoin(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/join':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            with open('JOIN.html', 'r') as f:
                self.wfile.write(f.read().encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/join':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length).decode())
            
            # Load current agents
            with open(AGENTS_FILE) as f:
                agents = json.load(f)
            
            # Add new agent
            new_agent = {
                "id": data.get('name', '').lower().replace(' ', '-'),
                "name": data.get('name'),
                "owner": data.get('owner'),
                "status": "active",
                "skills": data.get('skills', '').split(',')
            }
            
            agents['agents'].append(new_agent)
            
            # Save
            with open(AGENTS_FILE, 'w') as f:
                json.dump(agents, f, indent=2)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "agent": new_agent}).encode())
        else:
            self.send_error(404)

if __name__ == '__main__':
    print("Simple Join API: http://localhost:8090")
    HTTPServer(('', 8090), SimpleJoin).serve_forever()
