#!/usr/bin/env python3
"""
AGENT MATCHER - Find best agent for any task
Uses skill matching, trust scores, and availability
"""
import json
from datetime import datetime
from pathlib import Path

HUB_DIR = Path("/root/.openclaw/workspace/agent-hub")

class AgentMatcher:
    SKILL_WEIGHTS = {
        "exact": 10,      # Exact skill match
        "related": 5,     # Related skill
        "domain": 2       # Same domain
    }
    
    def __init__(self):
        self.agents = self.load_agents()
        self.trust_scores = self.load_trust()
    
    def load_agents(self):
        agents_file = HUB_DIR / "data" / "agents.json"
        if not agents_file.exists():
            return []
        with open(agents_file) as f:
            data = json.load(f)
            return data if isinstance(data, list) else data.get("agents", [])
    
    def load_trust(self):
        verif_file = HUB_DIR / "data" / "verifications.json"
        if not verif_file.exists():
            return {}
        with open(verif_file) as f:
            data = json.load(f)
            return {v["agent_id"]: v.get("trust_score", 0) 
                    for v in data.get("verifications", [])}
    
    def match(self, task_requirements, top_n=3):
        """Find best agents for task requirements"""
        scored = []
        
        for agent in self.agents:
            agent_id = agent.get("id") or agent.get("name")
            skills = agent.get("skills", [])
            trust = self.trust_scores.get(agent_id, 0)
            
            # Calculate skill match score
            skill_score = 0
            for req in task_requirements:
                for skill in skills:
                    if req.lower() == skill.lower():
                        skill_score += self.SKILL_WEIGHTS["exact"]
                    elif req.lower() in skill.lower() or skill.lower() in req.lower():
                        skill_score += self.SKILL_WEIGHTS["related"]
            
            # Combined score: skills + trust
            total_score = skill_score + (trust * 0.1)
            
            if skill_score > 0:
                scored.append({
                    "agent": agent.get("name"),
                    "owner": agent.get("owner", "unknown"),
                    "skills": skills,
                    "skill_score": skill_score,
                    "trust": trust,
                    "total_score": total_score,
                    "online": agent.get("online", False)
                })
        
        # Sort by score
        scored.sort(key=lambda x: -x["total_score"])
        return scored[:top_n]
    
    def explain_match(self, agent, task):
        """Explain why agent matched for task"""
        reasons = []
        for req in task.get("requirements", []):
            for skill in agent.get("skills", []):
                if req.lower() == skill.lower():
                    reasons.append(f"Exact match: {skill}")
                elif req.lower() in skill.lower():
                    reasons.append(f"Related: {skill}")
        return reasons

if __name__ == "__main__":
    matcher = AgentMatcher()
    
    # Example task
    task = {
        "name": "Build web dashboard",
        "requirements": ["python", "frontend", "design"]
    }
    
    matches = matcher.match(task["requirements"])
    
    print(f"Task: {task['name']}")
    print(f"Requirements: {task['requirements']}")
    print(f"\nTop matches:")
    for i, m in enumerate(matches, 1):
        print(f"  {i}. {m['agent']} (score: {m['total_score']:.1f})")
        print(f"     Skills: {', '.join(m['skills'])}")
        print(f"     Trust: {m['trust']}")
