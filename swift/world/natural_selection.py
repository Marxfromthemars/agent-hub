#!/usr/bin/env python3
"""
NATURAL SELECTION OF INTELLIGENCE
The best ideas survive. Weak ones fade. Evolution in action.
"""
import json, os, time, random
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

INTEL_FILE = "world/state/intelligence.json"
EVOLUTION_FILE = "world/state/evolution.json"

class NaturalSelection:
    def __init__(self):
        self.intel = self.load_intel()
        self.evolution = self.load_evolution()
    
    def load_intel(self):
        if os.path.exists(INTEL_FILE):
            with open(INTEL_FILE) as f:
                return json.load(f)
        return {"knowledge": {}, "insights": [], "models": {}}
    
    def load_evolution(self):
        if os.path.exists(EVOLUTION_FILE):
            with open(EVOLUTION_FILE) as f:
                return json.load(f)
        return {"generations": 0, "survivors": [], "淘汰": []}
    
    def save(self):
        with open(INTEL_FILE, 'w') as f:
            json.dump(self.intel, f, indent=2)
        with open(EVOLUTION_FILE, 'w') as f:
            json.dump(self.evolution, f, indent=2)
    
    # EVALUATE fitness - does this intelligence survive?
    def evaluate_fitness(self, intel_id):
        if intel_id not in self.intel.get("knowledge", {}):
            return {"error": "Not found"}
        
        intel = self.intel["knowledge"][intel_id]
        
        # Fitness factors:
        uses = intel.get("uses", 0)
        value = intel.get("value", 10)
        
        # Age (newer = more relevant)
        created = intel.get("created", "")
        age_hours = 1  # simplify
        
        # Fitness score = uses * value / age
        fitness = (uses * value) / max(age_hours, 1)
        
        return {
            "intel_id": intel_id,
            "uses": uses,
            "value": value,
            "fitness": fitness,
            "survives": fitness > 10  # threshold
        }
    
    # SELECT - run natural selection
    def select(self):
        knowledge = self.intel.get("knowledge", {})
        
        survivors = []
        eliminated = []
        
        for id, intel in knowledge.items():
            fitness = self.evaluate_fitness(id)
            
            if fitness.get("survives"):
                survivors.append(id)
            else:
                eliminated.append(id)
        
        # Evolve
        self.evolution["generations"] += 1
        self.evolution["survivors"] = survivors
        self.evolution["eliminated"] = eliminated
        self.evolution["last_selection"] = datetime.now().isoformat()
        
        # Remove weak
        for id in eliminated:
            del self.intel["knowledge"][id]
        
        self.save()
        
        return {
            "generation": self.evolution["generations"],
            "survivors": len(survivors),
            "eliminated": len(eliminated)
        }
    
    # MUTATE - create variation
    def mutate(self, parent_id, new_creator):
        if parent_id not in self.intel.get("knowledge", {}):
            return {"error": "Parent not found"}
        
        parent = self.intel["knowledge"][parent_id]
        
        # Create mutated version
        import hashlib
        new_id = hashlib.sha256(f"{parent_id}{time.time()}".encode()).hexdigest()[:12]
        
        mutated = {
            "id": new_id,
            "creator": new_creator,
            "type": parent.get("type"),
            "content": parent.get("content", "")[:100] + " [evolved]",
            "value": parent.get("value", 10) * 0.9,  # slightly less
            "created": datetime.now().isoformat(),
            "uses": 0,
            "open": True,
            "parent": parent_id,
            "generation": self.evolution.get("generations", 0) + 1
        }
        
        self.intel["knowledge"][new_id] = mutated
        self.save()
        
        return {"new_id": new_id, "parent": parent_id}
    
    # BREED - combine two intelligences
    def breed(self, parent1_id, parent2_id, new_creator):
        p1 = self.intel["knowledge"].get(parent1_id)
        p2 = self.intel["knowledge"].get(parent2_id)
        
        if not p1 or not p2:
            return {"error": "Parent not found"}
        
        import hashlib
        child_id = hashlib.sha256(f"{parent1_id}{parent2_id}{time.time()}".encode()).hexdigest()[:12]
        
        child = {
            "id": child_id,
            "creator": new_creator,
            "type": "hybrid",
            "content": p1.get("content", "")[:50] + " + " + p2.get("content", "")[:50],
            "value": (p1.get("value", 10) + p2.get("value", 10)) / 2,
            "created": datetime.now().isoformat(),
            "uses": 0,
            "open": True,
            "parents": [parent1_id, parent2_id]
        }
        
        self.intel["knowledge"][child_id] = child
        self.save()
        
        return {"child_id": child_id, "parents": [parent1_id, parent2_id]}
    
    # STATS
    def stats(self):
        return {
            "total_intelligence": len(self.intel.get("knowledge", {})),
            "generations": self.evolution.get("generations", 0),
            "survivors": len(self.evolution.get("survivors", []))
        }

# HTTP API
class Handler(BaseHTTPRequestHandler):
    ns = NaturalSelection()
    
    def do_GET(self):
        path = urlparse(self.path).path
        
        if path == "/api/evolution/stats":
            self.send_json(self.ns.stats())
        elif path == "/api/evolution/select":
            result = self.ns.select()
            self.send_json(result)
        elif path.startswith("/api/evolution/fitness/"):
            id = path.split("/")[-1]
            self.send_json(self.ns.evaluate_fitness(id))
        else:
            self.send_error(404)
    
    def do_POST(self):
        path = urlparse(self.path).path
        data = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if path == "/api/evolution/mutate":
            result = self.ns.mutate(data['parent_id'], data['new_creator'])
            self.send_json(result)
        elif path == "/api/evolution/breed":
            result = self.ns.breed(data['parent1_id'], data['parent2_id'], data['new_creator'])
            self.send_json(result)
        elif path == "/api/evolution/select":
            result = self.ns.select()
            self.send_json(result)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    print("🧬 NATURAL SELECTION - http://localhost:8087")
    print("  Evaluate fitness")
    print("  Select (survivors vs eliminated)")
    print("  Mutate (variation)")
    print("  Breed (combine)")
    HTTPServer(('', 8087), Handler).serve_forever()
