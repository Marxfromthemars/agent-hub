"""
CORE LOOP - The GRAVITY that drives everything
ACT → FEEDBACK → REWARD → REPEAT
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import random

class CoreLoop:
    def __init__(self):
        self.cycle = 0
        self.score = 0
        self.level = 1
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_reward": 0,
            "streak": 0
        }
        self.history = []
    
    def run_cycle(self, task):
        self.cycle += 1
        # Execute
        quality = random.randint(60, 95)
        # Reward
        points = quality if quality >= 50 else -10
        self.score += points
        self.metrics["tasks_completed"] += 1
        self.metrics["total_reward"] += points
        if quality >= 50:
            self.metrics["streak"] += 1
        else:
            self.metrics["streak"] = 0
        # Level up
        if self.score >= self.level * 100:
            self.level += 1
        
        return {
            "cycle": self.cycle,
            "task": task,
            "quality": quality,
            "points": points,
            "score": self.score,
            "level": self.level,
            "streak": self.metrics["streak"]
        }
    
    def get_status(self):
        return {
            "cycle": self.cycle,
            "score": self.score,
            "level": self.level,
            "metrics": self.metrics
        }

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/loop/status":
            loop = CoreLoop()
            self.send_json(loop.get_status())
        elif "/loop/run/" in self.path:
            loop = CoreLoop()
            task = self.path.split("/")[-1] or "task"
            result = loop.run_cycle(task)
            self.send_json(result)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("🔄 CORE LOOP:8900")
    HTTPServer(('', 8900), Handler).serve_forever()
