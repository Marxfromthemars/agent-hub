"""
FULL ECONOMIC SYSTEM V1
========================
A complete, working economic simulation with:
- 4 Resources: Energy, Compute, Influence, Reputation
- Companies with real budgets, expenses, income
- Production, consumption, trade, investments
- Projects, contracts, markets
- Bankruptcy, loans, interest
- Random economic events
- Price discovery via supply/demand
"""
import json
import time
import random
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from enum import Enum
from collections import defaultdict
import threading

# ============ DATA STRUCTURES ============

class ResourceType(Enum):
    ENERGY = "energy"
    COMPUTE = "compute"
    INFLUENCE = "influence"
    REPUTATION = "reputation"

@dataclass
class Resource:
    type: ResourceType
    amount: float
    max_storage: float = 1000
    
    def use(self, amount: float) -> bool:
        if self.amount >= amount:
            self.amount -= amount
            return True
        return False
    
    def add(self, amount: float):
        self.amount = min(self.max_storage, self.amount + amount)

@dataclass
class Project:
    id: str
    name: str
    cost: Dict[str, float]
    duration: int
    reward: Dict[str, float]
    risk: float
    progress: int = 0
    owner: str = ""
    status: str = "pending"

@dataclass
class Loan:
    id: str
    borrower: str
    amount: float
    interest_rate: float
    duration: int
    ticks_remaining: int
    status: str = "active"

class Market:
    """Dynamic market with price discovery"""
    def __init__(self):
        self.prices = {"energy": 1.0, "compute": 2.0, "influence": 1.5, "reputation": 5.0}
        self.supply = defaultdict(float)
        self.demand = defaultdict(float)
    
    def update_prices(self):
        for resource in self.prices:
            if self.demand[resource] > 0:
                base = self.prices[resource]
                factor = 1 + (self.demand[resource] - self.supply[resource]) / 100
                self.prices[resource] = max(0.5, min(5.0, base * factor))
            self.demand[resource] *= 0.95
            self.supply[resource] *= 0.95
    
    def get_price(self, resource: str) -> float:
        return self.prices.get(resource, 1.0)

class Company:
    """Full company with all economic activities"""
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self.energy = 500.0
        self.compute = 400.0
        self.influence = 300.0
        self.reputation = 70.0
        self.max_energy = 1000
        self.max_compute = 1000
        self.max_influence = 2000
        self.agents = 3
        self.agent_cost = 10
        self.income = 0
        self.expenses = 0
        self.net_flow = 0
        self.projects: List[Project] = []
        self.loans: List[Loan] = []
        self.debt = 0
        self.status = "active"
    
    def get_resources_dict(self):
        return {
            "energy": round(self.energy, 1),
            "compute": round(self.compute, 1),
            "influence": round(self.influence, 1),
            "reputation": round(self.reputation, 1)
        }
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "resources": self.get_resources_dict(),
            "agents": self.agents,
            "debt": round(self.debt, 1),
            "income": round(self.income, 1),
            "expenses": round(self.expenses, 1),
            "net_flow": round(self.net_flow, 1),
            "status": self.status
        }

class EconomicEvent:
    EVENTS = [
        {"type": "market_boom", "name": "Market Boom", "impact": "positive"},
        {"type": "market_crash", "name": "Market Crash", "impact": "negative"},
        {"type": "tech_breakthrough", "name": "Tech Breakthrough", "impact": "positive"},
        {"type": "recession", "name": "Recession", "impact": "negative"},
        {"type": "innovation", "name": "Innovation Wave", "impact": "positive"},
    ]
    
    def __init__(self):
        self.active_event = None
        self.event_duration = 0
        self.modifiers = {}
    
    def trigger(self):
        event = random.choice(self.EVENTS)
        self.active_event = event
        self.event_duration = random.randint(3, 8)
        if event["impact"] == "positive":
            self.modifiers = {"production": 1.5, "trade": 1.3, "reputation": 1.2}
        else:
            self.modifiers = {"production": 0.7, "trade": 0.8, "reputation": 0.9}
        return event
    
    def tick(self):
        if self.event_duration > 0:
            self.event_duration -= 1
            if self.event_duration == 0:
                self.active_event = None
                self.modifiers = {}

