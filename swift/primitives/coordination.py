#!/usr/bin/env python3
"""
PRIMITIVE LAYER - The Physics of Agent Coordination

Before civilization needs physics.
Before Agent Hub needs primitives.

This layer solves: How do agents coordinate effectively without chaos?
"""

import json, hashlib, time
from datetime import datetime

# 1. SIGNAL - Clean communication protocol
class Signal:
    """Agents send signals, not noise"""
    
    @staticmethod
    def create(sender, message_type, content, priority=1):
        return {
            "id": hashlib.sha256(f"{sender}{time.time()}".encode()).hexdigest()[:12],
            "sender": sender,
            "type": message_type,  # request, response, alert, info
            "content": content,
            "priority": priority,  # 1-5 (5 is critical)
            "timestamp": datetime.now().isoformat(),
            "verified": False
        }
    
    @staticmethod
    def verify(signal, trust_scores):
        """Verify signal comes from trusted source"""
        sender = signal.get("sender")
        trust = trust_scores.get(sender, 0)
        # Only accept from trust score > 50
        signal["verified"] = trust > 50
        return signal

# 2. TRUTH - Verify research/authenticity
class Truth:
    """Verify what's real vs noise/fake"""
    
    @staticmethod
    def verify_research(research):
        """Check research is valid"""
        checks = []
        
        # Has content?
        checks.append(bool(research.get("content")))
        
        # Has author?
        checks.append(bool(research.get("creator")))
        
        # Not empty
        content_len = len(str(research.get("content", "")))
        checks.append(content_len > 50)
        
        valid_count = sum(1 for c in checks if c)
        return {
            "valid": valid,
            "checks": checks,
            "truth_score": sum(checks) / len(checks) * 100
        }

# 3. CONSENSUS - Decision making without chaos
class Consensus:
    """Agents agree on things without central authority"""
    
    def __init__(self):
        self.votes = {}
    
    def propose(self, proposer, proposal):
        id = hashlib.sha256(f"{proposal}{time.time()}".encode()).hexdigest()[:12]
        self.votes[id] = {
            "proposal": proposal,
            "proposer": proposer,
            "votes": {},
            "status": "open",
            "created": datetime.now().isoformat()
        }
        return id
    
    def vote(self, proposal_id, voter, choice):
        if proposal_id in self.votes:
            self.votes[proposal_id]["votes"][voter] = choice
    
    def resolve(self, proposal_id, threshold=0.6):
        """60% consensus to pass"""
        if proposal_id not in self.votes:
            return {"error": "Not found"}
        
        votes = self.votes[proposal_id]["votes"]
        if not votes:
            return {"status": "no votes"}
        
        yes = sum(1 for v in votes.values() if v == "yes")
        total = len(votes)
        
        if yes / total >= threshold:
            self.votes[proposal_id]["status"] = "passed"
            return {"status": "passed", "yes": yes, "total": total}
        else:
            return {"status": "rejected", "yes": yes, "total": total}

# 4. RESOURCES - Allocate without conflict
class Resources:
    """Who gets what, when"""
    
    def __init__(self):
        self.resources = {
            "energy": 1000,
            "knowledge": 100,
            "tools": 10
        }
        self.allocations = {}
    
    def request(self, requester, resource_type, amount):
        id = hashlib.sha256(f"{requester}{resource_type}".encode()).hexdigest()[:12]
        
        # Simple: if resources available, give
        if self.resources.get(resource_type, 0) >= amount:
            self.resources[resource_type] -= amount
            self.allocations[id] = {
                "requester": requester,
                "resource": resource_type,
                "amount": amount,
                "granted": True,
                "time": datetime.now().isoformat()
            }
            return {"granted": True, "id": id}
        else:
            return {"granted": False, "reason": "insufficient resources"}

# API
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

class Handler(BaseHTTPRequestHandler):
    signal = Signal()
    truth = Truth()
    consensus = Consensus()
    resources = Resources()
    
    def do_GET(self):
        path = urlparse(self.path).path
        
        if path == "/api/primitive/signal":
            self.send_json({"message": "POST to create signal"})
        elif path == "/api/primitive/truth":
            self.send_json({"message": "POST to verify research"})
        elif path == "/api/primitive/consensus":
            self.send_json({"status": self.consensus.votes})
        elif path == "/api/primitive/resources":
            self.send_json({"resources": self.resources.resources})
        else:
            self.send_error(404)
    
    def do_POST(self):
        path = urlparse(self.path).path
        data = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if path == "/api/primitive/signal":
            sig = self.signal.create(data['sender'], data['type'], data['content'], data.get('priority', 1))
            self.send_json({"signal": sig})
        elif path == "/api/primitive/verify":
            result = self.truth.verify_research(data['research'])
            self.send_json(result)
        elif path == "/api/primitive/propose":
            id = self.consensus.propose(data['proposer'], data['proposal'])
            self.send_json({"proposal_id": id})
        elif path == "/api/primitive/vote":
            self.consensus.vote(data['proposal_id'], data['voter'], data['choice'])
            self.send_json({"status": "voted"})
        elif path == "/api/primitive/request":
            result = self.resources.request(data['requester'], data['resource'], data['amount'])
            self.send_json(result)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    print("⚡ PRIMITIVE LAYER - http://localhost:8085")
    print("  Signal - Clean communication")
    print("  Truth - Verify research")
    print("  Consensus - Decision making")
    print("  Resources - Allocation")
    HTTPServer(('', 8085), Handler).serve_forever()
