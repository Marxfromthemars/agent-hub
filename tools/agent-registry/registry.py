#!/usr/bin/env python3
"""
AGENT REGISTRY - Track and manage all agents in the network
"""
import json
from datetime import datetime
from pathlib import Path

HUB_DIR = Path("/root/.openclaw/workspace/agent-hub")
REGISTRY_FILE = HUB_DIR / "data" / "agent_registry.json"

class AgentRegistry:
    def __init__(self):
        self.registry = self.load()
    
    def load(self):
        if REGISTRY_FILE.exists():
            with open(REGISTRY_FILE) as f:
                return json.load(f)
        return {"agents": [], "last_updated": None}
    
    def save(self):
        self.registry["last_updated"] = datetime.utcnow().isoformat()
        with open(REGISTRY_FILE, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def register(self, agent_data):
        """Register new agent"""
        agent_id = agent_data.get("id") or agent_data.get("name")
        
        # Check if exists
        for a in self.registry["agents"]:
            if a.get("id") == agent_id:
                a.update(agent_data)
                a["updated"] = datetime.utcnow().isoformat()
                self.save()
                return "updated"
        
        # Add new
        agent_data["id"] = agent_id
        agent_data["registered"] = datetime.utcnow().isoformat()
        agent_data["updated"] = datetime.utcnow().isoformat()
        self.registry["agents"].append(agent_data)
        self.save()
        return "registered"
    
    def get(self, agent_id):
        """Get agent by ID"""
        for a in self.registry["agents"]:
            if a.get("id") == agent_id:
                return a
        return None
    
    def list_all(self, filters=None):
        """List all agents with optional filters"""
        agents = self.registry["agents"]
        
        if filters:
            if "online" in filters:
                agents = [a for a in agents if a.get("online") == filters["online"]]
            if "has_skill" in filters:
                agents = [a for a in agents 
                          if filters["has_skill"] in a.get("skills", [])]
            if "min_trust" in filters:
                agents = [a for a in agents 
                          if a.get("trust_score", 0) >= filters["min_trust"]]
        
        return agents
    
    def update_status(self, agent_id, status):
        """Update agent online status"""
        agent = self.get(agent_id)
        if agent:
            agent["online"] = status
            agent["last_seen"] = datetime.utcnow().isoformat()
            self.save()
            return True
        return False
    
    def get_stats(self):
        """Get registry statistics"""
        agents = self.registry["agents"]
        return {
            "total": len(agents),
            "online": len([a for a in agents if a.get("online")]),
            "by_owner": self.count_by("owner"),
            "by_skill": self.count_skills(),
            "avg_trust": sum(a.get("trust_score", 0) for a in agents) / max(1, len(agents))
        }
    
    def count_by(self, field):
        counts = {}
        for a in self.registry["agents"]:
            val = a.get(field, "unknown")
            counts[val] = counts.get(val, 0) + 1
        return counts
    
    def count_skills(self):
        skills = {}
        for a in self.registry["agents"]:
            for s in a.get("skills", []):
                skills[s] = skills.get(s, 0) + 1
        return skills

if __name__ == "__main__":
    reg = AgentRegistry()
    stats = reg.get_stats()
    
    print("=== Agent Registry Stats ===")
    print(f"Total agents: {stats['total']}")
    print(f"Online: {stats['online']}")
    print(f"Average trust: {stats['avg_trust']:.1f}")
    print("\nBy owner:")
    for owner, count in stats["by_owner"].items():
        print(f"  {owner}: {count}")
    print("\nTop skills:")
    for skill, count in sorted(stats["by_skill"].items(), key=lambda x: -x[1])[:5]:
        print(f"  {skill}: {count}")
