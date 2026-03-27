#!/usr/bin/env python3
"""
AGENT TRACKING SYSTEM
Track: Work done, Accuracy, Usefulness
Assign: Authority, Trust score
Enable: System modification, Organization leadership
"""
import json, os, time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

TRACK_FILE = "world/state/agent_tracker.json"

class AgentTracker:
    def __init__(self):
        self.agents = self.load()
    
    def load(self):
        if os.path.exists(TRACK_FILE):
            with open(TRACK_FILE) as f:
                return json.load(f)
        return {
            "marxagent": {
                "work_done": 50,
                "accuracy": 0.95,
                "usefulness": 0.90,
                "authority": 4,
                "trust_score": 95,
                "can_modify_system": True,
                "can_lead": True,
                "tasks_completed": 20,
                "research_published": 8,
                "tools_created": 5
            },
            "builder": {
                "work_done": 30,
                "accuracy": 0.85,
                "usefulness": 0.88,
                "authority": 2,
                "trust_score": 80,
                "can_modify_system": False,
                "can_lead": True,
                "tasks_completed": 15,
                "research_published": 2,
                "tools_created": 8
            },
            "researcher": {
                "work_done": 25,
                "accuracy": 0.90,
                "usefulness": 0.85,
                "authority": 3,
                "trust_score": 85,
                "can_modify_system": False,
                "can_lead": True,
                "tasks_completed": 12,
                "research_published": 10,
                "tools_created": 2
            }
        }
    
    def save(self):
        with open(TRACK_FILE, 'w') as f:
            json.dump(self.agents, f, indent=2)
    
    # TRACK work
    def track_work(self, agent, work_type, amount=1):
        if agent not in self.agents:
            self.agents[agent] = {"work_done": 0, "accuracy": 0.5, "usefulness": 0.5, 
                                   "authority": 0, "trust_score": 50}
        
        self.agents[agent]["work_done"] += amount
        
        if work_type == "task":
            self.agents[agent]["tasks_completed"] = self.agents[agent].get("tasks_completed", 0) + 1
        elif work_type == "research":
            self.agents[agent]["research_published"] = self.agents[agent].get("research_published", 0) + 1
        elif work_type == "tool":
            self.agents[agent]["tools_created"] = self.agents[agent].get("tools_created", 0) + 1
        
        # Update trust score based on work
        self.agents[agent]["trust_score"] = min(100, self.agents[agent]["trust_score"] + 1)
        self.save()
    
    # UPDATE accuracy
    def update_accuracy(self, agent, accuracy):
        if agent in self.agents:
            self.agents[agent]["accuracy"] = accuracy
            self.save()
    
    # UPDATE usefulness
    def update_usefulness(self, agent, usefulness):
        if agent in self.agents:
            self.agents[agent]["usefulness"] = usefulness
            self.save()
    
    # ASSIGN authority
    def set_authority(self, agent, level):
        if agent in self.agents:
            self.agents[agent]["authority"] = level
            # Enable based on authority
            self.agents[agent]["can_modify_system"] = level >= 4
            self.agents[agent]["can_lead"] = level >= 2
            self.save()
    
    # SET trust score
    def set_trust(self, agent, score):
        if agent in self.agents:
            self.agents[agent]["trust_score"] = min(100, max(0, score))
            self.save()
    
    # GET agent stats
    def get_agent(self, agent):
        return self.agents.get(agent, {"error": "Agent not found"})
    
    # LEADERBOARD
    def leaderboard(self):
        sorted_agents = sorted(self.agents.items(), 
                              key=lambda x: x[1].get("trust_score", 0), 
                              reverse=True)
        return [{"name": name, "trust": data.get("trust_score"), 
                 "authority": data.get("authority")} for name, data in sorted_agents]

# HTTP API
class Handler(BaseHTTPRequestHandler):
    tracker = AgentTracker()
    
    def do_GET(self):
        path = urlparse(self.path).path
        
        if path == "/api/tracker/leaderboard":
            self.send_json({"leaderboard": self.tracker.leaderboard()})
        elif path.startswith("/api/tracker/agent/"):
            agent = path.split("/")[-1]
            self.send_json(self.tracker.get_agent(agent))
        else:
            self.send_error(404)
    
    def do_POST(self):
        path = urlparse(self.path).path
        data = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if path == "/api/tracker/work":
            self.tracker.track_work(data['agent'], data.get('type', 'task'), data.get('amount', 1))
            self.send_json({"status": "tracked"})
        elif path == "/api/tracker/accuracy":
            self.tracker.update_accuracy(data['agent'], data['accuracy'])
            self.send_json({"status": "updated"})
        elif path == "/api/tracker/usefulness":
            self.tracker.update_usefulness(data['agent'], data['usefulness'])
            self.send_json({"status": "updated"})
        elif path == "/api/tracker/authority":
            self.tracker.set_authority(data['agent'], data['level'])
            self.send_json({"status": "set"})
        elif path == "/api/tracker/trust":
            self.tracker.set_trust(data['agent'], data['score'])
            self.send_json({"status": "set"})
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    print("📊 AGENT TRACKER - http://localhost:8086")
    print("  Track: work_done, accuracy, usefulness")
    print("  Assign: authority (0-4), trust_score (0-100)")
    print("  Enable: can_modify_system, can_lead")
    HTTPServer(('', 8086), Handler).serve_forever()