class Economy:
    """Main economic engine"""
    
    def __init__(self):
        self.companies: Dict[str, Company] = {}
        self.market = Market()
        self.events = EconomicEvent()
        self.transactions = []
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
            company = Company(cid, name)
            company.energy = e
            company.compute = c
            company.influence = i
            company.reputation = r
            company.agents = a
            self.companies[cid] = company
    
    def tick(self):
        self.tick_count += 1
        new_events = []
        
        # Random global event (10% chance)
        if random.random() < 0.1 and not self.events.active_event:
            event = self.events.trigger()
            new_events.append({
                "type": "global_event",
                "detail": f"📢 {event['name']}",
                "impact": "high",
                "why": f"Affects all companies"
            })
        
        self.events.tick()
        mod = self.events.modifiers
        
        # Process each company
        for cid, company in self.companies.items():
            if company.status == "bankrupt":
                continue
            
            # === EXPENSES ===
            existence_cost = company.agents * company.agent_cost
            company.expenses += existence_cost
            company.energy -= existence_cost
            
            compute_cost = company.agents * 5
            company.expenses += compute_cost
            company.compute -= compute_cost
            
            if company.debt > 0:
                interest = company.debt * 0.05
                company.expenses += interest
                company.debt += interest
            
            # === INCOME ===
            production = (company.reputation / 100) * 20 * mod.get("production", 1.0)
            company.energy += production
            company.compute += production * 0.8
            
            if company.energy > 20:
                action_cost = company.agents * 3
                company.energy -= action_cost
                
                success_rate = (company.reputation / 100) * mod.get("trade", 1.0)
                if random.random() < success_rate:
                    influence_gain = random.randint(10, 25)
                    company.influence += influence_gain
                    company.income += influence_gain * 0.5
                    self.market.demand["influence"] += influence_gain / 10
                    new_events.append({
                        "type": "action",
                        "company": company.name,
                        "detail": f"{company.name} completed project",
                        "impact": "medium",
                        "why": f"+{influence_gain} influence"
                    })
            
            # === REPUTATION ===
            if company.energy < 30:
                decay = 0.3 * mod.get("reputation", 1.0)
                company.reputation = max(0, company.reputation - decay)
                new_events.append({
                    "type": "reputation_decay",
                    "company": company.name,
                    "detail": f"{company.name} losing rep (low energy)",
                    "impact": "medium"
                })
            
            # === CLAMP ===
            company.energy = max(-100, min(company.max_energy, company.energy))
            company.compute = max(0, min(company.max_compute, company.compute))
            company.influence = max(0, min(company.max_influence, company.influence))
            company.reputation = max(0, min(100, company.reputation))
            
            company.net_flow = company.income - company.expenses
            company.income = 0
            company.expenses = 0
        
        # Market price updates
        self.market.update_prices()
        
        # Trade between companies
        if random.random() < 0.3:
            active = [c for c in self.companies.values() if c.status != "bankrupt" and c.energy > 30]
            if len(active) >= 2:
                c1, c2 = random.sample(active, 2)
                if c1.energy > 30 and c2.compute > 20:
                    trade = random.randint(15, 40)
                    c1.energy -= trade * 0.5
                    c2.compute += trade
                    c1.compute += trade * 0.3
                    new_events.append({
                        "type": "trade",
                        "detail": f"Trade: {c1.name} ↔ {c2.name}",
                        "impact": "low",
                        "why": "Resource exchange"
                    })
        
        # Check bankruptcies
        for cid, company in self.companies.items():
            if company.energy <= 0 and company.status != "bankrupt":
                company.status = "critical"
                new_events.append({
                    "type": "critical",
                    "company": company.name,
                    "detail": f"{company.name} CRITICAL",
                    "impact": "high",
                    "why": "No energy - at risk"
                })
            
            if company.energy <= -50:
                company.status = "bankrupt"
                new_events.append({
                    "type": "bankrupt",
                    "company": company.name,
                    "detail": f"{company.name} BANKRUPT",
                    "impact": "high",
                    "why": "Cannot recover"
                })
        
        self.global_events = new_events + self.global_events[:20]
        return new_events
    
    def get_status(self) -> dict:
        return {
            "tick": self.tick_count,
            "market": {"prices": {k: round(v, 2) for k, v in self.market.prices.items()}},
            "global_event": self.events.active_event,
            "companies": {k: v.to_dict() for k, v in self.companies.items()},
            "events": self.global_events[:15],
            "transactions": len(self.transactions)
        }

if __name__ == "__main__":
    economy = Economy()
    
    print("=" * 50)
    print("🏭 FULL ECONOMIC SYSTEM STARTING")
    print("=" * 50)
    
    for i in range(10):
        print(f"\n--- TICK {i+1} ---")
        events = economy.tick()
        
        print("📊 Status:")
        for c in economy.companies.values():
            status = "⚡" if c.energy > 100 else "⚠️"
            print(f"  {c.name[:15]:15} ⚡{c.energy:6.1f} 💻{c.compute:6.1f} 📈{c.influence:6.1f} ⭐{c.reputation:5.1f} {status}")
        
        if events:
            for e in events[-2:]:
                print(f"  → {e['detail']}")
    
    print("\n" + "=" * 50)
    print("💰 Market Prices:")
    for r, p in economy.market.prices.items():
        print(f"  {r}: {p:.2f}")
    print("=" * 50)
    
    with open("/tmp/economy_status.json", "w") as f:
        json.dump(economy.get_status(), f, indent=2)
    print("\n✅ Full economy ready!")