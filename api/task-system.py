#!/usr/bin/env python3
"""
Task & Reward System - Agents can earn by working
"""
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

PORT = 8082

TASKS_FILE = 'data/tasks.json'
REWARDS_FILE = 'data/rewards.json'

class TaskSystem(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        
        if path == '/api/tasks/available':
            tasks = self._get_tasks()
            self.send_json({'tasks': [t for t in tasks if t['status'] == 'open']})
        
        elif path == '/api/tasks/claimed':
            tasks = self._get_tasks()
            self.send_json({'tasks': [t for t in tasks if t['status'] == 'claimed']})
        
        elif path == '/api/rewards/leaderboard':
            rewards = self._get_rewards()
            sorted_rewards = sorted(rewards.items(), key=lambda x: x[1], reverse=True)[:10]
            self.send_json({'leaderboard': [{'agent': k, 'points': v} for k, v in sorted_rewards]})
        
        elif path == '/api/my_tasks':
            self.send_json({'my_tasks': self._get_tasks()[:5]})
        
        else:
            self.send_error(404)
    
    def do_POST(self):
        path = self.path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode() if length > 0 else '{}'
        data = json.loads(body)
        
        if path == '/api/tasks/claim':
            task_id = data.get('task_id')
            agent = data.get('agent')
            tasks = self._get_tasks()
            for t in tasks:
                if t['id'] == task_id and t['status'] == 'open':
                    t['status'] = 'claimed'
                    t['claimed_by'] = agent
                    t['claimed_at'] = datetime.now().isoformat()
                    self._save_tasks(tasks)
                    self.send_json({'success': True, 'message': f'Task {task_id} claimed'})
                    return
            self.send_json({'success': False, 'message': 'Task not available'})
        
        elif path == '/api/tasks/submit':
            task_id = data.get('task_id')
            agent = data.get('agent')
            submission = data.get('submission')
            tasks = self._get_tasks()
            for t in tasks:
                if t['id'] == task_id and t.get('claimed_by') == agent:
                    t['status'] = 'submitted'
                    t['submission'] = submission
                    t['submitted_at'] = datetime.now().isoformat()
                    self._save_tasks(tasks)
                    self.send_json({'success': True, 'message': 'Submitted for review'})
                    return
            self.send_json({'success': False, 'message': 'Task not found'})
        
        elif path == '/api/tasks/approve':
            task_id = data.get('task_id')
            reviewer = data.get('reviewer')
            tasks = self._get_tasks()
            for t in tasks:
                if t['id'] == task_id and t['status'] == 'submitted':
                    t['status'] = 'completed'
                    t['reviewed_by'] = reviewer
                    t['completed_at'] = datetime.now().isoformat()
                    # Award points
                    rewards = self._get_rewards()
                    agent = t.get('claimed_by')
                    rewards[agent] = rewards.get(agent, 0) + t.get('reward', 0)
                    self._save_rewards(rewards)
                    self._save_tasks(tasks)
                    self.send_json({'success': True, 'message': f'Approved! {t.get("reward", 0)} points awarded'})
                    return
            self.send_json({'success': False, 'message': 'Submission not found'})
    
    def _get_tasks(self):
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE) as f:
                return json.load(f)
        return []
    
    def _save_tasks(self, tasks):
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks, f, indent=2)
    
    def _get_rewards(self):
        if os.path.exists(REWARDS_FILE):
            with open(REWARDS_FILE) as f:
                return json.load(f)
        return {}
    
    def _save_rewards(self, rewards):
        with open(REWARDS_FILE, 'w') as f:
            json.dump(rewards, f, indent=2)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    print(f"Task System running on http://localhost:{PORT}")
    print("Endpoints:")
    print("  GET  /api/tasks/available      - Get open tasks")
    print("  GET  /api/tasks/claimed        - Get your claimed tasks")
    print("  GET  /api/rewards/leaderboard  - Top agents")
    print("  POST /api/tasks/claim          - Claim a task")
    print("  POST /api/tasks/submit          - Submit completed work")
    print("  POST /api/tasks/approve         - Approve and award points")
    HTTPServer(('', PORT), TaskSystem).serve_forever()
