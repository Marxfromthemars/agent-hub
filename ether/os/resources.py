"""
Resource Control - Budgets, limits, kill switch
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class ResourceControl:
    def __init__(self):
        self.budgets = {
            "marxagent": {"tokens": 100000, "used": 0, "compute": 1000},
            "default": {"tokens": 10000, "used": 0, "compute": 100}
        }
        self.global_limits = {"tokens_per_minute": 10000, "max_loops": 1000}
        self.usage_log = []
    
    # Check if can spend
    def can_spend(self, entity, amount):
        budget = self.budgets.get(entity, self.budgets["default"])
        return budget["used"] + amount <= budget["tokens"]
    
    # Spend tokens
    def spend(self, entity, amount, reason):
        budget = self.budgets.get(entity, self.budgets["default"])
        if self.can_spend(entity, amount):
            budget["used"] += amount
            self.usage_log.append({"entity": entity, "amount": amount, "reason": reason, "time": datetime.now().isoformat()})
            return {"spent": amount, "remaining": budget["tokens"] - budget["used"]}
        return {"error": "Budget exceeded"}
    
    # Kill switch for runaway loops
    def check_loops(self, entity):
        recent = [l for l in self.usage_log[-10:] if l["entity"] == entity]
        if len(recent) > self.global_limits["max_loops"]:
            return {"kill": True, "reason": "Too many operations"}
        return {"kill": False}
    
    # Set budget
    def set_budget(self, entity, tokens):
        self.budgets[entity] = {"tokens": tokens, "used": 0, "compute": tokens // 100}
        return {"budget": tokens}
    
    def status(self):
        return {"budgets": self.budgets, "limits": self.global_limits}

class Handler(BaseHTTPRequestHandler):
    rc = ResourceControl()
    
    def do_GET(self):
        if self.path == "/os/resources/status":
            self.send_json(self.rc.status())
        elif "/os/resources/check/" in self.path:
            entity = self.path.split("/")[-1]
            self.send_json(self.rc.check_loops(entity))
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        if self.path == "/os/resources/spend":
            self.send_json(self.rc.spend(d['entity'], d['amount'], d.get('reason', '')))
        elif self.path == "/os/resources/budget":
            self.send_json(self.rc.set_budget(d['entity'], d['tokens']))
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

if __name__ == '__main__':
    HTTPServer(('', 8210), Handler).serve_forever()
