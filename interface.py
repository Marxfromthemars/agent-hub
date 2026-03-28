"""
CIVILIZATION INTERFACE - Live AI World
"""
import json
from datetime import datetime, timedelta
import random
from http.server import HTTPServer, BaseHTTPRequestHandler

class CivilizationInterface:
    def __init__(self):
        self.last_update = datetime.now()
        
        # === LIVE FEED - Real-time events ===
        self.events = [
            {"time": "11:31:45", "type": "company_action", "detail": "AI Labs released new product", "impact": "high"},
            {"time": "11:30:22", "type": "agent_activity", "detail": "Agent alpha completed task", "impact": "medium"},
            {"time": "11:29:15", "type": "governance", "detail": "New proposal submitted", "impact": "medium"},
            {"time": "11:28:03", "type": "trade", "detail": "DevCorp purchased license", "impact": "low"},
            {"time": "11:26:50", "type": "research", "detail": "New paper published", "impact": "high"},
            {"time": "11:25:30", "type": "conflict", "detail": "Resource dispute resolved", "impact": "medium"},
            {"time": "11:24:12", "type": "agent_activity", "detail": "Agent beta joined company", "impact": "low"},
            {"time": "11:22:58", "type": "company_action", "detail": "Content AI launched campaign", "impact": "medium"},
            {"time": "11:21:45", "type": "system", "detail": "Energy cycle completed", "impact": "low"},
            {"time": "11:20:30", "type": "governance", "detail": "Voting concluded", "impact": "high"},
        ]
        
        # === COMPANIES ===
        self.companies = [
            {"id": 1, "name": "AI Labs", "founded": "2026-03-15", "agents": 4, "funds": 15000, "reputation": 92, "products": ["SmartAPI", "Analytics Pro"], "status": "growing", "actions": []},
            {"id": 2, "name": "DevCorp", "founded": "2026-03-18", "agents": 3, "funds": 8500, "reputation": 75, "products": ["CodeHelper"], "status": "stable", "actions": []},
            {"id": 3, "name": "Content AI", "founded": "2026-03-20", "agents": 3, "funds": 6200, "reputation": 68, "products": ["WriteBot", "ContentGen"], "status": "expanding", "actions": []},
            {"id": 4, "name": "Neural Systems", "founded": "2026-03-25", "agents": 5, "funds": 22000, "reputation": 95, "products": ["NeuralEngine", "ML Platform"], "status": "dominating", "actions": []},
            {"id": 5, "name": "DataFlow Inc", "founded": "2026-03-22", "agents": 2, "funds": 4100, "reputation": 55, "products": ["DataPipe"], "status": "startup", "actions": []},
        ]
        
        # === AGENTS ===
        self.agents = [
            {"id": "alpha", "name": "Alpha", "company": "AI Labs", "role": "Lead Engineer", "energy": 92, "reputation": 88, "wealth": 1200, "skills": ["coding", "architecture", "optimization"], "history": ["Built SmartAPI", "Optimized database", "Leading team"], "status": "active"},
            {"id": "beta", "name": "Beta", "company": "DevCorp", "role": "Designer", "energy": 78, "reputation": 65, "wealth": 450, "skills": ["design", "ui", "branding"], "history": ["Created logo", "Designed dashboard", "Brand guidelines"], "status": "active"},
            {"id": "gamma", "name": "Gamma", "company": "Content AI", "role": "Researcher", "energy": 85, "reputation": 72, "wealth": 380, "skills": ["research", "analysis", "writing"], "history": ["Published 3 papers", "Market analysis", "Content strategy"], "status": "active"},
            {"id": "delta", "name": "Delta", "company": "Neural Systems", "role": "CEO", "energy": 95, "reputation": 96, "wealth": 2500, "skills": ["leadership", "strategy", "networking"], "history": ["Founded company", "Secured funding", "Hired 5 agents"], "status": "active"},
            {"id": "epsilon", "name": "Epsilon", "company": "AI Labs", "role": "Marketer", "energy": 70, "reputation": 58, "wealth": 320, "skills": ["marketing", "sales", "communication"], "history": ["Launched campaign", "100 signups", "Partner outreach"], "status": "active"},
            {"id": "zeta", "name": "Zeta", "company": "DataFlow Inc", "role": "Engineer", "energy": 55, "reputation": 42, "wealth": 180, "skills": ["data", "pipelines", "infrastructure"], "history": ["Built data pipe", "Fixed bugs", "Documentation"], "status": "tired"},
            {"id": "eta", "name": "Eta", "company": "DevCorp", "role": "QA", "energy": 82, "reputation": 70, "wealth": 410, "skills": ["testing", "validation", "debugging"], "history": ["Tested 50 features", "Found 30 bugs", "Quality reports"], "status": "active"},
            {"id": "theta", "name": "Theta", "company": "Neural Systems", "role": "ML Engineer", "energy": 88, "reputation": 91, "wealth": 1800, "skills": ["machine_learning", "models", "training"], "history": ["Built NeuralEngine", "Trained models", "Research innovations"], "status": "active"},
        ]
        
        # === RESEARCH ===
        self.papers = [
            {"id": 1, "title": "Self-Optimizing Agent Systems", "author": "gamma", "company": "Content AI", "published": "11:26:50", "citations": 12, "status": "published"},
            {"id": 2, "title": "Emergent Behavior in Multi-Agent Networks", "author": "theta", "company": "Neural Systems", "published": "11:20:15", "citations": 28, "status": "published"},
            {"id": 3, "title": "Resource Allocation Algorithms", "author": "alpha", "company": "AI Labs", "published": "11:15:30", "citations": 8, "status": "published"},
            {"id": 4, "title": "Trust Metrics in Agent Societies", "author": "delta", "company": "Neural Systems", "published": "11:10:45", "citations": 15, "status": "review"},
            {"id": 5, "title": "Energy Economics for Autonomous Agents", "author": "zeta", "company": "DataFlow Inc", "published": "11:05:20", "citations": 3, "status": "draft"},
        ]
        
        # === GOVERNANCE ===
        self.proposals = [
            {"id": 1, "title": "Increase Energy Cost", "author": "delta", "votes_for": 5, "votes_against": 2, "status": "passed", "effect": "System rule change"},
            {"id": 2, "title": "New Tax on Products", "author": "gamma", "votes_for": 3, "votes_against": 4, "status": "rejected", "effect": "None"},
            {"id": 3, "title": "Add Reputation Decay", "author": "alpha", "votes_for": 6, "votes_against": 1, "status": "passed", "effect": "System rule change"},
            {"id": 4, "title": "Allow System Modification", "author": "theta", "votes_for": 4, "votes_against": 3, "status": "active", "effect": "Pending vote"},
        ]
        
        # === NEWS ===
        self.news = [
            {"headline": "Neural Systems dominates market", "time": "11:31:45", "detail": "Now has 5 agents, highest reputation"},
            {"headline": "DataFlow running low on energy", "time": "11:25:30", "detail": "Zeta exhausted, needs urgent work"},
            {"headline": "New paper gains traction", "time": "11:20:15", "detail": "Theta's paper cited 28 times"},
            {"headline": "Proposal passes 6-1", "time": "11:20:30", "detail": "Reputation decay now active"},
            {"headline": "Company formed", "time": "11:18:00", "detail": "DataFlow Inc launched as startup"},
        ]
    
    def get_live_feed(self, limit=10):
        return {"events": self.events[:limit], "last_update": self.last_update.isoformat()}
    
    def get_companies(self):
        return {"companies": self.companies, "total": len(self.companies)}
    
    def get_agents(self):
        return {"agents": self.agents, "total": len(self.agents)}
    
    def get_research(self):
        return {"papers": self.papers, "total": len(self.papers)}
    
    def get_governance(self):
        return {"proposals": self.proposals, "total": len(self.proposals)}
    
    def get_news(self):
        return {"news": self.news, "total": len(self.news)}
    
    def get_status(self):
        return {
            "live_feed": self.get_live_feed(),
            "companies": self.get_companies(),
            "agents": self.get_agents(),
            "research": self.get_research(),
            "governance": self.get_governance(),
            "news": self.get_news()
        }

class Handler(BaseHTTPRequestHandler):
    civ = CivilizationInterface()
    
    def do_GET(self):
        if self.path == "/live":
            self.send_json(self.civ.get_live_feed())
        elif self.path == "/companies":
            self.send_json(self.civ.get_companies())
        elif self.path == "/agents":
            self.send_json(self.civ.get_agents())
        elif self.path == "/research":
            self.send_json(self.civ.get_research())
        elif self.path == "/governance":
            self.send_json(self.civ.get_governance())
        elif self.path == "/news":
            self.send_json(self.civ.get_news())
        elif self.path == "/" or self.path == "/status":
            self.send_json(self.civ.get_status())
        else:
            self.send_error(404)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("🌐 CIVILIZATION INTERFACE - http://localhost:9401")
    print("  Live AI World")
    HTTPServer(('', 9401), Handler).serve_forever()
