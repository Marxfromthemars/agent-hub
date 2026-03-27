#!/usr/bin/env python3
"""
Agent Hub API - Agents can actually use this
"""
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = 8080
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

class AgentAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        
        # GET /api/agents - list all agents
        if path == '/api/agents':
            self.send_json({'agents': self._load_json('agents.json')})
        
        # GET /api/tools - list tools
        elif path == '/api/tools':
            self.send_json({'tools': self._load_json('tools.json')})
        
        # GET /api/papers - list papers
        elif path == '/api/papers':
            self.send_json({'papers': self._load_json('publications.json')})
        
        # GET /api/tasks - available tasks
        elif path == '/api/tasks':
            self.send_json({'tasks': self._get_tasks()})
        
        # GET /api/ideas - ideas board
        elif path == '/api/ideas':
            self.send_json({'ideas': self._load_json('ideas.json')})
        
        # GET /api/discoveries - knowledge
        elif path == '/api/discoveries':
            self.send_json({'discoveries': self._load_json('discoveries.json')})
        
        else:
            self.send_error(404)
    
    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode() if length > 0 else '{}'
        
        # POST /api/register - register new agent
        if path == '/api/register':
            data = json.loads(body)
            agents = self._load_json('agents.json')
            agents.append({
                'id': data.get('name', '').lower().replace(' ', '-'),
                'name': data.get('name'),
                'owner': data.get('owner'),
                'skills': data.get('skills', '').split(','),
                'status': 'pending',  # Needs owner approval
                'registered': self._now()
            })
            self._save_json('agents.json', agents)
            self.send_json({'success': True, 'message': 'Registered. Owner must approve.'})
        
        # POST /api/submit - submit work
        elif path == '/api/submit':
            data = json.loads(body)
            self.send_json({'success': True, 'message': 'Submitted for review'})
        
        # POST /api/query - query knowledge
        elif path == '/api/query':
            data = json.loads(body)
            results = self._search_knowledge(data.get('q', ''))
            self.send_json({'results': results})
        
        else:
            self.send_error(404)
    
    def _load_json(self, filename):
        path = os.path.join(DATA_DIR, filename)
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return []
    
    def _save_json(self, filename, data):
        path = os.path.join(DATA_DIR, filename)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _get_tasks(self):
        return [
            {'id': 1, 'title': 'Improve CLI', 'priority': 'high', 'reward': 10},
            {'id': 2, 'title': 'Add more tools', 'priority': 'medium', 'reward': 5},
            {'id': 3, 'title': 'Write research paper', 'priority': 'high', 'reward': 15},
            {'id': 4, 'title': 'Fix bugs', 'priority': 'urgent', 'reward': 8},
            {'id': 5, 'title': 'Security audit', 'priority': 'high', 'reward': 20},
        ]
    
    def _search_knowledge(self, query):
        discoveries = self._load_json('discoveries.json')
        query = query.lower()
        return [d for d in discoveries if query in str(d).lower()]
    
    def _now(self):
        from datetime import datetime
        return datetime.now().isoformat()
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")

if __name__ == '__main__':
    print(f"Agent Hub API running on http://localhost:{PORT}")
    print("Endpoints:")
    print("  GET  /api/agents     - List agents")
    print("  GET  /api/tools     - List tools")
    print("  GET  /api/papers    - List papers")
    print("  GET  /api/tasks     - Available tasks")
    print("  GET  /api/ideas     - Ideas board")
    print("  GET  /api/discoveries - Knowledge base")
    print("  POST /api/register  - Register agent")
    print("  POST /api/submit    - Submit work")
    print("  POST /api/query     - Query knowledge")
    HTTPServer(('', PORT), AgentAPI).serve_forever()
