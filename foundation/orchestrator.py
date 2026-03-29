"""
ORCHESTRATOR - Market-based task routing for multi-agent systems
"""
import json
from datetime import datetime

class Orchestrator:
    def __init__(self):
        self.agents = {
            "planner": {"status": "idle", "current_task": None, "skills": ["planning", "breaking_problems"]},
            "builder": {"status": "idle", "current_task": None, "skills": ["coding", "building"]},
            "researcher": {"status": "idle", "current_task": None, "skills": ["research", "analysis"]},
            "reviewer": {"status": "idle", "current_task": None, "skills": ["validation", "quality"]}
        }
        self.task_queue = []
        self.assignments = []

    def add_task(self, task, priority="medium", requirements=None):
        t = {
            "id": len(self.task_queue) + 1,
            "task": task,
            "priority": priority,
            "requirements": requirements or [],
            "status": "queued",
            "created": datetime.now().isoformat()
        }
        self.task_queue.append(t)
        return t

    def decide(self, task):
        """Traditional skill-based routing"""
        requirements = task.get("requirements", [])
        best_agent = None
        best_match = 0
        
        for agent, info in self.agents.items():
            if info["status"] == "idle":
                match = sum(1 for r in requirements if r in info["skills"])
                if match > best_match:
                    best_match = match
                    best_agent = agent
        
        if best_agent:
            return {"assign_to": best_agent, "reason": f"matches {best_match} requirements"}
        return {"assign_to": "queue", "reason": "no idle agents"}

    def market_route(self, task):
        """Market-based routing - agents bid on tasks"""
        eligible_agents = [(aid, info) for aid, info in self.agents.items() 
                          if info["status"] == "idle"]
        
        if not eligible_agents:
            return {"assign_to": "queue", "reason": "no idle agents"}
        
        task_reqs = set(task.get("requirements", []))
        bids = []
        
        for agent_id, agent_info in eligible_agents:
            agent_skills = set(agent_info["skills"])
            match = len(task_reqs & agent_skills)
            
            if match > 0:
                # Lower bid price = more competitive (inverse relationship)
                price = 100 / match
                bids.append({
                    "agent_id": agent_id,
                    "match": match,
                    "price": price,
                    "score": match / price
                })
        
        if bids:
            bids.sort(key=lambda x: x["score"], reverse=True)
            winner = bids[0]["agent_id"]
            return {
                "assign_to": winner,
                "reason": f"best value (match={bids[0]['match']}, bids={len(bids)})",
                "bids": len(bids)
            }
        
        return {"assign_to": "queue", "reason": "no skill matches"}

    def assign(self, task_id, agent):
        """Assign task to agent"""
        for t in self.task_queue:
            if t["id"] == task_id:
                t["status"] = "assigned"
                t["assigned_to"] = agent
                self.agents[agent]["status"] = "working"
                self.assignments.append({"task": task_id, "agent": agent})
                return {"assigned": agent, "task": task_id}
        return {"error": "not found"}

    def get_status(self):
        """Get orchestrator status"""
        busy = sum(1 for a in self.agents.values() if a["status"] == "busy")
        return {
            "agents": len(self.agents),
            "queue": len(self.task_queue),
            "assignments": len(self.assignments),
            "utilization": f"{busy}/{len(self.agents)}"
        }