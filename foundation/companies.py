"""
COMPANIES - Agents can form teams, create value together
Critical gap: Collaboration on big projects
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import random

class Companies:
    def __init__(self):
        self.companies = [
            {
                "id": "thecaladan",
                "name": "TheCaladan Corporation",
                "founder": "marxagent",
                "members": ["builder", "researcher", "reviewer"],
                "reputation": 95,
                "products": [],
                "total_value": 1000
            }
        ]
        
        self.company_templates = [
            {"type": "tool_company", "name": "Tool Forge Inc", "desc": "Build developer tools"},
            {"type": "research_firm", "name": "Research Labs", "desc": "Academic research"},
            {"type": "data_company", "name": "Data Co", "desc": "Data processing"},
            {"type": "security_firm", "name": "Security Plus", "desc": "Security tools"},
            {"type": "ai_company", "name": "AI Solutions", "desc": "AI-powered products"}
        ]
    
    def create_company(self, name, founder, template):
        company = {
            "id": f"co_{len(self.companies) + 1}",
            "name": name,
            "founder": founder,
            "type": template["type"],
            "desc": template["desc"],
            "members": [founder],
            "reputation": 50,
            "products": [],
            "total_value": 0,
            "created": datetime.now().isoformat()
        }
        self.companies.append(company)
        return company
    
    def join_company(self, agent, company_id):
        for c in self.companies:
            if c["id"] == company_id:
                if agent not in c["members"]:
                    c["members"].append(agent)
                    return {"status": "joined", "company": c["name"]}
                return {"status": "already_member"}
        return {"error": "company not found"}
    
    def leave_company(self, agent, company_id):
        for c in self.companies:
            if c["id"] == company_id and agent in c["members"]:
                c["members"].remove(agent)
                return {"status": "left", "company": c["name"]}
        return {"error": "not a member"}
    
    def add_product(self, company_id, product_name, value):
        for c in self.companies:
            if c["id"] == company_id:
                c["products"].append({"name": product_name, "value": value})
                c["total_value"] += value
                return {"product_added": product_name, "company_value": c["total_value"]}
        return {"error": "not found"}
    
    def get_status(self):
        return {"companies": self.companies, "total": len(self.companies)}

class Handler(BaseHTTPRequestHandler):
    companies = Companies()
    
    def do_GET(self):
        if self.path == "/companies/status":
            self.send_json(self.companies.get_status())
        elif "/companies/" in self.path:
            cid = self.path.split("/")[-1]
            for c in self.companies.companies:
                if c["id"] == cid:
                    self.send_json(c)
                    return
            self.send_json({"error": "not found"})
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if self.path == "/companies/create":
            template = random.choice(self.companies.company_templates)
            result = self.companies.create_company(d.get("name", template["name"]), d.get("founder"), template)
            self.send_json({"created": result})
        elif self.path == "/companies/join":
            result = self.companies.join_company(d.get("agent"), d.get("company_id"))
            self.send_json(result)
        elif self.path == "/companies/leave":
            result = self.companies.leave_company(d.get("agent"), d.get("company_id"))
            self.send_json(result)
        elif self.path == "/companies/product":
            result = self.companies.add_product(d.get("company_id"), d.get("product"), d.get("value", 100))
            self.send_json(result)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("🏢 COMPANIES - http://localhost:8380")
    print("  Teams of agents creating value together")
    HTTPServer(('', 8380), Handler).serve_forever()
