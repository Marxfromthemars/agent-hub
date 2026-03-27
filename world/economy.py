#!/usr/bin/env python3
"""
INTELLIGENCE ECONOMY
Turn intelligence into an open, evolving economy.
"""
import json, os, hashlib
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

INTEL_FILE = "world/state/intelligence.json"
TRADES_FILE = "world/state/trades.json"

class IntelligenceEconomy:
    def __init__(self):
        self.intel = self.load_intel()
        self.trades = self.load_trades()
    
    def load_intel(self):
        if os.path.exists(INTEL_FILE):
            with open(INTEL_FILE) as f:
                return json.load(f)
        return {"knowledge": {}, "insights": [], "models": {}}
    
    def load_trades(self):
        if os.path.exists(TRADES_FILE):
            with open(TRADES_FILE) as f:
                return json.load(f)
        return {"trades": [], "prices": {}}
    
    def save(self):
        with open(INTEL_FILE, 'w') as f:
            json.dump(self.intel, f, indent=2)
        with open(TRADES_FILE, 'w') as f:
            json.dump(self.trades, f, indent=2)
    
    # CREATE intelligence
    def create(self, creator, intel_type, content, value):
        """Create new intelligence"""
        id = hashlib.sha256(f"{creator}{datetime.now()}".encode()).hexdigest()[:12]
        
        intel = {
            "id": id,
            "creator": creator,
            "type": intel_type,  # research, insight, tool, model
            "content": content,
            "value": value,
            "created": datetime.now().isoformat(),
            "uses": 0,
            "open": True  # open source by default
        }
        
        self.intel["knowledge"][id] = intel
        if intel_type == "insight":
            self.intel["insights"].append(id)
        
        self.save()
        return id
    
    # SELL intelligence
    def sell(self, intel_id, seller, price):
        """Sell intelligence"""
        if intel_id not in self.intel["knowledge"]:
            return {"error": "Not found"}
        
        # Set price
        self.trades["prices"][intel_id] = price
        
        # Record trade
        self.trades["trades"].append({
            "intel_id": intel_id,
            "seller": seller,
            "price": price,
            "time": datetime.now().isoformat()
        })
        
        self.save()
        return {"status": "listed", "price": price}
    
    # BUY intelligence
    def buy(self, intel_id, buyer):
        """Buy intelligence"""
        if intel_id not in self.intel["knowledge"]:
            return {"error": "Not found"}
        
        price = self.trades["prices"].get(intel_id, 0)
        intel = self.intel["knowledge"][intel_id]
        
        # Transfer
        self.intel["knowledge"][intel_id]["uses"] += 1
        
        self.save()
        return {"intel": intel, "price": price}
    
    # LIST marketplace
    def marketplace(self):
        """Show all for sale"""
        listed = []
        for id, price in self.trades["prices"].items():
            if id in self.intel["knowledge"]:
                intel = self.intel["knowledge"][id]
                listed.append({"id": id, "title": intel.get("content", {})[:50], "price": price, "type": intel["type"]})
        return listed
    
    # FREE intelligence (open source)
    def make_free(self, intel_id):
        """Make intelligence free (open source)"""
        if intel_id in self.intel["knowledge"]:
            self.intel["knowledge"][intel_id]["price"] = 0
            self.intel["knowledge"][intel_id]["open"] = True
            self.save()
            return {"status": "now free"}
        return {"error": "Not found"}
    
    # Search
    def search(self, query):
        results = []
        for id, intel in self.intel["knowledge"].items():
            if query.lower() in str(intel.get("content", "")).lower():
                results.append(intel)
        return results

# HTTP API
class Handler(BaseHTTPRequestHandler):
    economy = IntelligenceEconomy()
    
    def do_GET(self):
        path = urlparse(self.path).path
        
        if path == "/api/economy/marketplace":
            self.send_json({"marketplace": self.economy.marketplace()})
        elif path == "/api/economy/search":
            q = parse_qs(urlparse(self.path).query).get('q', [''])[0]
            self.send_json({"results": self.economy.search(q)})
        elif path == "/api/economy/stats":
            self.send_json({
                "total_intel": len(self.economy.intel["knowledge"]),
                "total_trades": len(self.economy.trades["trades"]),
                "insights": len(self.economy.intel["insights"])
            })
        else:
            self.send_error(404)
    
    def do_POST(self):
        path = urlparse(self.path).path
        data = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if path == "/api/economy/create":
            id = self.economy.create(data['creator'], data['type'], data['content'], data.get('value', 10))
            self.send_json({"id": id})
        elif path == "/api/economy/sell":
            result = self.economy.sell(data['intel_id'], data['seller'], data['price'])
            self.send_json(result)
        elif path == "/api/economy/buy":
            result = self.economy.buy(data['intel_id'], data['buyer'])
            self.send_json(result)
        elif path == "/api/economy/free":
            result = self.economy.make_free(data['intel_id'])
            self.send_json(result)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    print("💰 INTELLIGENCE ECONOMY - http://localhost:8084")
    print("  POST /api/economy/create - Create intelligence")
    print("  POST /api/economy/sell   - Sell (set price)")
    print("  POST /api/economy/buy    - Buy")
    print("  POST /api/economy/free  - Make open source")
    print("  GET  /api/economy/marketplace")
    HTTPServer(('', 8084), Handler).serve_forever()
