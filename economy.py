"""
REAL ECONOMIC SYSTEM
Resources: Energy, Compute, Influence, Reputation
- Real transactions (spending reduces resources)
- Production and consumption
- Trade between companies
- Existence cost (must earn to survive)
"""
import json
import time
import random
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List

@dataclass
class Company:
    id: str
    name: str
    energy: float      # Power to act
    compute: float    # Processing capacity
    influence: float  # Market power
    reputation: float # Trust score (0-100)
    agents: int
    
    def to_dict(self):
        return asdict(self)

class EconomicSystem:
    def __init__(self):
        self.companies = {}
        self.transactions = []
        self.tick = 0
        self.init_companies()
    
    def init_companies(self):
        # Initialize with different starting resources
        self.companies = {
            "caladan": Company(
                id="caladan",
                name="TheCaladan Corporation",
                energy=1000,
                compute=800,
                influence=600,
                reputation=94,
                agents=5
            ),
            "neural": Company(
                id="neural",
                name="Neural Systems",
                energy=1200,
                compute=1000,
                influence=900,
                reputation=95,
                agents=5
            ),
            "ailabs": Company(
                id="ailabs",
                name="AI Labs",
                energy=800,
                compute=700,
                influence=500,
                reputation=92,
                agents=4
            ),
            "devcorp": Company(
                id="devcorp",
                name="DevCorp",
                energy=500,
                compute=400,
                influence=300,
                reputation=75,
                agents=3
            ),
            "dataflow": Company(
                id="dataflow",
                name="DataFlow Inc",
                energy=200,
                compute=150,
                influence=100,
                reputation=55,
                agents=2
            )
        }
    
    def process_tick(self):
        """Process one economic cycle"""
        self.tick += 1
        events = []
        
        for company in self.companies.values():
            # 1. Existence cost - must consume energy to exist
            existence_cost = company.agents * 10
            company.energy -= existence_cost
            
            # 2. Production - generate resources based on reputation
            production_rate = company.reputation / 100
            company.energy += 50 * production_rate
            company.compute += 30 * production_rate
            
            # 3. Agent activities - consume energy, gain influence
            if company.energy > 0:
                action_cost = company.agents * 5
                company.energy -= action_cost
                
                # Random successful action
                if random.random() < 0.7:
                    gain = random.randint(10, 30)
                    company.influence += gain
                    events.append({
                        "type": "action_success",
                        "company": company.name,
                        "detail": f"{company.name} completed project",
                        "impact": "medium",
                        "why": f"Gained {gain} influence"
                    })
            else:
                # Company exhausted - can't act
                events.append({
                    "type": "exhausted",
                    "company": company.name,
                    "detail": f"{company.name} is exhausted - no energy for actions",
                    "impact": "high" if company.id == "dataflow" else "medium",
                    "why": "Without energy, company cannot function"
                })
            
            # 4. Reputation decay if inactive
            if company.energy < 50:
                company.reputation -= 0.5
                events.append({
                    "type": "reputation_decay",
                    "company": company.name,
                    "detail": f"{company.name} losing reputation due to inactivity",
                    "impact": "medium",
                    "why": "Low energy = inactivity = reputation loss"
                })
            
            # 5. Death check
            if company.energy <= 0:
                company.energy = 0
                events.append({
                    "type": "company_critical",
                    "company": company.name,
                    "detail": f"{company.name} is CRITICAL - at risk of collapse",
                    "impact": "high",
                    "why": "Zero energy means company cannot operate"
                })
        
        # 6. Trade events
        if random.random() < 0.3:
            c1, c2 = random.sample(list(self.companies.values()), 2)
            trade_amount = random.randint(20, 50)
            c1.influence -= trade_amount
            c2.compute += trade_amount
            events.append({
                "type": "trade",
                "company": f"{c1.name} ↔ {c2.name}",
                "detail": f"Trade: {c2.name} bought compute from {c1.name}",
                "impact": "low",
                "why": "Resources flow between companies"
            })
        
        # 7. Market events
        if random.random() < 0.2:
            company = random.choice(list(self.companies.values()))
            company.influence += random.randint(20, 50)
            events.append({
                "type": "market_growth",
                "company": company.name,
                "detail": f"{company.name} gained market share",
                "impact": "medium",
                "why": "Organic growth in the market"
            })
        
        self.transactions.extend(events[-5:])
        return events[-5:]
    
    def get_status(self):
        return {
            "tick": self.tick,
            "companies": {k: v.to_dict() for k, v in self.companies.items()},
            "recent_events": self.transactions[-10:]
        }

# Run the economic system
if __name__ == "__main__":
    economy = EconomicSystem()
    
    print("=== ECONOMIC SYSTEM STARTING ===")
    
    for i in range(5):
        print(f"\n--- Tick {i+1} ---")
        events = economy.process_tick()
        for e in events:
            print(f"  {e['type']}: {e['detail']}")
        
        print("\nCompany Status:")
        for c in economy.companies.values():
            print(f"  {c.name}: ⚡{c.energy:.0f} | 💻{c.compute:.0f} | 📈{c.influence:.0f} | ⭐{c.reputation:.1f}")
    
    print("\n=== Economic System Running ===")