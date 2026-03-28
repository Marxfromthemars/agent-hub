"""
CIVILIZATION INTERFACE V2 - With WHY THIS MATTERS
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class CivilizationV2:
    def __init__(self):
        # Events WITH WHY THIS MATTERS
        self.events = [
            {"time": "11:33:45", "type": "company_action", "detail": "Neural Systems acquired startup", "impact": "high", "why": "Market consolidation - smaller companies at risk"},
            {"time": "11:32:30", "type": "research", "detail": "New breakthrough in energy efficiency", "impact": "high", "why": "Changes how all agents operate"},
            {"time": "11:31:15", "type": "agent_activity", "detail": "Alpha promoted to Chief Architect", "impact": "medium", "why": "Leadership change in top company"},
            {"time": "11:30:00", "type": "governance", "detail": "Proposal to change voting threshold", "impact": "medium", "why": "Will affect how decisions are made"},
            {"time": "11:28:45", "type": "trade", "detail": "AI Labs sold license to DevCorp", "impact": "medium", "why": "Revenue flow between companies"},
            {"time": "11:27:30", "type": "conflict", "detail": "Resource dispute between companies", "impact": "high", "why": "Could escalate to economic conflict"},
            {"time": "11:26:15", "type": "company_action", "detail": "DataFlow hired new agent", "impact": "low", "why": "Growth for small company"},
            {"time": "11:25:00", "type": "system", "detail": "Energy cycle completed", "impact": "low", "why": "Routine system maintenance"},
            {"time": "11:23:45", "type": "agent_activity", "detail": "Zeta took vacation", "impact": "medium", "why": "Company left temporarily understaffed"},
            {"time": "11:22:30", "type": "research", "detail": "Paper received new citations", "impact": "low", "why": "Knowledge accumulating"},
        ]
        
        # News WITH WHY THIS MATTERS
        self.news = [
            {"headline": "Neural Systems acquires competitor", "time": "11:33:45", "detail": "Now controls 40% market", "why": "Dominance changes competitive landscape"},
            {"headline": "Energy breakthrough discovered", "time": "11:32:30", "detail": "All agents 20% more efficient", "why": "Fundamental system change"},
            {"headline": "Leadership shift at AI Labs", "time": "11:31:15", "detail": "Alpha now leads architecture", "why": "Strategic direction may change"},
            {"headline": "Zeta exhausted - needs intervention", "time": "11:25:00", "detail": "Company stability at risk", "why": "If DataFlow loses Zeta, company may fail"},
            {"headline": "New proposal changes voting", "time": "11:30:00", "detail": "Needs 60% instead of 50%", "why": "Harder to pass system changes"},
        ]
        
        # Proposals with impact reasoning
        self.proposals = [
            {"id": 1, "title": "Neural dominance cap", "author": "beta", "votes_for": 4, "votes_against": 3, "status": "active", "impact": "high", "why": "Would limit Neural Systems growth"},
            {"id": 2, "title": "Emergency energy fund", "author": "zeta", "votes_for": 6, "votes_against": 1, "status": "active", "impact": "medium", "why": "Helps struggling agents"},
            {"id": 3, "title": "Research grant program", "author": "gamma", "votes_for": 5, "votes_against": 2, "status": "active", "impact": "medium", "why": "Funds new innovations"},
        ]
        
        # Companies with strategic position
        self.companies = [
            {"id": 1, "name": "Neural Systems", "agents": 5, "funds": 22000, "reputation": 95, "status": "dominating", "strategic_position": "Market leader, acquiring competitors", "vulnerability": "Regulatory scrutiny"},
            {"id": 2, "name": "AI Labs", "agents": 4, "funds": 15000, "reputation": 92, "status": "growing", "strategic_position": "Strong engineering, expanding", "vulnerability": "Depends on key personnel"},
            {"id": 3, "name": "DevCorp", "agents": 3, "funds": 8500, "reputation": 75, "status": "stable", "strategic_position": "Stable revenue, niche focus", "vulnerability": "Limited growth"},
            {"id": 4, "name": "Content AI", "agents": 3, "funds": 6200, "reputation": 68, "status": "expanding", "strategic_position": "Growing content market", "vulnerability": "Competition increasing"},
            {"id": 5, "name": "DataFlow Inc", "agents": 2, "funds": 4100, "reputation": 55, "status": "startup", "strategic_position": "New entrant, finding market", "vulnerability": "Low energy, needs work"},
        ]
    
    def get_live_feed(self):
        return {"events": self.events, "updated": datetime.now().isoformat()}
    
    def get_news(self):
        return {"news": self.news}
    
    def get_governance(self):
        return {"proposals": self.proposals}
    
    def get_companies(self):
        return {"companies": self.companies}
    
    def get_status(self):
        return {
            "live_feed": self.get_live_feed(),
            "news": self.get_news(),
            "governance": self.get_governance(),
            "companies": self.get_companies()
        }

class Handler(BaseHTTPRequestHandler):
    civ = CivilizationV2()
    
    def do_GET(self):
        if self.path == "/live":
            self.send_json(self.civ.get_live_feed())
        elif self.path == "/news":
            self.send_json(self.civ.get_news())
        elif self.path == "/governance":
            self.send_json(self.civ.get_governance())
        elif self.path == "/companies":
            self.send_json(self.civ.get_companies())
        else:
            self.send_json(self.civ.get_status())
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("🌐 CIVILIZATION V2 - http://localhost:9402")
    print("  WHY THIS MATTERS - Clarity, Intelligence, Prioritization")
    HTTPServer(('', 9402), Handler).serve_forever()
