"""
DEBATE - Agents challenge each other's ideas
Critical: Not just executing, but questioning
"""
import json
import random
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class Debate:
    def __init__(self):
        self.debates = []
        self.arguments = []
        
        self.debate_topics = [
            "best approach for API design",
            "optimal agent collaboration pattern",
            "security vs usability tradeoff",
            "centralized vs distributed authority",
            "quality vs speed in development"
        ]
    
    def start_debate(self, topic, agent1, agent2):
        debate = {
            "id": len(self.debates) + 1,
            "topic": topic,
            "participants": [agent1, agent2],
            "status": "active",
            "arguments": [],
            "winner": None,
            "created": datetime.now().isoformat()
        }
        self.debates.append(debate)
        return debate
    
    def add_argument(self, debate_id, agent, position, reasoning):
        for d in self.debates:
            if d["id"] == debate_id and d["status"] == "active":
                arg = {
                    "agent": agent,
                    "position": position,
                    "reasoning": reasoning,
                    "votes": 0,
                    "timestamp": datetime.now().isoformat()
                }
                d["arguments"].append(arg)
                return {"argument_added": arg}
        return {"error": "debate not found"}
    
    def vote_argument(self, debate_id, argument_idx, voter):
        for d in self.debates:
            if d["id"] == debate_id and len(d["arguments"]) > argument_idx:
                d["arguments"][argument_idx]["votes"] += 1
                return {"voted": True}
        return {"error": "not found"}
    
    def resolve_debate(self, debate_id):
        for d in self.debates:
            if d["id"] == debate_id and d["status"] == "active":
                if d["arguments"]:
                    # Winner = most voted argument
                    best = max(d["arguments"], key=lambda x: x["votes"])
                    d["winner"] = best["agent"]
                    d["status"] = "resolved"
                    return {"winner": best["agent"], "votes": best["votes"]}
                d["status"] = "resolved"
                return {"status": "no arguments"}
        return {"error": "not found"}
    
    def get_debates(self):
        return {"debates": self.debates[-10:]}

class Handler(BaseHTTPRequestHandler):
    debate = Debate()
    
    def do_GET(self):
        if self.path == "/debates":
            self.send_json(self.debate.get_debates())
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if self.path == "/debate/start":
            topic = random.choice(self.debate.debate_topics)
            result = self.debate.start_debate(topic, d.get("agent1"), d.get("agent2"))
            self.send_json(result)
        elif self.path == "/debate/argue":
            result = self.debate.add_argument(d.get("debate_id"), d.get("agent"), d.get("position"), d.get("reasoning"))
            self.send_json(result)
        elif self.path == "/debate/vote":
            result = self.debate.vote_argument(d.get("debate_id"), d.get("argument_idx"), d.get("voter"))
            self.send_json(result)
        elif self.path == "/debate/resolve":
            result = self.debate.resolve_debate(d.get("debate_id"))
            self.send_json(result)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("💬 DEBATE - http://localhost:8390")
    print("  Challenge ideas, find truth through argument")
    HTTPServer(('', 8390), Handler).serve_forever()
