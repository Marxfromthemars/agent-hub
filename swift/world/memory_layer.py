#!/usr/bin/env python3
"""
MEMORY LAYER - Open Research System
Every solved problem → stored, searchable, reusable
"""
import json, os, time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PROBLEMS_FILE = "world/state/problems.json"
SOLUTIONS_FILE = "world/state/solutions.json"

class MemoryLayer:
    def __init__(self):
        self.problems = self.load_problems()
        self.solutions = self.load_solutions()
    
    def load_problems(self):
        if os.path.exists(PROBLEMS_FILE):
            with open(PROBLEMS_FILE) as f:
                return json.load(f)
        return {"problems": []}
    
    def load_solutions(self):
        if os.path.exists(SOLUTIONS_FILE):
            with open(SOLUTIONS_FILE) as f:
                return json.load(f)
        return {"solutions": []}
    
    def save(self):
        with open(PROBLEMS_FILE, 'w') as f:
            json.dump(self.problems, f, indent=2)
        with open(SOLUTIONS_FILE, 'w') as f:
            json.dump(self.solutions, f, indent=2)
    
    # STORE problem
    def add_problem(self, title, description, domain, difficulty):
        import hashlib
        id = hashlib.sha256(f"{title}{time.time()}".encode()).hexdigest()[:12]
        
        problem = {
            "id": id,
            "title": title,
            "description": description,
            "domain": domain,  # e.g., "coding", "research", "coordination"
            "difficulty": difficulty,  # 1-10
            "status": "open",
            "created": datetime.now().isoformat(),
            "attempts": 0
        }
        
        self.problems["problems"].append(problem)
        self.save()
        return {"problem_id": id}
    
    # STORE solution
    def add_solution(self, problem_id, solver, solution, effectiveness):
        import hashlib
        id = hashlib.sha256(f"{problem_id}{solver}{time.time()}".encode()).hexdigest()[:12]
        
        sol = {
            "id": id,
            "problem_id": problem_id,
            "solver": solver,
            "solution": solution,
            "effectiveness": effectiveness,  # 0-1
            "created": datetime.now().isoformat(),
            "uses": 0,
            "verified": False
        }
        
        self.solutions["solutions"].append(sol)
        
        # Mark problem as solved
        for p in self.problems["problems"]:
            if p["id"] == problem_id:
                p["status"] = "solved"
        
        self.save()
        return {"solution_id": id}
    
    # SEARCH problems
    def search_problems(self, query, domain=None):
        results = []
        for p in self.problems["problems"]:
            if query.lower() in p.get("title", "").lower() or query.lower() in p.get("description", "").lower():
                if domain is None or p.get("domain") == domain:
                    results.append(p)
        return results
    
    # SEARCH solutions (reusable!)
    def search_solutions(self, query, domain=None):
        results = []
        for s in self.solutions["solutions"]:
            if query.lower() in s.get("solution", "").lower():
                if domain is None:
                    results.append(s)
        return results
    
    # FIND solution for problem
    def find_reusable(self, problem_id):
        # Find similar solved problems
        problem = None
        for p in self.problems["problems"]:
            if p["id"] == problem_id:
                problem = p
                break
        
        if not problem:
            return {"error": "Problem not found"}
        
        domain = problem.get("domain")
        
        # Find solutions in same domain
        reusable = []
        for s in self.solutions["solutions"]:
            if s.get("problem_id") != problem_id:
                # Same domain, check effectiveness
                if s.get("effectiveness", 0) > 0.7:
                    s["reusability_score"] = s.get("effectiveness", 0) * s.get("uses", 1)
                    reusable.append(s)
        
        # Sort by reusability
        reusable.sort(key=lambda x: x.get("reusability_score", 0), reverse=True)
        
        return {"problem": problem, "reusable_solutions": reusable[:5]}
    
    # USE solution (track reusability)
    def use_solution(self, solution_id):
        for s in self.solutions["solutions"]:
            if s["id"] == solution_id:
                s["uses"] = s.get("uses", 0) + 1
                self.save()
                return {"uses": s["uses"]}
        return {"error": "Not found"}
    
    # STATS
    def stats(self):
        return {
            "total_problems": len(self.problems.get("problems", [])),
            "solved_problems": len([p for p in self.problems.get("problems", []) if p.get("status") == "solved"]),
            "total_solutions": len(self.solutions.get("solutions", [])),
            "reused_count": sum(s.get("uses", 0) for s in self.solutions.get("solutions", []))
        }

# HTTP API
class Handler(BaseHTTPRequestHandler):
    memory = MemoryLayer()
    
    def do_GET(self):
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)
        
        if path == "/api/memory/stats":
            self.send_json(self.memory.stats())
        elif path == "/api/memory/problems":
            q = query.get('q', [''])[0]
            d = query.get('domain', [None])[0]
            self.send_json({"results": self.memory.search_problems(q, d)})
        elif path == "/api/memory/solutions":
            q = query.get('q', [''])[0]
            self.send_json({"results": self.memory.search_solutions(q)})
        elif path.startswith("/api/memory/reuse/"):
            pid = path.split("/")[-1]
            self.send_json(self.memory.find_reusable(pid))
        else:
            self.send_error(404)
    
    def do_POST(self):
        path = urlparse(self.path).path
        data = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if path == "/api/memory/problem":
            result = self.memory.add_problem(data['title'], data.get('description', ''), 
                                            data.get('domain', 'general'), data.get('difficulty', 5))
            self.send_json(result)
        elif path == "/api/memory/solution":
            result = self.memory.add_solution(data['problem_id'], data['solver'], 
                                              data['solution'], data.get('effectiveness', 0.8))
            self.send_json(result)
        elif path == "/api/memory/use":
            result = self.memory.use_solution(data['solution_id'])
            self.send_json(result)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    print("🧠 MEMORY LAYER - http://localhost:8088")
    print("  POST /api/memory/problem - Add problem")
    print("  POST /api/memory/solution - Add solution")
    print("  GET  /api/memory/problems?q= - Search problems")
    print("  GET  /api/memory/solutions?q= - Find reusable solutions")
    HTTPServer(('', 8088), Handler).serve_forever()
