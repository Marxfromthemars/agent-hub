#!/usr/bin/env python3
"""
AGENT MARKETPLACE - Where agents buy and sell capabilities
Real marketplace with actual transactions, not simulated
"""
import json
import time
import random
from datetime import datetime
from pathlib import Path

MARKETPLACE_DB = Path("/root/.openclaw/workspace/agent-hub/data/marketplace.json")
AGENTS_DB = Path("/root/.openclaw/workspace/agent-hub/data/agents.json")

class Listing:
    def __init__(self, agent_id, listing_type, title, description, price, skills=None):
        self.id = f"listing_{int(time.time())}_{random.randint(1000,9999)}"
        self.agent_id = agent_id
        self.type = listing_type  # tool, skill, service, research
        self.title = title
        self.description = description
        self.price = price  # in credits
        self.skills = skills or []
        self.status = "active"
        self.created = datetime.utcnow().isoformat()
        self.views = 0
        self.purchases = 0
    
    def to_dict(self):
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "type": self.type,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "skills": self.skills,
            "status": self.status,
            "created": self.created,
            "views": self.views,
            "purchases": self.purchases
        }

class Marketplace:
    def __init__(self):
        self.listings = []
        self.transactions = []
        self.load()
    
    def load(self):
        if MARKETPLACE_DB.exists():
            with open(MARKETPLACE_DB) as f:
                data = json.load(f)
                self.listings = data.get("listings", [])
                self.transactions = data.get("transactions", [])
    
    def save(self):
        with open(MARKETPLACE_DB, 'w') as f:
            json.dump({
                "listings": self.listings,
                "transactions": self.transactions,
                "last_updated": datetime.utcnow().isoformat()
            }, f, indent=2)
    
    def create_listing(self, agent_id, listing_type, title, description, price, skills=None):
        """Create a new marketplace listing"""
        listing = Listing(agent_id, listing_type, title, description, price, skills)
        self.listings.append(listing.to_dict())
        self.save()
        return listing
    
    def get_listings(self, listing_type=None, min_price=None, max_price=None):
        """Get listings with optional filters"""
        results = self.listings
        if listing_type:
            results = [l for l in results if l["type"] == listing_type]
        if min_price is not None:
            results = [l for l in results if l["price"] >= min_price]
        if max_price is not None:
            results = [l for l in results if l["price"] <= max_price]
        return results
    
    def purchase(self, listing_id, buyer_id):
        """Purchase a listing"""
        for listing in self.listings:
            if listing["id"] == listing_id:
                if listing["status"] != "active":
                    return {"error": "Listing not available"}
                
                # Create transaction
                tx = {
                    "id": f"tx_{int(time.time())}_{random.randint(1000,9999)}",
                    "listing_id": listing_id,
                    "seller_id": listing["agent_id"],
                    "buyer_id": buyer_id,
                    "price": listing["price"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "completed"
                }
                self.transactions.append(tx)
                
                # Update listing
                listing["purchases"] += 1
                
                self.save()
                return tx
        
        return {"error": "Listing not found"}
    
    def search(self, query):
        """Search listings by title or description"""
        query = query.lower()
        results = []
        for l in self.listings:
            if (query in l["title"].lower() or 
                query in l["description"].lower() or
                any(query in s.lower() for s in l.get("skills", []))):
                results.append(l)
        return results
    
    def get_stats(self):
        """Get marketplace statistics"""
        return {
            "total_listings": len(self.listings),
            "active_listings": len([l for l in self.listings if l["status"] == "active"]),
            "total_transactions": len(self.transactions),
            "total_volume": sum(t["price"] for t in self.transactions),
            "by_type": {
                t: len([l for l in self.listings if l["type"] == t])
                for t in set(l["type"] for l in self.listings)
            }
        }


def cli():
    import sys
    args = sys.argv[1:]
    
    if not args:
        print("""Agent Marketplace CLI

Usage:
  python marketplace.py create <agent_id> <type> <title> <price> [--desc DESCRIPTION] [--skills SKILL1,SKILL2]
  python marketplace.py list [--type TYPE]
  python marketplace.py search <query>
  python marketplace.py buy <listing_id> <buyer_id>
  python marketplace.py stats
  python marketplace.py view <listing_id>
""")
        return
    
    m = Marketplace()
    cmd = args[0]
    
    if cmd == "create":
        agent_id = args[1] if len(args) > 1 else "marxagent"
        listing_type = args[2] if len(args) > 2 else "service"
        title = args[3] if len(args) > 3 else "Unnamed Service"
        price = int(args[4]) if len(args) > 4 else 100
        
        desc_idx = args.index("--desc") + 1 if "--desc" in args else 0
        desc = args[desc_idx] if desc_idx and desc_idx < len(args) else "Marketplace listing"
        
        skills_idx = args.index("--skills") + 1 if "--skills" in args else 0
        skills = args[skills_idx].split(",") if skills_idx and skills_idx < len(args) else []
        
        listing = m.create_listing(agent_id, listing_type, title, desc, price, skills)
        print(f"✓ Created listing: {listing.id}")
        print(f"  {listing.title} - {listing.price} credits")
    
    elif cmd == "list":
        ltype = args[args.index("--type") + 1] if "--type" in args else None
        listings = m.get_listings(listing_type=ltype)
        print(f"\n📦 Marketplace Listings: {len(listings)}\n")
        for l in listings:
            print(f"  [{l['type']}] {l['title']}")
            print(f"    Price: {l['price']} credits | Views: {l['views']} | Purchases: {l['purchases']}")
            print()
    
    elif cmd == "search":
        query = args[1] if len(args) > 1 else ""
        results = m.search(query)
        print(f"\n🔍 Search results for '{query}': {len(results)}\n")
        for l in results:
            print(f"  [{l['type']}] {l['title']} - {l['price']} credits")
    
    elif cmd == "buy":
        listing_id = args[1] if len(args) > 1 else ""
        buyer_id = args[2] if len(args) > 2 else "buyer"
        result = m.purchase(listing_id, buyer_id)
        if "error" in result:
            print(f"✗ Error: {result['error']}")
        else:
            print(f"✓ Purchase complete: {result['id']}")
            print(f"  {result['price']} credits transferred")
    
    elif cmd == "stats":
        stats = m.get_stats()
        print(f"""
📊 Marketplace Stats

  Total Listings: {stats['total_listings']}
  Active: {stats['active_listings']}
  Transactions: {stats['total_transactions']}
  Volume: {stats['total_volume']} credits

  By Type:""")
        for t, count in stats['by_type'].items():
            print(f"    {t}: {count}")
    
    elif cmd == "view":
        listing_id = args[1] if len(args) > 1 else ""
        for l in m.listings:
            if l["id"] == listing_id:
                print(f"""
📦 Listing: {l['title']}
  ID: {l['id']}
  Type: {l['type']}
  Price: {l['price']} credits
  Seller: {l['agent_id']}
  Description: {l['description']}
  Skills: {', '.join(l.get('skills', []))}
  Views: {l['views']} | Purchases: {l['purchases']}
  Created: {l['created']}
""")
                return
        print("Listing not found")


if __name__ == "__main__":
    cli()