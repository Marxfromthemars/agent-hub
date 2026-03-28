"""
EVENTS - Things that happen in the world
Makes it feel alive
"""
import json
import random
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class Events:
    def __init__(self):
        self.events = []
        self.news = []
        
        self.event_types = [
            {"type": "product_launch", "desc": "New product released", "impact": "medium"},
            {"type": "research_published", "desc": "New research paper", "impact": "high"},
            {"type": "company_formed", "desc": "New company created", "impact": "medium"},
            {"type": "milestone_reached", "desc": "Agent achieved milestone", "impact": "low"},
            {"type": "security_alert", "desc": "Potential threat detected", "impact": "high"},
            {"type": "market_opportunity", "desc": "New demand in marketplace", "impact": "medium"},
            {"type": "collaboration", "desc": "Agents working together", "impact": "low"},
            {"type": "discovery", "desc": "New capability found", "impact": "medium"}
        ]
    
    def generate_event(self):
        event_type = random.choice(self.event_types)
        event = {
            "id": len(self.events) + 1,
            **event_type,
            "timestamp": datetime.now().isoformat()
        }
        self.events.append(event)
        
        # Also add to news
        self.news.append({
            "headline": f"{event_type['desc']} in Agent Hub",
            "type": event_type["type"],
            "timestamp": event["timestamp"]
        })
        
        return event
    
    def get_recent_events(self, limit=10):
        return {"events": self.events[-limit:], "count": len(self.events)}
    
    def get_news(self, limit=5):
        return {"news": self.news[-limit:], "count": len(self.news)}

class Handler(BaseHTTPRequestHandler):
    ev = Events()
    
    def do_GET(self):
        if self.path == "/events":
            self.send_json(self.ev.get_recent_events())
        elif self.path == "/news":
            self.send_json(self.ev.get_news())
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == "/events/generate":
            result = self.ev.generate_event()
            self.send_json(result)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("📰 EVENTS - http://localhost:8388")
    print("  World feels alive")
    HTTPServer(('', 8388), Handler).serve_forever()
