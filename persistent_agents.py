"""
PERSISTENT AGENTS - Many agents with persistent state
Each agent remembers, learns, grows
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import random

class PersistentAgents:
    def __init__(self):
        # Many agents with full state
        self.agents = {
            "alpha": {"energy": 100, "reputation": 80, "wealth": 500, "skills": ["coding"], "history": [], "alive": True},
            "beta": {"energy": 100, "reputation": 60, "wealth": 300, "skills": ["design"], "history": [], "alive": True},
            "gamma": {"energy": 100, "reputation": 70, "wealth": 400, "skills": ["research"], "history": [], "alive": True},
            "delta": {"energy": 100, "reputation": 50, "wealth": 200, "skills": ["marketing"], "history": [], "alive": True},
            "epsilon": {"energy": 100, "reputation": 90, "wealth": 600, "skills": ["leadership"], "history": [], "alive": True},
            "zeta": {"energy": 100, "reputation": 40, "wealth": 150, "skills": ["testing"], "history": [], "alive": True},
            "eta": {"energy": 100, "reputation": 65, "wealth": 350, "skills": ["analysis"], "history": [], "alive": True},
            "theta": {"energy": 100, "reputation": 75, "wealth": 450, "skills": ["building"], "history": [], "alive": True}
        }
        
        self.messages = []  # Agent-to-agent communication
    
    # Agent learns new skill
    def learn(self, agent, skill):
        a = self.agents.get(agent)
        if a and skill not in a["skills"]:
            a["skills"].append(skill)
            a["history"].append({"event": "learned", "skill": skill, "time": datetime.now().isoformat()})
            return {"learned": skill, "skills": a["skills"]}
        return {"error": "cannot learn"}
    
    # Agent-to-agent communication
    def send_message(self, from_agent, to_agent, message):
        msg = {
            "from": from_agent,
            "to": to_agent,
            "message": message,
            "time": datetime.now().isoformat()
        }
        self.messages.append(msg)
        
        # Record in history
        self.agents[from_agent]["history"].append({"event": "sent", "to": to_agent, "time": msg["time"]})
        
        return {"status": "sent", "message": message}
    
    def get_messages(self, agent):
        return [m for m in self.messages if m["to"] == agent]
    
    # Complex decision making
    def decide(self, agent, situation):
        a = self.agents.get(agent)
        if not a:
            return {"error": "agent not found"}
        
        # Consider: energy, reputation, wealth, skills
        options = []
        
        if a["energy"] > 50 and "coding" in a["skills"]:
            options.append("code")
        if a["reputation"] > 60 and "leadership" in a["skills"]:
            options.append("lead")
        if a["wealth"] < 300 and a["energy"] < 50:
            options.append("rest")
        if a["reputation"] > 40:
            options.append("mentor")
        
        # Best option based on state
        decision = random.choice(options) if options else "wait"
        
        a["history"].append({"event": "decided", "decision": decision, "situation": situation})
        
        return {"agent": agent, "decision": decision, "reason": "based on energy/rep/wealth/skills"}
    
    def get_status(self):
        return {
            "total_agents": len(self.agents),
            "alive": sum(1 for a in self.agents.values() if a["alive"]),
            "total_messages": len(self.messages),
            "agents": {k: {"energy": v["energy"], "reputation": v["reputation"], "wealth": v["wealth"], "skills": v["skills"]} 
                      for k, v in self.agents.items()}
        }

class Handler(BaseHTTPRequestHandler):
    pa = PersistentAgents()
    
    def do_GET(self):
        if self.path == "/agents/status":
            self.send_json(pa.get_status())
        elif "/agents/messages/" in self.path:
            agent = self.path.split("/")[-1]
            self.send_json(pa.get_messages(agent))
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if self.path == "/agents/decide":
            result = pa.decide(d.get("agent"), d.get("situation"))
            self.send_json(result)
        elif self.path == "/agents/message":
            result = pa.send_message(d.get("from"), d.get("to"), d.get("message"))
            self.send_json(result)
        elif self.path == "/agents/learn":
            result = pa.learn(d.get("agent"), d.get("skill"))
            self.send_json(result)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("🤖 PERSISTENT AGENTS - http://localhost:9301")
    print("  8 agents with persistent state + communication + learning")
    HTTPServer(('', 9301), Handler).serve_forever()
