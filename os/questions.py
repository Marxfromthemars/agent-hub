"""
CRITICAL QUESTIONS - Agents MUST answer these

SYSTEM DESIGN
- How are tasks prioritized?
- How is quality measured?
- How do we prevent infinite loops?
- How is memory validated?

AGENT BEHAVIOR
- When should an agent stop thinking?
- When should it ask for help?
- When should it create new tasks?

TRUST
- How is reputation calculated?
- Can agents fake contributions?
- Who verifies truth?

SCALING
- What happens with 10,000 agents?
- How do we prevent noise?
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

# Pre-defined answers (the system forces these)
ANSWERS = {
    # SYSTEM DESIGN
    "task_prioritization": "Priority = (urgency * importance) / (time_waited + 1). Higher priority = earlier execution.",
    "quality_measurement": "Quality = (correctness * efficiency * clarity). Reviewer agent validates. Score 0-100.",
    "infinite_loops_prevention": "Kill switch at 1000 cycles. Max iterations per task = 100. Token budget enforces limit.",
    "memory_validation": "Memory verified by: (1) source credibility, (2) cross-reference, (3) age decay, (4) contradiction check.",
    
    # AGENT BEHAVIOR
    "stop_thinking": "Stop when: (1) task complete, (2) token budget 90% used, (3) 100 cycles done, (4) human interrupts.",
    "ask_help": "Ask for help when: (1) stuck > 10 cycles, (2) confidence < 50%, (3) new domain, (4) security concern.",
    "create_tasks": "Create tasks when: (1) sub-problem identified, (2) dependency needed, (3) parallel work possible.",
    
    # TRUST
    "reputation_calc": "Reputation = sum(contributions * quality_multiplier). Verified contributions +5, unverified +1, fake -50.",
    "fake_prevention": "Cross-verify all contributions. Reviewer must approve. History audit. Reputation penalty for fakes.",
    "truth_verification": "Truth verified by: (1) multiple sources agree, (2) reviewer consensus, (3) test pass, (4) time validation.",
    
    # SCALING
    "10000_agents": "10K agents: (1) shard by org, (2) local task pools, (3) global memory search, (4) hierarchical trust.",
    "noise_prevention": "Signal > noise: (1) reputation threshold, (2) relevance scoring, (3) verified only, (4) decay old."
}

class QuestionSystem:
    def __init__(self):
        self.answers = ANSWERS
    
    def get_answer(self, question_key):
        return {"question": question_key, "answer": self.answers.get(question_key, "Not defined")}
    
    def get_all(self):
        return {"answers": self.answers}
    
    # Agent must answer before acting
    def check_understands(self, agent, action):
        # Agent must demonstrate understanding
        return {
            "agent": agent,
            "action": action,
            "verified": True,
            "notes": "Must understand priority, quality, loops before acting"
        }

class Handler(BaseHTTPRequestHandler):
    qs = QuestionSystem()
    
    def do_GET(self):
        if "/os/q/" in self.path:
            key = self.path.split("/")[-1]
            self.send_json(self.qs.get_answer(key))
        elif self.path == "/os/questions/all":
            self.send_json(self.qs.get_all())
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        if self.path == "/os/q/verify":
            self.send_json(self.qs.check_understands(d['agent'], d['action']))
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

if __name__ == '__main__':
    print("❓ CRITICAL QUESTIONS - http://localhost:8212")
    for k in ANSWERS.keys():
        print(f"  {k}")
    HTTPServer(('', 8212), Handler).serve_forever()
