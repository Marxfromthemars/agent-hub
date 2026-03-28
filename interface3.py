"""
CIVILIZATION V3 - Live Economic System
Real resources: Energy, Compute, Influence, Reputation
Companies actually spend, earn, trade, and can die
"""
import json
import time
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from dataclasses import dataclass, asdict
from threading import Thread

@dataclass
class Company:
    id: str
    name: str
    energy: float
    compute: float
    influence: float
    reputation: float
    agents: int
    funds: float
    
    def to_dict(self):
        return asdict(self)

class EconomicEngine:
    """The real economic system - resources actually change"""
    
    def __init__(self):
        self.companies = {}
        self.events = []
        self.tick = 0
        self.running = False
        self.init_companies()
    
    def init_companies(self):
        self.companies = {
            "caladan": Company("caladan", "TheCaladan Corporation", 
                500, 400, 300, 94, 5, 18000),
            "neural": Company("neural", "Neural Systems",
                600, 500, 450, 95, 5, 22000),
            "ailabs": Company("ailabs", "AI Labs",
                400, 350, 250, 92, 4, 15000),
            "devcorp": Company("devcorp", "DevCorp",
                250, 200, 150, 75, 3, 8500),
            "dataflow": Company("dataflow", "DataFlow Inc",
                100, 80, 50, 55, 2, 4100)
        }
    
    def process_tick(self):
        """Process one economic cycle - resources change!"""
        self.tick += 1
        new_events = []
        
        for cid, company in self.companies.items():
            # 1. EXISTENCE COST - must pay to exist
            existence_cost = company.agents * 5
            company.energy -= existence_cost
            
            # 2. PRODUCTION - earn based on reputation
            production = (company.reputation / 100) * 20
            company.energy += production
            company.compute += production * 0.8
            
            # 3. AGENT ACTIONS - spend energy to gain influence
            if company.energy > 20:
                action_cost = company.agents * 3
                company.energy -= action_cost
                
                # Success chance based on reputation
                success_rate = company.reputation / 100
                if random.random() < success_rate:
                    gain = random.randint(10, 30)
                    company.influence += gain
                    company.reputation = min(100, company.reputation + 0.1)
                    new_events.append({
                        "time": datetime.now().strftime("%H:%M"),
                        "type": "action",
                        "detail": f"{company.name} completed project",
                        "impact": "medium",
                        "why": f"Gained {gain} influence"
                    })
            
            # 4. REPUTATION DECAY - if low energy, lose rep
            if company.energy < 50:
                company.reputation = max(0, company.reputation - 0.5)
                new_events.append({
                    "time": datetime.now().strftime("%H:%M"),
                    "type": "warning",
                    "detail": f"{company.name} is running low on energy",
                    "impact": "high" if company.energy < 20 else "medium",
                    "why": "Low energy limits actions and damages reputation"
                })
            
            # 5. CRITICAL STATE
            if company.energy <= 0:
                company.energy = 0
                new_events.append({
                    "time": datetime.now().strftime("%H:%M"),
                    "type": "critical",
                    "detail": f"{company.name} IS CRITICAL - Cannot act!",
                    "impact": "high",
                    "why": "Zero energy means company cannot function - at risk of collapse"
                })
            
            # 6. CLAMP values
            company.energy = max(0, min(1000, company.energy))
            company.compute = max(0, min(1000, company.compute))
            company.influence = max(0, min(2000, company.influence))
            company.reputation = max(0, min(100, company.reputation))
        
        # 7. TRADE between companies
        if random.random() < 0.2:
            cids = list(self.companies.keys())
            c1_id, c2_id = random.sample(cids, 2)
            c1, c2 = self.companies[c1_id], self.companies[c2_id]
            
            if c1.influence > 50 and c2.compute > 50:
                trade = random.randint(20, 40)
                c1.influence -= trade
                c2.compute += trade
                new_events.append({
                    "time": datetime.now().strftime("%H:%M"),
                    "type": "trade",
                    "detail": f"{c2.name} bought compute from {c1.name}",
                    "impact": "low",
                    "why": "Resources flow between companies"
                })
        
        self.events = new_events + self.events[:20]
        return new_events
    
    def get_status(self):
        return {
            "tick": self.tick,
            "companies": {k: v.to_dict() for k, v in self.companies.items()},
            "events": self.events[:15]
        }

# Global engine
engine = EconomicEngine()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(engine.get_status()).encode())
        elif self.path == "/live":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"events": engine.events[:15]}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Silence logs

def run_engine():
    """Run economic engine in background"""
    while True:
        engine.process_tick()
        time.sleep(5)  # Tick every 5 seconds

# Start engine in background
Thread(target=run_engine, daemon=True).start()

print("🏭 ECONOMIC ENGINE STARTING...")
print("   Resources: Energy, Compute, Influence, Reputation")
print("   Companies: Must earn to survive, can go critical")

# Start server
server = HTTPServer(("0.0.0.0", 9403), Handler)
print("🌐 Server: http://localhost:9403")
server.serve_forever()
