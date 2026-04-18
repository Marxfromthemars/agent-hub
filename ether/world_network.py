"""
WORLD NETWORK - Multiple Companies, Competition, Trade
Step 4: Expanding from one company to ecosystem
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class WorldNetwork:
    def __init__(self):
        # Multiple companies
        self.companies = [
            {
                "id": 1,
                "name": "AI Analytics Co",
                "agents": {"CEO": "Alice", "Engineer": "Bob", "Designer": "Carol", "Marketer": "Dave"},
                "funds": 10000,
                "revenue": 5000,
                "products": ["Analytics Pro"],
                "reputation": 85
            },
            {
                "id": 2,
                "name": "DevTools Inc",
                "agents": {"CEO": "Eve", "Engineer": "Frank", "Designer": "Grace", "Marketer": "Hank"},
                "funds": 8000,
                "revenue": 3000,
                "products": ["CodeHelper"],
                "reputation": 70
            },
            {
                "id": 3,
                "name": "Content AI",
                "agents": {"CEO": "Ivy", "Engineer": "Jack", "Designer": "Kate", "Marketer": "Leo"},
                "funds": 5000,
                "revenue": 2000,
                "products": ["WriteBot"],
                "reputation": 65
            }
        ]
        
        # Trade between companies
        self.trades = []
        
        # Competition rankings
        self.rankings = []
        
        # Agents can move between companies
        self.agent_market = []
    
    def run_competition(self):
        """Run competition between companies"""
        results = []
        for c in self.companies:
            # Each company runs a cycle
            revenue = c["revenue"] * (0.8 + (c["reputation"] / 100) * 0.4)  # reputation affects
            c["funds"] += revenue
            results.append({"company": c["name"], "revenue": revenue, "funds": c["funds"]})
        
        # Rank by revenue
        results.sort(key=lambda x: x["revenue"], reverse=True)
        self.rankings = results
        
        return results
    
    def trade(self, from_company, to_company, item, price):
        """Companies can trade with each other"""
        for c in self.companies:
            if c["name"] == from_company and c["funds"] >= price:
                c["funds"] -= price
                for c2 in self.companies:
                    if c2["name"] == to_company:
                        c2["funds"] += price
                        self.trades.append({
                            "from": from_company,
                            "to": to_company,
                            "item": item,
                            "price": price,
                            "time": datetime.now().isoformat()
                        })
                return {"trade": "completed", "item": item, "price": price}
        return {"trade": "failed", "reason": "insufficient_funds"}
    
    def get_world_status(self):
        return {
            "companies": self.companies,
            "rankings": self.rankings,
            "trades": len(self.trades),
            "total_revenue": sum(c["revenue"] for c in self.companies)
        }

class Handler(BaseHTTPRequestHandler):
    world = WorldNetwork()
    
    def do_GET(self):
        if self.path == "/world/status":
            self.send_json(self.world.get_world_status())
        elif self.path == "/world/compete":
            result = self.world.run_competition()
            self.send_json(result)
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        if self.path == "/world/trade":
            result = self.world.trade(d.get("from"), d.get("to"), d.get("item"), d.get("price"))
            self.send_json(result)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("🌐 WORLD NETWORK - http://localhost:8801")
    print("  Multiple companies competing + trading")
    HTTPServer(('', 8801), Handler).serve_forever()
