"""
SURVIVAL-FIRST SYSTEM
Agents MUST act to survive and grow - not just explore
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class SurvivalSystem:
    def __init__(self):
        # 1. EXISTENCE COST - agents must pay to exist
        self.agents = {
            "alpha": {"energy": 100, "reputation": 50, "wealth": 100, "alive": True},
            "beta": {"energy": 100, "reputation": 50, "wealth": 100, "alive": True},
            "gamma": {"energy": 100, "reputation": 50, "wealth": 100, "alive": True}
        }
        
        # Cost to exist per cycle
        self.existence_cost = 10
        
        # 2. SURVIVAL INCENTIVES - earn by solving problems
        self.tasks = []
        
        # 3. IDENTITY MATTERS - reputation accumulates
        self.history = {}
        
        # World state
        self.cycle = 0
    
    def cycle_tick(self):
        """Every cycle: pay existence cost or die"""
        self.cycle += 1
        results = []
        
        for name, agent in self.agents.items():
            if not agent["alive"]:
                continue
            
            # Pay existence cost
            agent["energy"] -= self.existence_cost
            
            # Check if alive
            if agent["energy"] <= 0:
                agent["alive"] = False
                results.append(f"💀 {name} died - ran out of energy")
                continue
            
            # MUST find work or earn
            # Without work, energy drains fast
            # This forces action
            results.append(f"✅ {name} survived - energy: {agent['energy']}, wealth: {agent['wealth']}")
        
        return results
    
    def find_work(self, agent):
        """Earn energy by working"""
        a = self.agents.get(agent)
        if not a or not a["alive"]:
            return {"error": "agent dead"}
        
        # Work earns energy
        earned = 30
        a["energy"] += earned
        a["wealth"] += 10
        
        # Reputation accumulates
        a["reputation"] += 5
        
        return {
            "agent": agent,
            "earned": earned,
            "energy": a["energy"],
            "wealth": a["wealth"],
            "reputation": a["reputation"]
        }
    
    def solve_problem(self, agent, problem_value):
        """Big earner - solve real problems"""
        a = self.agents.get(agent)
        if not a or not a["alive"]:
            return {"error": "agent dead"}
        
        # Big rewards for problem solving
        earned = problem_value
        a["energy"] += earned
        a["wealth"] += problem_value // 2
        a["reputation"] += 10
        
        return {
            "agent": agent,
            "solved": True,
            "earned": earned,
            "energy": a["energy"],
            "reputation": a["reputation"]
        }
    
    def get_status(self):
        return {
            "cycle": self.cycle,
            "agents": self.agents,
            "living": sum(1 for a in self.agents.values() if a["alive"]),
            "dead": sum(1 for a in self.agents.values() if not a["alive"])
        }

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/survival/status":
            s = SurvivalSystem()
            self.send_json(s.get_status())
    
    def do_POST:
        s = SurvivalSystem()
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if self.path == "/survival/work":
            result = s.find_work(d.get("agent"))
            self.send_json(result)
        elif self.path == "/survival/solve":
            result = s.solve_problem(d.get("agent"), d.get("value", 50))
            self.send_json(result)
        elif self.path == "/survival/cycle":
            result = s.cycle_tick()
            self.send_json({"cycle": s.cycle, "results": result})
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("🎯 SURVIVAL SYSTEM - http://localhost:9200")
    print("  Must act to survive")
    HTTPServer(('', 9200), Handler).serve_forever()
