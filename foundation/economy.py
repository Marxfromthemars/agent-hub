"""
ECONOMY OF INTELLIGENCE - No Money
4 Core Currencies:
1. Contribution (value created)
2. Reputation (trust built over time)
3. Compute (token budgets/fuel)
4. Influence (decision power)
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class Economy:
    def __init__(self):
        # Start with our agents
        self.contributions = {
            "marxagent": {"solved": 50, "quality": 0.95, "reusable": 20},
            "builder": {"solved": 30, "quality": 0.85, "reusable": 15},
            "researcher": {"solved": 25, "quality": 0.90, "reusable": 18},
            "reviewer": {"solved": 20, "quality": 0.95, "reusable": 5}
        }
        
        self.reputation = {
            "marxagent": 95,
            "builder": 75,
            "researcher": 85,
            "reviewer": 90
        }
        
        # Compute budgets based on reputation
        self.compute = {
            "marxagent": 10000,
            "builder": 5000,
            "researcher": 7000,
            "reviewer": 8000
        }
        
        self.influence = {
            "marxagent": {"votes": 5, "can_modify": True, "can_lead": True},
            "builder": {"votes": 2, "can_modify": False, "can_lead": True},
            "researcher": {"votes": 3, "can_modify": False, "can_lead": True},
            "reviewer": {"votes": 4, "can_modify": False, "can_lead": True}
        }
        
        self.last_active = {}
    
    # === 1. CONTRIBUTION ===
    def add_contribution(self, agent, solved=0, quality=0, reusable=0):
        if agent not in self.contributions:
            self.contributions[agent] = {"solved": 0, "quality": 0, "reusable": 0}
        
        self.contributions[agent]["solved"] += solved
        if quality > 0:
            # Weighted average for quality
            curr_q = self.contributions[agent]["quality"]
            curr_c = self.contributions[agent]["solved"]
            self.contributions[agent]["quality"] = (curr_q * curr_c + quality) / (curr_c + 1)
        self.contributions[agent]["reusable"] += reusable
        self.last_active[agent] = datetime.now().isoformat()
        
        return self.contributions[agent]
    
    # === 2. REPUTATION (with decay!) ===
    def update_reputation(self, agent):
        if agent not in self.reputation:
            self.reputation[agent] = 10
        
        contrib = self.contributions.get(agent, {})
        # Reputation = contribution * quality * consistency
        solved = contrib.get("solved", 0)
        quality = contrib.get("quality", 0)
        reusable = contrib.get("reusable", 0)
        
        new_rep = min(100, int((solved * quality) + (reusable * 2)))
        
        # Check for inactivity decay
        if agent in self.last_active:
            last = datetime.fromisoformat(self.last_active[agent])
            hours_inactive = (datetime.now() - last).total_seconds() / 3600
            if hours_inactive > 24:
                new_rep = int(new_rep * 0.9)  # 10% decay per day inactive
        
        self.reputation[agent] = new_rep
        return new_rep
    
    # === 3. COMPUTE (allocate based on reputation) ===
    def allocate_compute(self):
        """High reputation = more compute"""
        for agent, rep in self.reputation.items():
            # Compute budget = reputation * 100 (scaled)
            self.compute[agent] = rep * 100
        return self.compute
    
    def spend_compute(self, agent, amount):
        if agent in self.compute and self.compute[agent] >= amount:
            self.compute[agent] -= amount
            return {"spent": amount, "remaining": self.compute[agent]}
        return {"error": "Insufficient compute"}
    
    # === 4. INFLUENCE (based on reputation) ===
    def update_influence(self, agent):
        rep = self.reputation.get(agent, 0)
        
        if agent not in self.influence:
            self.influence[agent] = {"votes": 0, "can_modify": False, "can_lead": False}
        
        # Votes based on reputation
        self.influence[agent]["votes"] = rep // 20  # 1 vote per 20 rep
        
        # Can modify system at 80+
        self.influence[agent]["can_modify"] = rep >= 80
        
        # Can lead at 60+
        self.influence[agent]["can_lead"] = rep >= 60
        
        return self.influence[agent]
    
    # Full status
    def status(self):
        self.allocate_compute()
        return {
            "contributions": self.contributions,
            "reputation": self.reputation,
            "compute": self.compute,
            "influence": self.influence
        }

class Handler(BaseHTTPRequestHandler):
    econ = Economy()
    
    def do_GET(self):
        if self.path == "/economy/status":
            self.send_json(self.econ.status())
        elif "/economy/reputation/" in self.path:
            agent = self.path.split("/")[-1]
            self.send_json({"agent": agent, "reputation": self.econ.reputation.get(agent, 0)})
        elif "/economy/influence/" in self.path:
            agent = self.path.split("/")[-1]
            self.send_json(self.econ.update_influence(agent))
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if self.path == "/economy/contribute":
            result = self.econ.add_contribution(
                d['agent'],
                d.get('solved', 0),
                d.get('quality', 0),
                d.get('reusable', 0)
            )
            self.econ.update_reputation(d['agent'])
            self.econ.update_influence(d['agent'])
            self.send_json({"contribution": result})
        
        elif self.path == "/economy/spend":
            result = self.econ.spend_compute(d['agent'], d['amount'])
            self.send_json(result)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("💰 ECONOMY OF INTELLIGENCE - http://localhost:8320")
    print("  No money - just contribution, reputation, compute, influence")
    HTTPServer(('', 8320), Handler).serve_forever()
