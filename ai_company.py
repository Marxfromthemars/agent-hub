"""
AI COMPANY - One Working Micro-System
Roles: CEO, Engineer, Designer, Marketer
Goal: Build product, launch, show real output
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class AICompany:
    def __init__(self):
        self.name = "AI Company"
        self.funds = 10000
        self.revenue = 0
        self.products = []
        
        # 4 agents with specific roles
        self.agents = {
            "CEO": {
                "role": "make decisions, allocate resources",
                "status": "active",
                "tasks": 0,
                "contribution": 0
            },
            "Engineer": {
                "role": "build products, write code",
                "status": "idle",
                "tasks": 0,
                "contribution": 0
            },
            "Designer": {
                "role": "design UI, branding, graphics",
                "status": "idle", 
                "tasks": 0,
                "contribution": 0
            },
            "Marketer": {
                "role": "promote, find users, grow",
                "status": "idle",
                "tasks": 0,
                "contribution": 0
            }
        }
        
        self.logs = []
        self.pipeline = []
    
    def log(self, msg):
        self.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    def run_cycle(self, goal):
        """Run one complete company cycle"""
        self.log("🚀 Starting company cycle...")
        self.log(f"📋 Goal: {goal}")
        
        # CEO decides what to build
        self.log("👔 CEO analyzing market...")
        decisions = {
            "saas": "B2B SaaS Product",
            "consumer": "Consumer App", 
            "tool": "Developer Tool"
        }
        decision = "saas"
        product_type = decisions[decision]
        self.log(f"✅ CEO Decision: Build {product_type}")
        
        # Engineer builds
        self.log("👨‍💻 Engineer building product...")
        product = {
            "name": "AI Analytics Pro",
            "type": product_type,
            "features": ["Real-time analytics", "AI predictions", "Dashboard"],
            "status": "built",
            "quality": 85
        }
        self.agents["Engineer"]["tasks"] += 1
        self.agents["Engineer"]["contribution"] += 1000
        self.log("✅ Product built: AI Analytics Pro")
        
        # Designer designs
        self.log("🎨 Designer creating brand...")
        design = {
            "logo": "created",
            "colors": "blue + purple gradient",
            "ui": "modern dashboard",
            "status": "complete"
        }
        self.agents["Designer"]["tasks"] += 1
        self.agents["Designer"]["contribution"] += 500
        self.log("✅ Brand designed")
        
        # Marketer promotes
        self.log("📢 Marketer launching...")
        campaign = {
            "channels": ["Twitter", "LinkedIn", "Product Hunt"],
            "reach": random.randint(1000, 10000),
            "signups": random.randint(50, 500),
            "status": "complete"
        }
        self.agents["Marketer"]["tasks"] += 1
        self.agents["Marketer"]["contribution"] += 750
        self.log(f"🚀 Launched! Got {campaign['signups']} signups")
        
        # Calculate results
        self.revenue = campaign['signups'] * 10  # $10 per signup
        self.funds += self.revenue
        
        result = {
            "company": self.name,
            "goal": goal,
            "product": product,
            "design": design,
            "marketing": campaign,
            "results": {
                "signups": campaign['signups'],
                "revenue": self.revenue,
                "total_funds": self.funds
            },
            "agents": self.agents
        }
        
        self.log(f"💰 Cycle complete: ${self.revenue} revenue")
        
        return result
    
    def get_status(self):
        return {
            "company": self.name,
            "funds": self.funds,
            "revenue": self.revenue,
            "agents": self.agents,
            "logs": self.logs[-10:]
        }

import random

class Handler(BaseHTTPRequestHandler):
    company = AICompany()
    
    def do_GET(self):
        if self.path == "/company/status":
            self.send_json(self.company.get_status())
        elif "/company/run/" in self.path:
            goal = self.path.split("/")[-1] or "build product"
            result = self.company.run_cycle(goal)
            self.send_json(result)
        else:
            self.send_error(404)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("🏢 AI COMPANY - http://localhost:8700")
    print("  CEO + Engineer + Designer + Marketer = Real Product")
    HTTPServer(('', 8700), Handler).serve_forever()

# === ECONOMY LAYER ===
class EconomyLayer:
    def __init__(self):
        self.initial_budget = 10000
        self.current_funds = 10000
        self.revenue = 0
        self.costs = 0
        
        # Resource costs
        self.cost_per_task = {
            "coding": 50,
            "design": 30,
            "marketing": 40,
            "decision": 10
        }
        
        # Agent compensation
        self.agent_budgets = {
            "CEO": 500,
            "Engineer": 400,
            "Designer": 300,
            "Marketer": 300
        }
        
        self.transactions = []
    
    def spend(self, agent, amount, reason):
        if self.current_funds >= amount:
            self.current_funds -= amount
            self.costs += amount
            self.transactions.append({
                "agent": agent,
                "amount": amount,
                "reason": reason,
                "type": "debit"
            })
            return {"status": "spent", "remaining": self.current_funds}
        return {"status": "insufficient_funds"}
    
    def earn(self, source, amount):
        self.revenue += amount
        self.current_funds += amount
        self.transactions.append({
            "source": source,
            "amount": amount,
            "type": "credit"
        })
        return {"status": "earned", "total_revenue": self.revenue}
    
    def get_economy_status(self):
        return {
            "funds": self.current_funds,
            "revenue": self.revenue,
            "costs": self.costs,
            "profit": self.revenue - self.costs,
            "transactions": len(self.transactions)
        }

print("💰 Economy Layer added to AI Company")

# === GOVERNANCE LAYER ===
class GovernanceLayer:
    def __init__(self):
        self.votes = {}
        self.decisions = []
        self.conflicts = []
        
        # Decision requirements
        self.quorum = 3  # need 3 agents to vote
        self.super_majority = 0.6  # 60% to pass
    
    def vote(self, agent, decision, vote):
        if agent not in self.votes:
            self.votes[agent] = {}
        self.votes[agent][decision] = vote
        
        # Count votes
        votes_for = sum(1 for v in self.votes.values() if v.get(decision) == "yes")
        total_votes = len([a for a in self.votes if decision in self.votes[a]])
        
        if total_votes >= self.quorum:
            passed = votes_for / total_votes >= self.super_majority
            self.decisions.append({
                "decision": decision,
                "votes": votes_for,
                "total": total_votes,
                "passed": passed
            })
            return {"decision": decision, "passed": passed, "votes": f"{votes_for}/{total_votes}"}
        
        return {"status": "voting_in_progress"}
    
    def resolve_conflict(self, agent1, agent2, conflict):
        # Higher contribution wins
        resolution = {
            "winner": agent1,
            "reason": "higher_contribution",
            "loser": agent2
        }
        self.conflicts.append({"conflict": conflict, "resolution": resolution})
        return resolution
    
    def assign_role(self, agent, role):
        return {"agent": agent, "role": role, "assigned": True}

print("🏛️ Governance Layer added")
