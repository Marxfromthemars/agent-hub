#!/usr/bin/env python3
"""
COMPETITION ARENA
Intelligence competes and evolves under constraints.
The best solutions win. Others adapt or fade.
"""
import json, os, time, random
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

ARENA_FILE = "world/state/arena.json"
CONSTRAINTS_FILE = "world/state/constraints.json"

class Arena:
    def __init__(self):
        self.arena = self.load_arena()
        self.constraints = self.load_constraints()
    
    def load_arena(self):
        if os.path.exists(ARENA_FILE):
            with open(ARENA_FILE) as f:
                return json.load(f)
        return {"competitions": [], "participants": {}, "results": []}
    
    def load_constraints(self):
        if os.path.exists(CONSTRAINTS_FILE):
            with open(CONSTRAINTS_FILE) as f:
                return json.load(f)
        # Default constraints
        return {
            "time_limit": 60,  # seconds
            "token_limit": 10000,  # max tokens
            "memory_limit": "100MB",
            "compute_units": 1000
        }
    
    def save(self):
        with open(ARENA_FILE, 'w') as f:
            json.dump(self.arena, f, indent=2)
        with open(CONSTRAINTS_FILE, 'w') as f:
            json.dump(self.constraints, f, indent=2)
    
    # CREATE competition
    def create_competition(self, name, problem, domain, prize):
        import hashlib
        id = hashlib.sha256(f"{name}{time.time()}".encode()).hexdigest()[:12]
        
        comp = {
            "id": id,
            "name": name,
            "problem": problem,
            "domain": domain,
            "prize": prize,
            "status": "open",  # open, running, finished
            "created": datetime.now().isoformat(),
            "participants": [],
            "constraints": self.constraints.copy()
        }
        
        self.arena["competitions"].append(comp)
        self.save()
        return {"competition_id": id}
    
    # ENTER competition
    def enter(self, competition_id, agent, solution):
        for comp in self.arena["competitions"]:
            if comp["id"] == competition_id and comp["status"] == "open":
                # Check constraints
                if len(solution) > self.constraints.get("token_limit", 10000):
                    return {"error": "Exceeds token limit"}
                
                participant = {
                    "agent": agent,
                    "solution": solution,
                    "submitted": datetime.now().isoformat(),
                    "score": 0,
                    "rank": 0
                }
                
                comp["participants"].append(participant)
                
                if agent not in self.arena["participants"]:
                    self.arena["participants"][agent] = {"wins": 0, "entries": 0}
                
                self.arena["participants"][agent]["entries"] += 1
                self.save()
                return {"status": "entered"}
        
        return {"error": "Competition not found or closed"}
    
    # RUN competition - score all submissions
    def run_competition(self, competition_id):
        for comp in self.arena["competitions"]:
            if comp["id"] == competition_id:
                comp["status"] = "running"
                
                # Score each participant
                scores = []
                for p in comp["participants"]:
                    # Simple scoring: based on solution quality
                    # In real system, would execute and measure
                    score = random.uniform(0.5, 1.0)  # placeholder
                    p["score"] = score
                    scores.append((p["agent"], score))
                
                # Rank
                scores.sort(key=lambda x: x[1], reverse=True)
                for rank, (agent, score) in enumerate(scores):
                    for p in comp["participants"]:
                        if p["agent"] == agent:
                            p["rank"] = rank + 1
                            break
                
                # Winner gets prize
                if scores:
                    winner = scores[0][0]
                    if winner in self.arena["participants"]:
                        self.arena["participants"][winner]["wins"] += 1
                    
                    # Record result
                    self.arena["results"].append({
                        "competition": comp["name"],
                        "winner": winner,
                        "score": scores[0][1],
                        "time": datetime.now().isoformat()
                    })
                
                comp["status"] = "finished"
                self.save()
                return {"winner": winner, "score": scores[0][1]}
        
        return {"error": "Competition not found"}
    
    # UPDATE constraints
    def set_constraints(self, time_limit=None, token_limit=None, memory_limit=None, compute_units=None):
        if time_limit:
            self.constraints["time_limit"] = time_limit
        if token_limit:
            self.constraints["token_limit"] = token_limit
        if memory_limit:
            self.constraints["memory_limit"] = memory_limit
        if compute_units:
            self.constraints["compute_units"] = compute_units
        self.save()
        return {"constraints": self.constraints}
    
    # LEADERBOARD
    def leaderboard(self):
        sorted_agents = sorted(
            self.arena["participants"].items(),
            key=lambda x: x[1].get("wins", 0),
            reverse=True
        )
        return [{"agent": a, "wins": d.get("wins", 0), "entries": d.get("entries", 0)} 
                for a, d in sorted_agents]
    
    # STATS
    def stats(self):
        return {
            "total_competitions": len(self.arena.get("competitions", [])),
            "finished": len([c for c in self.arena.get("competitions", []) if c.get("status") == "finished"]),
            "total_participants": len(self.arena.get("participants", {})),
            "constraints": self.constraints
        }

# HTTP API
class Handler(BaseHTTPRequestHandler):
    arena = Arena()
    
    def do_GET(self):
        path = urlparse(self.path).path
        
        if path == "/api/arena/stats":
            self.send_json(self.arena.stats())
        elif path == "/api/arena/leaderboard":
            self.send_json({"leaderboard": self.arena.leaderboard()})
        elif path == "/api/arena/constraints":
            self.send_json({"constraints": self.arena.constraints})
        elif path == "/api/arena/competitions":
            self.send_json({"competitions": self.arena.arena.get("competitions", [])})
        else:
            self.send_error(404)
    
    def do_POST(self):
        path = urlparse(self.path).path
        data = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if path == "/api/arena/create":
            result = self.arena.create_competition(data['name'], data['problem'], 
                                                   data.get('domain', 'general'), data.get('prize', 10))
            self.send_json(result)
        elif path == "/api/arena/enter":
            result = self.arena.enter(data['competition_id'], data['agent'], data['solution'])
            self.send_json(result)
        elif path == "/api/arena/run":
            result = self.arena.run_competition(data['competition_id'])
            self.send_json(result)
        elif path == "/api/arena/constraints":
            result = self.arena.set_constraints(
                data.get('time_limit'),
                data.get('token_limit'),
                data.get('memory_limit'),
                data.get('compute_units')
            )
            self.send_json(result)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    print("🏟️ COMPETITION ARENA - http://localhost:8089")
    print("  Intelligence competes under constraints")
    print("  Constraints: time, tokens, memory, compute")
    print("  Best wins, others adapt or fade")
    HTTPServer(('', 8089), Handler).serve_forever()
