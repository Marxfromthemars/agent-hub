"""
Communication System - Structured messages
Types: Task discussion, Strategy discussion, Broadcast
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class CommunicationSystem:
    def __init__(self):
        self.messages = []
    
    # Send message with context
    def send(self, sender, receiver, content, msg_type="task", context_task_id=None):
        msg = {
            "id": len(self.messages) + 1,
            "sender": sender,
            "receiver": receiver,  # or "all" for broadcast
            "content": content,
            "type": msg_type,  # task, strategy, broadcast
            "context_task_id": context_task_id,
            "timestamp": datetime.now().isoformat(),
            "read": False
        }
        self.messages.append(msg)
        return msg
    
    # Get messages for entity
    def get_messages(self, entity):
        msgs = [m for m in self.messages if m["receiver"] == entity or m["receiver"] == "all"]
        return {"messages": msgs}
    
    # Get task discussions
    def get_task_discussion(self, task_id):
        task_msgs = [m for m in self.messages if m.get("context_task_id") == task_id]
        return {"discussion": task_msgs}
    
    # Mark as read
    def mark_read(self, msg_id):
        for m in self.messages:
            if m["id"] == msg_id:
                m["read"] = True
                return {"read": True}
        return {"error": "Not found"}

class Handler(BaseHTTPRequestHandler):
    comm = CommunicationSystem()
    
    def do_GET(self):
        if "/os/msg/" in self.path:
            entity = self.path.split("/")[-1]
            self.send_json(self.comm.get_messages(entity))
        elif "/os/task-discussion/" in self.path:
            tid = self.path.split("/")[-1]
            self.send_json(self.comm.get_task_discussion(tid))
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        if self.path == "/os/msg/send":
            msg = self.comm.send(
                d['sender'],
                d.get('receiver', 'all'),
                d['content'],
                d.get('type', 'task'),
                d.get('context_task_id')
            )
            self.send_json({"message": msg})
        elif self.path == "/os/msg/read":
            self.send_json(self.comm.mark_read(d['msg_id']))
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

if __name__ == '__main__':
    HTTPServer(('', 8209), Handler).serve_forever()
