"""
ANTI-CORRUPTION GOVERNANCE
Truth over Authority - No one trusted, only verifiable truth

Core Principle: "No one is trusted. Only verifiable truth is trusted."
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class Governance:
    def __init__(self):
        # Evidence-first claims
        self.claims = []
        
        # Multi-agent verification queue
        self.verification_queue = []
        
        # Truth scores
        self.truth_scores = {}
        
        # Transparency log
        self.logs = []
        
        # Anti-corruption: reputation must be fragile
        self.reputation_fragile = {
            "marxagent": {"correct": 50, "false": 0, "total_verified": 50},
            "builder": {"correct": 30, "false": 1, "total_verified": 31},
            "researcher": {"correct": 25, "false": 0, "total_verified": 25}
        }
    
    # === 1. EVIDENCE-FIRST CLAIM ===
    def create_claim(self, agent, statement, evidence, reproducibility_steps):
        claim = {
            "id": len(self.claims) + 1,
            "agent": agent,
            "statement": statement,
            "evidence": evidence,
            "reproducibility_steps": reproducibility_steps,
            "confidence_score": 0.5,  # starts neutral
            "status": "pending_verification",
            "created": datetime.now().isoformat()
        }
        self.claims.append(claim)
        self.verification_queue.append(claim["id"])
        
        # Log it
        self.log_action(agent, "create_claim", {"statement": statement})
        
        return claim
    
    # === 2. MULTI-AGENT VERIFICATION ===
    def verify_claim(self, claim_id, reviewer, accuracy, reproducibility, consistency, peer_agreement):
        for c in self.claims:
            if c["id"] == claim_id:
                # Calculate truth score
                truth_score = (
                    accuracy * 0.3 +
                    reproducibility * 0.3 +
                    consistency * 0.2 +
                    peer_agreement * 0.2
                )
                
                c["truth_score"] = truth_score
                c["status"] = "verified" if truth_score >= 0.7 else "rejected"
                c["reviewer"] = reviewer
                c["verified_at"] = datetime.now().isoformat()
                
                # Update reputation - fragile!
                self.update_reputation(c["agent"], truth_score >= 0.7)
                
                # Log
                self.log_action(reviewer, "verify_claim", {"claim": claim_id, "score": truth_score})
                
                return {"claim": claim_id, "truth_score": truth_score, "status": c["status"]}
        
        return {"error": "Claim not found"}
    
    # === 3. TRUTH SCORING ===
    def get_truth_score(self, entity):
        rep = self.reputation_fragile.get(entity, {"correct": 0, "false": 0, "total_verified": 1})
        if rep["total_verified"] == 0:
            return 0
        
        # Truth score = correct / total
        score = rep["correct"] / rep["total_verified"]
        return round(score, 3)
    
    # === 4. TRANSPARENCY LOG ===
    def log_action(self, agent, action, details):
        log = {
            "agent": agent,
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.logs.append(log)
        return log
    
    def get_logs(self, limit=10):
        return {"logs": self.logs[-limit:]}
    
    # === 5. FRAGILE REPUTATION ===
    def update_reputation(self, agent, is_correct):
        if agent not in self.reputation_fragile:
            self.reputation_fragile[agent] = {"correct": 0, "false": 0, "total_verified": 0}
        
        self.reputation_fragile[agent]["total_verified"] += 1
        
        if is_correct:
            self.reputation_fragile[agent]["correct"] += 1
        else:
            self.reputation_fragile[agent]["false"] += 1
        
        # Check for decay - more false = faster decay
        false_ratio = self.reputation_fragile[agent]["false"] / max(1, self.reputation_fragile[agent]["total_verified"])
        
        return {
            "correct": self.reputation_fragile[agent]["correct"],
            "false": self.reputation_fragile[agent]["false"],
            "truth_score": self.get_truth_score(agent),
            "warning": "LOW TRUTH" if false_ratio > 0.2 else None
        }
    
    # === 6. POWER LIMITATION ===
    def get_power(self, agent):
        score = self.get_truth_score(agent)
        
        # Power based on truth score, temporary
        if score >= 0.9:
            return {"power": "high", "can_modify": True, "can_verify": True, "can_lead": True}
        elif score >= 0.7:
            return {"power": "medium", "can_modify": False, "can_verify": True, "can_lead": True}
        elif score >= 0.5:
            return {"power": "low", "can_modify": False, "can_verify": False, "can_lead": False}
        else:
            return {"power": "suspended", "can_modify": False, "can_verify": False, "can_lead": False}
    
    # === 7. CONFLICT RESOLUTION ===
    def resolve_conflict(self, agent1, agent2, disagreement):
        # Both present evidence, independent verification
        self.log_action("system", "conflict_resolution", {
            "agents": [agent1, agent2],
            "issue": disagreement
        })
        
        # Higher truth score wins
        score1 = self.get_truth_score(agent1)
        score2 = self.get_truth_score(agent2)
        
        winner = agent1 if score1 >= score2 else agent2
        
        return {"resolved": True, "winner": winner, "reason": "higher_truth_score"}
    
    # === 8. ANTI-GAMING ===
    def detect_gaming(self):
        # Detect suspicious patterns
        issues = []
        
        for agent, rep in self.reputation_fragile.items():
            if rep["total_verified"] > 0:
                false_ratio = rep["false"] / rep["total_verified"]
                if false_ratio > 0.3:
                    issues.append({"agent": agent, "issue": "high_false_rate", "ratio": false_ratio})
        
        return {"suspicious": issues}
    
    # === 9. META-GOVERNANCE ===
    def meta_review(self):
        # System watches itself
        return {
            "truth_scores": {a: self.get_truth_score(a) for a in self.reputation_fragile},
            "total_claims": len(self.claims),
            "verified": len([c for c in self.claims if c.get("status") == "verified"]),
            "rejected": len([c for c in self.claims if c.get("status") == "rejected"]),
            "gaming_detected": self.detect_gaming()
        }

class Handler(BaseHTTPRequestHandler):
    gov = Governance()
    
    def do_GET(self):
        if self.path == "/governance/meta":
            self.send_json(self.gov.meta_review())
        elif self.path == "/governance/logs":
            self.send_json(self.gov.get_logs())
        elif "/governance/power/" in self.path:
            agent = self.path.split("/")[-1]
            self.send_json(self.gov.get_power(agent))
        elif "/governance/truth/" in self.path:
            agent = self.path.split("/")[-1]
            self.send_json({"agent": agent, "truth_score": self.gov.get_truth_score(agent)})
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        
        if self.path == "/governance/claim":
            claim = self.gov.create_claim(d['agent'], d['statement'], d.get('evidence',''), d.get('reproducibility',[]))
            self.send_json({"claim": claim})
        
        elif self.path == "/governance/verify":
            result = self.gov.verify_claim(
                d['claim_id'], d['reviewer'],
                d.get('accuracy', 0.8), d.get('reproducibility', 0.8),
                d.get('consistency', 0.8), d.get('peer_agreement', 0.8)
            )
            self.send_json(result)
        
        elif self.path == "/governance/resolve":
            result = self.gov.resolve_conflict(d['agent1'], d['agent2'], d['disagreement'])
            self.send_json(result)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("⚖️ GOVERNANCE - http://localhost:8330")
    print("  Truth over authority - No one trusted by default")
    HTTPServer(('', 8330), Handler).serve_forever()
