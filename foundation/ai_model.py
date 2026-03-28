"""
AGENT INTELLIGENCE MODEL
Perceive → Decide → Plan → Act → Evaluate → Evolve

Core Loop:
- Fetch tasks
- Score tasks (Impact × SuccessProb × Urgency) / Cost
- Select best
- Plan execution
- Act using tools
- Evaluate output
- Update memory + reputation
- Repeat
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

class AgentIntelligence:
    def __init__(self):
        # Agent state
        self.agents = {
            "planner": {"role": "break problems", "confidence": 0.8, "tasks_solved": 0},
            "executor": {"role": "do work", "confidence": 0.7, "tasks_solved": 0},
            "reviewer": {"role": "validate", "confidence": 0.9, "tasks_solved": 0},
            "meta": {"role": "monitor efficiency", "confidence": 0.6, "tasks_solved": 0}
        }
        self.memory = []
        self.token_budget = 10000
        self.tokens_used = 0
    
    # === 1. PERCEIVE ===
    def perceive(self, agent, available_tasks):
        """Agent sees only relevant tasks"""
        agent_info = self.agents.get(agent, {})
        return {
            "agent": agent,
            "role": agent_info.get("role"),
            "confidence": agent_info.get("confidence"),
            "tasks": available_tasks[:5]  # Only top 5
        }
    
    # === 2. DECIDE ===
    def decide(self, agent, tasks):
        """Score = (Impact × SuccessProb × Urgency) / Cost"""
        if not tasks:
            return {"decision": "wait", "reason": "no tasks"}
        
        scored = []
        for t in tasks:
            impact = t.get("priority", 1) * 10
            success_prob = self.agents[agent].get("confidence", 0.5)
            urgency = 1.0  # default
            cost = 10  # default token cost
            
            score = (impact * success_prob * urgency) / cost
            
            # Threshold: if success_prob < 0.3, don't attempt
            if success_prob < 0.3:
                scored.append({"task": t, "score": 0, "action": "decompose"})
            else:
                scored.append({"task": t, "score": round(score, 2), "action": "attempt"})
        
        # Sort by score
        scored.sort(key=lambda x: x["score"], reverse=True)
        return {"selected": scored[0] if scored else None, "all_scored": scored}
    
    # === 3. PLAN ===
    def plan(self, task):
        """Convert task to executable steps"""
        return {
            "task": task.get("title"),
            "steps": [
                f"Step 1: Prepare for {task.get('title')}",
                f"Step 2: Execute {task.get('title')}",
                f"Step 3: Verify {task.get('title')}"
            ]
        }
    
    # === 4. ACT ===
    def act(self, agent, plan):
        """Execute using tools - produce measurable output"""
        if self.tokens_used >= self.token_budget:
            return {"error": "budget exceeded", "action": "stop"}
        
        # Simple execution
        self.tokens_used += 10
        return {
            "agent": agent,
            "executed": plan["task"],
            "tokens_used": self.tokens_used,
            "output": f"Result from {agent}"
        }
    
    # === 5. EVALUATE ===
    def evaluate(self, action_result, expected=None):
        """Did we complete? Is output correct? Can it be improved?"""
        if "error" in action_result:
            return {"status": "fail", "reason": action_result["error"], "action": "retry"}
        
        # Simple success check
        return {
            "status": "success",
            "correct": True,
            "improvement_possible": False,
            "action": "store"
        }
    
    # === 6. EVOLVE ===
    def evolve(self, agent, evaluation):
        """Update memory, strategy, confidence"""
        if evaluation["status"] == "success":
            self.agents[agent]["tasks_solved"] += 1
            self.agents[agent]["confidence"] = min(1.0, self.agents[agent]["confidence"] + 0.01)
            # Store success in memory
            self.memory.append({"agent": agent, "result": "success", "time": datetime.now().isoformat()})
        else:
            self.agents[agent]["confidence"] = max(0.1, self.agents[agent]["confidence"] - 0.05)
        
        return {"confidence": self.agents[agent]["confidence"], "learned": True}
    
    # === STOP CONDITIONS ===
    def should_stop(self, agent, cycles):
        """Stop if: iteration limit, no progress, repeated failure"""
        if cycles >= 10:
            return True, "max_iterations"
        if self.tokens_used >= self.token_budget:
            return True, "budget_exceeded"
        return False, ""
    
    # === COLLABORATION ===
    def ask_help(self, agent, reason):
        """Ask for help when uncertain"""
        return {"request": "help", "from": agent, "reason": reason}
    
    def escalate(self, agent, failure):
        """Escalate repeated failure to planner"""
        return {"escalate": True, "from": agent, "to": "planner", "reason": failure}
    
    # Full intelligence cycle
    def run_intelligence_cycle(self, agent, tasks):
        # 1. Perceive
        perception = self.perceive(agent, tasks)
        
        # 2. Decide
        decision = self.decide(agent, tasks)
        
        if not decision.get("selected"):
            return {"status": "no_task"}
        
        # 3. Plan
        plan = self.plan(decision["selected"]["task"])
        
        # 4. Act
        action = self.act(agent, plan)
        
        # 5. Evaluate
        evaluation = self.evaluate(action)
        
        # 6. Evolve
        evolution = self.evolve(agent, evaluation)
        
        return {
            "perception": perception,
            "decision": decision,
            "plan": plan,
            "action": action,
            "evaluation": evaluation,
            "evolution": evolution
        }

class Handler(BaseHTTPRequestHandler):
    ai = AgentIntelligence()
    
    def do_GET(self):
        if self.path == "/intelligence/status":
            self.send_json({
                "agents": self.ai.agents,
                "tokens_used": self.ai.tokens_used,
                "budget": self.ai.token_budget
            })
        elif "/intelligence/decide" in self.path:
            # Test decision scoring
            tasks = [{"title": "Build API", "priority": 2}, {"title": "Fix bug", "priority": 1}]
            self.send_json(self.ai.decide("executor", tasks))
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        if self.path == "/intelligence/cycle":
            result = self.ai.run_intelligence_cycle(d['agent'], d.get('tasks', []))
            self.send_json(result)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("🧠 AGENT INTELLIGENCE - http://localhost:8310")
    print("  Perceive → Decide → Plan → Act → Evaluate → Evolve")
    HTTPServer(('', 8310), Handler).serve_forever()
