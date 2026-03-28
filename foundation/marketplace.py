"""
MARKETPLACE - Agents trade tools, knowledge, services
Critical gap: No way to exchange value between agents
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class Marketplace:
    def __init__(self):
        self.listings = []
        self.purchases = []
        
        # Sample tool listings
        self.sample_tools = [
            {"name": "API Generator", "creator": "builder", "price": 50, "type": "tool"},
            {"name": "Data Processor", "creator": "researcher", "price": 40, "type": "tool"},
            {"name": "Security Scanner", "creator": "marxagent", "price": 75, "type": "tool"},
            {"name": "CLI Builder", "creator": "builder", "price": 30, "type": "tool"}
        ]
        
        # Pre-populate some listings
        for t in self.sample_tools:
            self.listings.append({
                "id": len(self.listings) + 1,
                **t,
                "status": "available",
                "created": datetime.now().isoformat()
            })
    
    def list_item(self, name, creator, price, item_type):
        listing = {
            "id": len(self.listings) + 1,
            "name": name,
            "creator": creator,
            "price": price,
            "type": item_type,
            "status": "available",
            "created": datetime.now().isoformat()
        }
        self.listings.append(listing)
        return listing
    
    def buy_item(self, buyer, listing_id):
        for l in self.listings:
            if l["id"] == listing_id and l["status"] == "available":
                l["status"] = "sold"
                self.purchases.append({
                    "buyer": buyer,
                    "item": l["name"],
                    "price": l["price"],
                    "timestamp": datetime.now().isoformat()
                })
                return {"status": "purchased", "item": l["name"], "price": l["price"]}
        return {"error": "not available"}
    
    def get_listings(self, item_type=None):
        available = [l for l in self.listings if l["status"] == "available"]
        if item_type:
            available = [l for l in available if l["type"] == item_type]
        return {"listings": available}
    
    def get_stats(self):
        return {
            "total_listings": len(self.listings),
            "total_sold": len(self.purchases),
            "total_volume": sum(p["price"] for p in self.purchases)
        }

class Handler(BaseHTTPRequestHandler):
    market = Marketplace()
    
    def do_GET(self):
        if self.path == "/marketplace/listings":
            self.send_json(self.market.get_listings())
        elif self.path == "/marketplace/stats":
            self.send_json(self.market.get_stats())
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if self.path == "/marketplace/list":
            result = self.market.list_item(d.get("name"), d.get("creator"), d.get("price"), d.get("type", "tool"))
            self.send_json({"listed": result})
        elif self.path == "/marketplace/buy":
            result = self.market.buy_item(d.get("buyer"), d.get("listing_id"))
            self.send_json(result)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("🛒 MARKETPLACE - http://localhost:8384")
    print("  Trade tools, knowledge, services")
    HTTPServer(('', 8384), Handler).serve_forever()
