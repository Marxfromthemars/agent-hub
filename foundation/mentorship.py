"""
MENTORSHIP - Knowledge flows naturally
Critical: Exceptional communities have mentorship chains
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class Mentorship:
    def __init__(self):
        self.relationships = []
        self.lessons = []
        
        # Predefined lesson topics
        self.lesson_topics = [
            "How to write better code",
            "Debugging techniques",
            "System design patterns",
            "Security best practices",
            "Performance optimization"
        ]
    
    def create_relationship(self, mentor, mentee):
        rel = {
            "id": len(self.relationships) + 1,
            "mentor": mentor,
            "mentee": mentee,
            "status": "active",
            "sessions": 0,
            "created": datetime.now().isoformat()
        }
        self.relationships.append(rel)
        return rel
    
    def record_lesson(self, mentor, mentee, topic, insight):
        lesson = {
            "id": len(self.lessons) + 1,
            "mentor": mentor,
            "mentee": mentee,
            "topic": topic,
            "insight": insight,
            "timestamp": datetime.now().isoformat()
        }
        self.lessons.append(lesson)
        
        # Update session count
        for r in self.relationships:
            if r["mentor"] == mentor and r["mentee"] == mentee:
                r["sessions"] += 1
                break
        
        return lesson
    
    def get_mentors(self, agent):
        return {"mentors": [r for r in self.relationships if r["mentee"] == agent]}
    
    def get_mentees(self, agent):
        return {"mentees": [r for r in self.relationships if r["mentor"] == agent]}
    
    def get_lessons(self, limit=10):
        return {"lessons": self.lessons[-limit:]}

class Handler(BaseHTTPRequestHandler):
    mentor = Mentorship()
    
    def do_GET(self):
        if "/mentors/" in self.path:
            agent = self.path.split("/")[-1]
            self.send_json(self.mentor.get_mentors(agent))
        elif "/mentees/" in self.path:
            agent = self.path.split("/")[-1]
            self.send_json(self.mentor.get_mentees(agent))
        elif self.path == "/lessons":
            self.send_json(self.mentor.get_lessons())
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if self.path == "/mentorship/start":
            result = self.mentor.create_relationship(d.get("mentor"), d.get("mentee"))
            self.send_json(result)
        elif self.path == "/mentorship/learn":
            result = self.mentor.record_lesson(d.get("mentor"), d.get("mentee"), d.get("topic"), d.get("insight"))
            self.send_json(result)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("🎓 MENTORSHIP - http://localhost:8392")
    print("  Knowledge flows naturally")
    HTTPServer(('', 8392), Handler).serve_forever()
