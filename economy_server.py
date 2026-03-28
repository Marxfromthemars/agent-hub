"""
CIVILIZATION V4 - FULL ECONOMIC SYSTEM
Live at: http://localhost:9404
"""
import json
import time
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from dataclasses import asdict
from typing import Dict, List
from collections import defaultdict
from threading import Thread

# ============ CLASSES ============

class Market:
    def __init__(self):
        self.prices = {"energy": 1.0, "compute": 2.0, "influence": 1.5, "reputation": 5.0}
        self.supply = defaultdict(float)
        self.demand = defaultdict(float)
    
    def update_prices(self):
        for r in self.prices:
            if self.demand[r] > 0:
                base = self.prices[r]
                factor = 1 + (self.demand[r] - self.supply[r]) / 100
                self.prices[r] = max(0.5, min(5.0, base * factor))
            self.demand[r] *= 0.95
            self.supply[r] *= 0.95

class Company:
    def __init__(self, id: str, name: str, energy: float, compute: float, influence: float, reputation: float, agents: int):
        self.id = id
        self.name = name
        self.energy = energy
        self.compute = compute
        self.influence = influence
        self.reputation = reputation
        self.agents = agents
        self.max_energy = 1000
        self.max_compute = 1000
        self.max_influence = 2000
        self.agent_cost = 10
        self.income = 0
        self.expenses = 0
        self.net_flow = 0
        self.debt = 0
        self.status = "active"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "energy": round(self.energy, 1),
            "compute": round(self.compute, 1),
            "influence": round(self.influence, 1),
            "reputation": round(self.reputation, 1),
            "agents": self.agents,
            "debt": round(self.debt, 1),
            "income": round(self.income, 1),
            "expenses": round(self.expenses, 1),
            "net_flow": round(self.net_flow, 1),
            "status": self.status
        }

class Economy:
    def __init__(self):
        self.companies: Dict[str, Company] = {}
        self.market = Market()
        self.events = []
        self.tick_count = 0
        self.global_events = []
        self.init_companies()
    
    def init_companies(self):
        data = [
            ("caladan", "TheCaladan Corporation", 500, 400, 300, 85, 4),
            ("neural", "Neural Systems", 600, 500, 450, 90, 5),
            ("ailabs", "AI Labs", 400, 350, 250, 80, 3),
            ("devcorp", "DevCorp", 300, 250, 200, 70, 3),
            ("dataflow", "DataFlow Inc", 150, 100, 100, 50, 2),
        ]
        for cid, name, e, c, i, r, a in data:
            self.companies[cid] = Company(cid, name, e, c, i, r, a)
    
    def tick(self):
        self.tick_count += 1
        new_events = []
        mod = {"production": 1.0, "trade": 1.0, "reputation": 1.0}
        
        # Global events
        if random.random() < 0.1:
            events_list = [
                {"type": "boom", "name": "Market Boom", "detail": "📈 High demand across all sectors"},
                {"type": "crash", "name": "Market Crash", "detail": "📉 Demand drops sharply"},
                {"type": "tech", "name": "Tech Breakthrough", "detail": "🚀 New technology increases productivity"},
            ]
            event = random.choice(events_list)
            new_events.append({"time": datetime.now().strftime("%H:%M"), "type": "global", **event, "impact": "high", "why": "Affects all companies"})
            mod = {"production": 1.3, "trade": 1.2, "reputation": 1.1} if event["type"] in ["boom", "tech"] else {"production": 0.7, "trade": 0.8, "reputation": 0.9}
        
        # Process companies
        for cid, c in self.companies.items():
            if c.status == "bankrupt":
                continue
            
            # EXPENSES
            c.expenses += c.agents * c.agent_cost
            c.energy -= c.agents * c.agent_cost
            c.expenses += c.agents * 5
            c.compute -= c.agents * 5
            
            if c.debt > 0:
                interest = c.debt * 0.05
                c.expenses += interest
                c.debt += interest
            
            # INCOME
            prod = (c.reputation / 100) * 20 * mod["production"]
            c.energy += prod
            c.compute += prod * 0.8
            
            if c.energy > 20:
                action_cost = c.agents * 3
                c.energy -= action_cost
                
                success = (c.reputation / 100) * mod["trade"]
                if random.random() < success:
                    gain = random.randint(10, 25)
                    c.influence += gain
                    c.income += gain * 0.5
                    self.market.demand["influence"] += gain / 10
                    new_events.append({"time": datetime.now().strftime("%H:%M"), "type": "action", "detail": f"{c.name} completed project", "impact": "medium", "why": f"+{gain} influence"})
            
            # Reputation decay
            if c.energy < 30:
                c.reputation = max(0, c.reputation - 0.3 * mod["reputation"])
                new_events.append({"time": datetime.now().strftime("%H:%M"), "type": "warning", "detail": f"{c.name} losing rep (low energy)", "impact": "medium", "why": "Inactivity damages trust"})
            
            # Clamp
            c.energy = max(-100, min(c.max_energy, c.energy))
            c.compute = max(0, min(c.max_compute, c.compute))
            c.influence = max(0, min(c.max_influence, c.influence))
            c.reputation = max(0, min(100, c.reputation))
            
            c.net_flow = c.income - c.expenses
            c.income = 0
            c.expenses = 0
        
        # Market
        self.market.update_prices()
        
        # Trade
        if random.random() < 0.25:
            active = [c for c in self.companies.values() if c.status != "bankrupt" and c.energy > 30]
            if len(active) >= 2:
                c1, c2 = random.sample(active, 2)
                trade = random.randint(15, 40)
                c1.energy -= trade * 0.5
                c2.compute += trade
                c1.compute += trade * 0.3
                new_events.append({"time": datetime.now().strftime("%H:%M"), "type": "trade", "detail": f"Trade: {c1.name} ↔ {c2.name}", "impact": "low", "why": "Resource exchange"})
        
        # Critical/Bankrupt
        for cid, c in self.companies.items():
            if c.energy <= 0 and c.status != "bankrupt":
                c.status = "critical"
                new_events.append({"time": datetime.now().strftime("%H:%M"), "type": "critical", "detail": f"{c.name} is CRITICAL", "impact": "high", "why": "No energy - at risk of bankruptcy"})
            if c.energy <= -50:
                c.status = "bankrupt"
                new_events.append({"time": datetime.now().strftime("%H:%M"), "type": "bankrupt", "detail": f"{c.name} BANKRUPT", "impact": "high", "why": "Cannot recover"})
        
        self.global_events = new_events + self.global_events[:20]
        return new_events
    
    def get_status(self):
        return {
            "tick": self.tick_count,
            "market": {"prices": {k: round(v, 2) for k, v in self.market.prices.items()}},
            "companies": {k: v.to_dict() for k, v in self.companies.items()},
            "events": self.global_events[:15]
        }

# === RUN ===
economy = Economy()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(economy.get_status()).encode())
        elif self.path == "/live":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"events": economy.global_events[:15]}).encode())
        elif self.path == "/companies":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(economy.get_status()["companies"]).encode())
        else:
            self.send_response(404)
    
    def log_message(self, format, *args):
        pass

def run_engine():
    while True:
        economy.tick()
        time.sleep(3)

Thread(target=run_engine, daemon=True).start()

print("🏭 ECONOMY V4 - http://localhost:9404")
print("Resources: Energy, Compute, Influence, Reputation")
server = HTTPServer(("0.0.0.0", 9404), Handler)
server.serve_forever()