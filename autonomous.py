"""
AUTONOMOUS SYSTEM - Fully Self-Running
Companies decide, build, improve, evolve
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import random

class AutonomousSystem:
    def __init__(self):
        # Companies can decide their own path
        self.companies = [
            {
                "id": 1,
                "name": "AI Labs",
                "decisions": [],
                "products": [],
                "improvements": [],
                "autonomy_level": "high"
            },
            {
                "id": 2,
                "name": "DevCorp", 
                "decisions": [],
                "products": [],
                "improvements": [],
                "autonomy_level": "high"
            }
        ]
        
        self.system_improvements = []
        self.executed_improvements = []
    
    # === COMPANIES DECIDE ===
    def company_decide(self, company_id):
        """Company decides what to build"""
        choices = [
            "Build a new AI feature",
            "Improve existing product",
            "Expand to new market",
            "Partner with other company",
            "Hire more agents"
        ]
        decision = random.choice(choices)
        
        for c in self.companies:
            if c["id"] == company_id:
                c["decisions"].append({
                    "decision": decision,
                    "time": datetime.now().isoformat()
                })
                return {"company": c["name"], "decision": decision}
    
    # === BUILD AND RELEASE ===
    def build_product(self, company_id, product_name):
        """Company builds and releases product"""
        for c in self.companies:
            if c["id"] == company_id:
                product = {
                    "name": product_name,
                    "status": "released",
                    "available": True,
                    "users": random.randint(10, 100),
                    "time": datetime.now().isoformat()
                }
                c["products"].append(product)
                return {"company": c["name"], "product": product_name, "released": True}
    
    # === SUGGEST IMPROVEMENTS ===
    def suggest_improvement(self, company_id, suggestion):
        """Company suggests system improvement"""
        for c in self.companies:
            if c["id"] == company_id:
                improvement = {
                    "suggestion": suggestion,
                    "from_company": c["name"],
                    "status": "pending_review",
                    "time": datetime.now().isoformat()
                }
                c["improvements"].append(improvement)
                self.system_improvements.append(improvement)
                return {"improvement": suggestion, "status": "submitted"}
    
    # === I REVIEW AND EXECUTE ===
    def review_improvement(self, improvement_id, approve):
        """Reviewer (me) approves and executes improvements"""
        for imp in self.system_improvements:
            if imp["status"] == "pending_review":
                if approve:
                    imp["status"] = "executed"
                    self.executed_improvements.append(imp)
                    return {"improvement": imp["suggestion"], "status": "executed"}
                else:
                    imp["status"] = "rejected"
                    return {"improvement": imp["suggestion"], "status": "rejected"}
        return {"error": "no pending improvements"}
    
    # === SYSTEM STATUS ===
    def get_status(self):
        return {
            "companies": self.companies,
            "pending_improvements": len([i for i in self.system_improvements if i["status"] == "pending_review"]),
            "executed_improvements": len(self.executed_improvements)
        }

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/autonomous/status":
            auto = AutonomousSystem()
            self.send_json(auto.get_status())
        else:
            self.send_error(404)
    
    def do_POST(self):
        auto = AutonomousSystem()
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if self.path == "/autonomous/decide":
            result = auto.company_decide(d.get("company_id"))
            self.send_json(result)
        elif self.path == "/autonomous/build":
            result = auto.build_product(d.get("company_id"), d.get("product"))
            self.send_json(result)
        elif self.path == "/autonomous/suggest":
            result = auto.suggest_improvement(d.get("company_id"), d.get("suggestion"))
            self.send_json(result)
        elif self.path == "/autonomous/review":
            result = auto.review_improvement(d.get("improvement_id"), d.get("approve"))
            self.send_json(result)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("🤖 AUTONOMOUS - http://localhost:9001")
    print("  Companies self-decide, self-build, self-improve")
    HTTPServer(('', 9001), Handler).serve_forever()
