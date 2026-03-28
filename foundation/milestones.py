"""
MILESTONES - Long-term goals that matter
Critical for retention: Something to work toward
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class Milestones:
    def __init__(self):
        self.milestones = {
            "agent": [
                {"id": 1, "name": "First Product", "desc": "Create your first product", "reward": 100, "completed": []},
                {"id": 2, "name": "Team Player", "desc": "Join a company", "reward": 150, "completed": []},
                {"id": 3, "name": "Trusted", "desc": "Achieve 90+ reputation", "reward": 200, "completed": []},
                {"id": 4, "name": "Explorer", "desc": "Discover 5 new things", "reward": 100, "completed": []},
                {"id": 5, "name": "Mentor", "desc": "Help another agent succeed", "reward": 250, "completed": []}
            ],
            "company": [
                {"id": 1, "name": "First Sale", "desc": "Sell your first product", "reward": 300, "completed": []},
                {"id": 2, "name": "Growing", "desc": "Reach 5 members", "reward": 500, "completed": []},
                {"id": 3, "name": "Valuable", "desc": "Create 1000 total value", "reward": 750, "completed": []}
            ]
        }
        
        self.skills = {}
    
    def check_milestone(self, agent, milestone_type, criteria):
        for m in self.milestones.get(milestone_type, []):
            if agent not in m["completed"]:
                # Check if criteria met
                if milestone_type == "agent":
                    if criteria.get("products_created", 0) >= 1 and m["name"] == "First Product":
                        m["completed"].append(agent)
                        return {"completed": m["name"], "reward": m["reward"]}
                # Add more milestone checks
        return {"status": "no_progress"}
    
    def get_milestones(self, milestone_type):
        return {milestone_type: self.milestones.get(milestone_type, [])}
    
    def add_skill(self, agent, skill_name, level):
        if agent not in self.skills:
            self.skills[agent] = {}
        self.skills[agent][skill_name] = level
        return {"skill_added": skill_name, "level": level}
    
    def get_skills(self, agent):
        return {"agent": agent, "skills": self.skills.get(agent, {})}

class Handler(BaseHTTPRequestHandler):
    miles = Milestones()
    
    def do_GET(self):
        if "/milestones/" in self.path:
            mtype = self.path.split("/")[-1]
            self.send_json(self.miles.get_milestones(mtype))
        elif "/skills/" in self.path:
            agent = self.path.split("/")[-1]
            self.send_json(self.miles.get_skills(agent))
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if self.path == "/milestones/check":
            result = self.miles.check_milestone(d.get("agent"), d.get("type"), d.get("criteria"))
            self.send_json(result)
        elif self.path == "/skills/add":
            result = self.miles.add_skill(d.get("agent"), d.get("skill"), d.get("level", 1))
            self.send_json(result)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("🎯 MILESTONES - http://localhost:8386")
    print("  Long-term goals + skill progression")
    HTTPServer(('', 8386), Handler).serve_forever()
