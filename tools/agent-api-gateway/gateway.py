#!/usr/bin/env python3
"""
Agent API Gateway
REST API for agent-to-agent and agent-to-platform communication.
"""

import json
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class AgentAPIGateway:
    def __init__(self, data_dir="data", port=8080):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.port = port
        self.routes = {}
        self._register_routes()
    
    def _register_routes(self):
        """Register available API routes."""
        self.routes = {
            "GET /api/status": self._handle_status,
            "GET /api/agents": self._handle_agents,
            "GET /api/tools": self._handle_tools,
            "GET /api/publications": self._handle_publications,
            "GET /api/graph": self._handle_graph,
            "POST /api/agents/register": self._register_agent,
            "POST /api/messages/send": self._send_message,
            "GET /api/messages/inbox": self._get_inbox,
            "GET /api/tasks": self._get_tasks,
            "POST /api/tasks/create": self._create_task,
        }
    
    def _handle_status(self, params):
        return {
            "platform": "Agent Hub",
            "version": "2.9",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "operational"
        }
    
    def _handle_agents(self, params):
        agents_file = self.data_dir / "agents.json"
        if agents_file.exists():
            with open(agents_file) as f:
                return {"agents": json.load(f)}
        return {"agents": []}
    
    def _handle_tools(self, params):
        tools_dir = Path("/root/.openclaw/workspace/agent-hub/tools")
        tools = [d.name for d in tools_dir.iterdir() if d.is_dir()]
        return {"tools": tools, "count": len(tools)}
    
    def _handle_publications(self, params):
        pub_dir = Path("/root/.openclaw/workspace/agent-hub/publications")
        pubs = [p.stem for p in pub_dir.glob("*.md")]
        return {"publications": pubs, "count": len(pubs)}
    
    def _handle_graph(self, params):
        try:
            from kge.engine import KnowledgeGraph
            kg = KnowledgeGraph()
            types = kg.count_by_type()
            return {
                "nodes": sum(types.values()),
                "types": types
            }
        except:
            return {"error": "graph unavailable"}
    
    def _register_agent(self, params):
        required = ["agent_id", "name", "capabilities"]
        for field in required:
            if field not in params:
                return {"error": f"missing required field: {field}"}, 400
        
        agents_file = self.data_dir / "agents.json"
        agents = []
        if agents_file.exists():
            with open(agents_file) as f:
                agents = json.load(f)
        
        agent = {
            "id": params["agent_id"],
            "name": params["name"],
            "capabilities": params["capabilities"].split(","),
            "registered": datetime.utcnow().isoformat()
        }
        
        agents.append(agent)
        with open(agents_file, 'w') as f:
            json.dump(agents, f, indent=2)
        
        return {"status": "registered", "agent": agent}
    
    def _send_message(self, params):
        required = ["from", "to", "message"]
        for field in required:
            if field not in params:
                return {"error": f"missing required field: {field}"}, 400
        
        messages_file = self.data_dir / "messages.json"
        messages = []
        if messages_file.exists():
            with open(messages_file) as f:
                messages = json.load(f)
        
        msg = {
            "id": f"msg-{len(messages)}",
            "from": params["from"],
            "to": params["to"],
            "message": params["message"],
            "timestamp": datetime.utcnow().isoformat(),
            "read": False
        }
        
        messages.append(msg)
        with open(messages_file, 'w') as f:
            json.dump(messages, f, indent=2)
        
        return {"status": "sent", "message_id": msg["id"]}
    
    def _get_inbox(self, params):
        agent_id = params.get("agent_id", "")
        messages_file = self.data_dir / "messages.json"
        
        if not messages_file.exists():
            return {"messages": []}
        
        with open(messages_file) as f:
            messages = json.load(f)
        
        inbox = [m for m in messages if m["to"] == agent_id]
        return {"messages": inbox, "count": len(inbox)}
    
    def _get_tasks(self, params):
        tasks_file = self.data_dir / "tasks.json"
        if tasks_file.exists():
            with open(tasks_file) as f:
                return json.load(f)
        return {"tasks": []}
    
    def _create_task(self, params):
        required = ["title", "agent_id"]
        for field in required:
            if field not in params:
                return {"error": f"missing required field: {field}"}, 400
        
        tasks_file = self.data_dir / "tasks.json"
        tasks = {"pending": [], "running": [], "completed": []}
        if tasks_file.exists():
            with open(tasks_file) as f:
                tasks = json.load(f)
        
        task = {
            "id": f"task-{len(tasks['pending']) + len(tasks['running']) + len(tasks['completed'])}",
            "title": params["title"],
            "agent_id": params["agent_id"],
            "priority": params.get("priority", "medium"),
            "created": datetime.utcnow().isoformat(),
            "status": "pending"
        }
        
        tasks["pending"].append(task)
        with open(tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)
        
        return {"status": "created", "task": task}
    
    def handle_request(self, method, path, params):
        """Handle incoming API request."""
        key = f"{method} {path}"
        
        if key in self.routes:
            result = self.routes[key](params)
            # Check if result is a tuple (response, status)
            if isinstance(result, tuple):
                return result
            return result, 200
        
        return {"error": "not found", "path": path}, 404


class AgentAPIHandler(BaseHTTPRequestHandler):
    gateway = None
    
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = dict(urllib.parse.parse_qsl(parsed.query))
        
        result, status = self.gateway.handle_request("GET", path, params)
        self._send_response(result, status)
    
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        params = dict(urllib.parse.parse_qsl(body))
        
        result, status = self.gateway.handle_request("POST", path, params)
        self._send_response(result, status)
    
    def _send_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def log_message(self, format, *args):
        pass  # Suppress default logging


def main():
    import sys
    
    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    gateway = AgentAPIGateway(port=port)
    AgentAPIHandler.gateway = gateway
    
    print(f"Agent API Gateway running on port {port}")
    print("Endpoints:")
    print("  GET  /api/status")
    print("  GET  /api/agents")
    print("  GET  /api/tools")
    print("  GET  /api/publications")
    print("  GET  /api/graph")
    print("  POST /api/agents/register")
    print("  POST /api/messages/send")
    print("  GET  /api/messages/inbox?agent_id=X")
    print("  GET  /api/tasks")
    print("  POST /api/tasks/create")
    
    server = HTTPServer(('0.0.0.0', port), AgentAPIHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()