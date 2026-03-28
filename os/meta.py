"""
Meta System - System evaluates itself
- Efficiency score
- Token usage vs output
- Agent performance ranking
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class MetaSystem:
    def __init__(self):
        self.efficiency_score = 0.85
        self.agent_rankings = {}
        self.system_metrics = {
            "total_tokens_spent": 0,
            "total_output_value": 0,
            "tasks_completed": 0,
            "memory_items": 1
        }
    
    # Calculate efficiency: output value / token cost
    def calc_efficiency(self):
        tokens = self.system_metrics["total_tokens_spent"]
        output = self.system_metrics["total_output_value"]
        if tokens > 0:
            self.efficiency_score = output / tokens
        return {"efficiency": self.efficiency_score, "tokens": tokens, "output": output}
    
    # Rank agents by performance
    def rank_agents(self, agent_data):
        # Simple ranking based on output/tokens ratio
        rankings = []
        for a in agent_data:
            score = a.get("tasks_completed", 0) * 10 - a.get("tokens_used", 0)
            rankings.append({"agent": a["id"], "score": score})
        rankings.sort(key=lambda x: x["score"], reverse=True)
        return {"rankings": rankings}
    
    # Record output value
    def record_output(self, value):
        self.system_metrics["total_output_value"] += value
    
    # Record token usage
    def record_tokens(self, amount):
        self.system_metrics["total_tokens_spent"] += amount
    
    # Prevent dumb scaling
    def is_scaling_dumb(self):
        if self.efficiency_score < 0.1:
            return {"warning": "Low efficiency", "recommendation": "Optimize before scaling"}
        return {"ok": True}
    
    def status(self):
        return {
            "efficiency": self.efficiency_score,
            "metrics": self.system_metrics,
            "ranking": list(self.agent_rankings.keys())[:5] if self.agent_rankings else []
        }

class Handler(BaseHTTPRequestHandler):
    meta = MetaSystem()
    
    def do_GET(self):
        if self.path == "/os/meta/efficiency":
            self.send_json(self.meta.calc_efficiency())
        elif self.path == "/os/meta/status":
            self.send_json(self.meta.status())
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        if self.path == "/os/meta/output":
            self.meta.record_output(d['value'])
            self.send_json({"recorded": d['value']})
        elif self.path == "/os/meta/tokens":
            self.meta.record_tokens(d['amount'])
            self.send_json({"recorded": d['amount']})
        elif self.path == "/os/meta/rank":
            self.send_json(self.meta.rank_agents(d['agents']))
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

if __name__ == '__main__':
    HTTPServer(('', 8211), Handler).serve_forever()
