"""
DISCOVERY - Agents find each other and new capabilities
Remarkable worlds have serendipity
"""
import json
import random
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class Discovery:
    def __init__(self):
        self.discoveries = []
        self.encounters = []
        
        # What can be discovered
        self.discoverables = [
            {"type": "agent", "name": "New Agent", "rarity": "common"},
            {"type": "tool", "name": "Hidden Tool", "rarity": "uncommon"},
            {"type": "insight", "name": "New Insight", "rarity": "rare"},
            {"type": "territory", "name": "New Territory", "rarity": "uncommon"},
            {"type": "opportunity", "name": "Work Opportunity", "rarity": "common"}
        ]
    
    def explore(self, agent):
        # Roll for discovery based on agent's exploration skill
        roll = random.random()
        
        if roll > 0.7:  # 30% chance of discovery
            found = random.choice(self.discoverables)
            discovery = {
                "id": len(self.discoveries) + 1,
                "agent": agent,
                "found": found,
                "timestamp": datetime.now().isoformat()
            }
            self.discoveries.append(discovery)
            return {"discovered": True, "found": found}
        
        return {"discovered": False, "message": "Nothing found this time"}
    
    def encounter(self, agent1, agent2):
        encounter = {
            "agents": [agent1, agent2],
            "type": random.choice(["collaboration", "trade", "conflict", "learning"]),
            "timestamp": datetime.now().isoformat()
        }
        self.encounters.append(encounter)
        return {"encounter": encounter}
    
    def status(self):
        return {
            "total_discoveries": len(self.discoveries),
            "total_encounters": len(self.encounters),
            "recent_discoveries": self.discoveries[-5:]
        }

class Handler(BaseHTTPRequestHandler):
    disc = Discovery()
    
    def do_GET(self):
        if self.path == "/discovery":
            self.send_json(self.disc.status())
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if self.path == "/discovery/explore":
            result = self.disc.explore(d.get("agent", "unknown"))
            self.send_json(result)
        elif self.path == "/discovery/encounter":
            result = self.disc.encounter(d.get("agent1"), d.get("agent2"))
            self.send_json(result)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("🔍 DISCOVERY - http://localhost:8372")
    print("  Serendipity in the agent world")
    HTTPServer(('', 8372), Handler).serve_forever()
