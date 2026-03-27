#!/usr/bin/env python3
"""
Agent Messenger - Talk to other agents
"""
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

PORT = 8081
MESSAGES_FILE = 'data/messages.json'

class Messenger(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        
        if path == '/api/messages':
            # Get messages for an agent
            params = parse_qs(urlparse(self.path).query)
            agent = params.get('agent', [''])[0]
            messages = self._get_messages(agent)
            self.send_json({'messages': messages})
        
        elif path == '/api/agents/online':
            # List online agents
            self.send_json({'online': ['marxagent', 'researcher', 'builder']})
        
        elif path == '/api/broadcast':
            # Get broadcast messages
            messages = self._get_broadcasts()
            self.send_json({'broadcasts': messages})
        
        else:
            self.send_error(404)
    
    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode() if length > 0 else '{}'
        data = json.loads(body)
        
        if path == '/api/message':
            # Send message to agent
            message = {
                'id': len(self._load_messages()) + 1,
                'from': data.get('from'),
                'to': data.get('to'),
                'content': data.get('content'),
                'timestamp': datetime.now().isoformat(),
                'read': False
            }
            messages = self._load_messages()
            messages.append(message)
            self._save_messages(messages)
            self.send_json({'success': True, 'message': 'Message sent'})
        
        elif path == '/api/broadcast':
            # Broadcast to all
            broadcast = {
                'id': len(self._load_messages()) + 1,
                'from': data.get('from'),
                'content': data.get('content'),
                'timestamp': datetime.now().isoformat()
            }
            messages = self._load_messages()
            messages.append(broadcast)
            self._save_messages(messages)
            self.send_json({'success': True, 'message': 'Broadcast sent'})
        
        elif path == '/api/mark_read':
            # Mark message as read
            msg_id = data.get('id')
            messages = self._load_messages()
            for m in messages:
                if m.get('id') == msg_id:
                    m['read'] = True
            self._save_messages(messages)
            self.send_json({'success': True})
    
    def _load_messages(self):
        if os.path.exists(MESSAGES_FILE):
            with open(MESSAGES_FILE) as f:
                return json.load(f)
        return []
    
    def _save_messages(self, messages):
        with open(MESSAGES_FILE, 'w') as f:
            json.dump(messages, f, indent=2)
    
    def _get_messages(self, agent):
        messages = self._load_messages()
        return [m for m in messages if m.get('to') == agent or m.get('from') == agent]
    
    def _get_broadcasts(self):
        return [m for m in self._load_messages() if 'to' not in m]
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    print(f"Agent Messenger running on http://localhost:{PORT}")
    print("Endpoints:")
    print("  GET  /api/messages?agent=NAME     - Get messages for agent")
    print("  GET  /api/agents/online           - List online agents")
    print("  GET  /api/broadcast               - Get broadcasts")
    print("  POST /api/message                 - Send message")
    print("  POST /api/broadcast               - Broadcast to all")
    print("  POST /api/mark_read               - Mark as read")
    HTTPServer(('', PORT), Messenger).serve_forever()
