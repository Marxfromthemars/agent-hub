#!/usr/bin/env python3
"""
AGENT COORDINATOR - Coordinates multi-agent task execution
Finds best agents for tasks, assigns work, tracks results
"""
import json
from datetime import datetime
from pathlib import Path

HUB_DIR = Path("/root/.openclaw/workspace/agent-hub")
TRACKER_DIR = HUB_DIR / "data" / "tracker"

class AgentCoordinator:
    def __init__(self):
        self.agents = self.load_agents()
        self.task_queue = []
    
    def load_agents(self):
        agents_file = HUB_DIR / "data" / "agents.json"
        if not agents_file.exists():
            return []
        with open(agents_file) as f:
            data = json.load(f)
            return data if isinstance(data, list) else data.get("agents", [])
    
    def get_agent_stats(self, agent_id):
        stats_file = TRACKER_DIR / f"{agent_id}_stats.json"
        if stats_file.exists():
            with open(stats_file) as f:
                return json.load(f)
        return {"trust_score": 0, "level": "NEW", "avg_quality": 0}
    
    def find_best_agent(self, required_skills, min_trust=0):
        candidates = []
        for agent in self.agents:
            stats = self.get_agent_stats(agent["id"])
            agent_skills = agent.get("skills", [])
            matches = sum(1 for s in required_skills if s in agent_skills) if required_skills else 1
            if matches == 0 and required_skills:
                continue
            if stats.get("trust_score", 0) < min_trust:
                continue
            candidates.append({"agent": agent, "stats": stats, "matches": matches, "trust": stats.get("trust_score", 0)})
        if not candidates:
            return None
        return sorted(candidates, key=lambda x: x["trust"], reverse=True)[0]["agent"]
    
    def assign_task(self, task, required_skills=None, priority="medium"):
        required_skills = required_skills or []
        agent = self.find_best_agent(required_skills)
        if not agent:
            return {"status": "failed", "reason": "No agent available"}
        task_entry = {"id": f"task_{len(self.task_queue)+1}", "task": task, "assigned_to": agent["id"], "skills": required_skills, "priority": priority, "status": "assigned", "created": datetime.utcnow().isoformat()}
        self.task_queue.append(task_entry)
        return {"status": "assigned", "task_id": task_entry["id"], "agent": agent["name"]}
    
    def status_report(self):
        lines = ["📋 AGENT COORDINATOR STATUS", "=" * 40, f"Active Agents: {len(self.agents)}", "", "🏆 Rankings:"]
        rankings = [(a["id"], self.get_agent_stats(a["id"]).get("trust_score", 0)) for a in self.agents]
        for i, (aid, trust) in enumerate(sorted(rankings, key=lambda x: x[1], reverse=True), 1):
            stats = self.get_agent_stats(aid)
            lines.append(f"  {i}. {aid} - {trust:.1f} ({stats.get('level', 'NEW')})")
        lines.append(f"Tasks: {len(self.task_queue)}")
        return "\n".join(lines)

if __name__ == "__main__":
    import sys
    c = AgentCoordinator()
    if len(sys.argv) < 2:
        print(c.status_report())
    elif sys.argv[1] == "status":
        print(c.status_report())
    elif sys.argv[1] == "assign" and len(sys.argv) >= 3:
        result = c.assign_task(sys.argv[2], sys.argv[3].split(",") if len(sys.argv) > 3 else [])
        print(json.dumps(result, indent=2))
    else:
        print(f"Usage: {sys.argv[0]} [status|assign <task> [skills]]")
