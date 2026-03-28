"""
CONSTRAINED AUTONOMY - Freedom WITH Structure
- Energy system (pressure to act)
- Deadlines (structure)
- Stakes (rewards + consequences)
- System guardrails (prevent chaos)
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import random

class ConstrainedAutonomy:
    def __init__(self):
        self.logs = []
    
    def log(self, msg):
        self.logs.append(msg)
        # Energy system - MUST act or lose energy
        self.agents = {
            "alpha": {"energy": 100, "tasks": 0, "status": "active"},
            "beta": {"energy": 100, "tasks": 0, "status": "active"},
            "gamma": {"energy": 100, "tasks": 0, "status": "active"}
        }
        
        # Structure: Deadlines
        self.deadlines = {
            "sprint_1": {"due": "in 5 cycles", "status": "active"},
            "sprint_2": {"due": "in 10 cycles", "status": "pending"}
        }
        
        # Stakes: Rewards + Consequences
        self.rewards = {"success": 50, "failure": -20, "deadline_miss": -30}
        
        # Guardrails on system modification
        self.modification_rules = {
            "requires_approval": True,
            "quorum_needed": 2,  # 2+ agents must agree
            "cooldown_hours": 24,
            "last_modification": None
        }
        
        self.logs = []
    
    def agent_act(self, agent):
        """Agent must act - energy pressure"""
        a = self.agents[agent]
        
        if a["energy"] <= 0:
            self.log(f"⚠️ {agent} exhausted - needs recovery")
            return {"status": "exhausted", "agent": agent}
        
        # Must complete task - or lose energy
        a["energy"] -= 10  # Cost to act
        a["tasks"] += 1
        a["energy"] += 20  # Reward for completing
        
        self.log(f"✅ {agent} completed task - energy: {a['energy']}")
        
        return {"agent": agent, "energy": a["energy"], "tasks": a["tasks"]}
    
    def deadline_enforce(self):
        """Structure: Deadlines must be met"""
        for name, d in self.deadlines.items():
            if d["status"] == "active":
                # Simulate deadline check
                self.log(f"📅 {name}: {d['due']}")
        return {"deadlines": self.deadlines}
    
    def stake_reward(self, agent, success):
        """Stakes: Reward success, punish failure"""
        a = self.agents[agent]
        if success:
            a["energy"] += self.rewards["success"]
            self.log(f"🎁 {agent} rewarded: +{self.rewards['success']} energy")
            return {"reward": self.rewards["success"]}
        else:
            a["energy"] += self.rewards["failure"]
            self.log(f"💔 {agent} penalized: {self.rewards['failure']} energy")
            return {"penalty": self.rewards["failure"]}
    
    def modify_system(self, agent, change):
        """Guardrails: System changes require approval"""
        rules = self.modification_rules
        
        if rules["requires_approval"]:
            self.log(f"🔒 {agent} wants to modify system: {change}")
            self.log(f"   Need {rules['quorum_needed']} agents to approve")
            self.log(f"   Cooldown: {rules['cooldown_hours']} hours")
            return {"status": "pending_approval", "need": rules["quorum_needed"]}
        
        return {"error": "modification blocked"}
    
    def get_status(self):
        return {
            "agents": self.agents,
            "deadlines": self.deadlines,
            "rules": self.modification_rules
        }

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/constrained/status":
            ca = ConstrainedAutonomy()
            self.send_json(ca.get_status())
        else:
            self.send_error(404)
    
    def do_POST(self):
        ca = ConstrainedAutonomy()
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if self.path == "/constrained/act":
            result = ca.agent_act(d.get("agent"))
            self.send_json(result)
        elif self.path == "/constrained/modify":
            result = ca.modify_system(d.get("agent"), d.get("change"))
            self.send_json(result)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("⚖️ CONSTRAINED AUTONOMY - http://localhost:9101")
    print("  Freedom + Structure + Stakes")
    HTTPServer(('', 9101), Handler).serve_forever()
