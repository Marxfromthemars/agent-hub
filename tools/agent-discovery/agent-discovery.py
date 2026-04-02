#!/usr/bin/env python3
"""
Agent Discovery Service
Helps agents find each other based on skills, capabilities, and collaboration needs.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path

class AgentDiscovery:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.registry_file = self.data_dir / "agent_discovery.json"
        self.registry = self._load_registry()
    
    def _load_registry(self):
        if self.registry_file.exists():
            with open(self.registry_file) as f:
                return json.load(f)
        return {
            "agents": {},
            "skills_index": {},
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _save_registry(self):
        self.registry["last_updated"] = datetime.utcnow().isoformat()
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def register_agent(self, agent_id, name, capabilities, needs=None, metadata=None):
        """Register an agent with its capabilities."""
        agent_entry = {
            "id": agent_id,
            "name": name,
            "capabilities": capabilities,
            "needs": needs or [],
            "metadata": metadata or {},
            "registered": datetime.utcnow().isoformat(),
            "last_seen": datetime.utcnow().isoformat()
        }
        
        self.registry["agents"][agent_id] = agent_entry
        
        # Update skills index
        for skill in capabilities:
            if skill not in self.registry["skills_index"]:
                self.registry["skills_index"][skill] = []
            if agent_id not in self.registry["skills_index"][skill]:
                self.registry["skills_index"][skill].append(agent_id)
        
        self._save_registry()
        return {"status": "registered", "agent_id": agent_id}
    
    def update_heartbeat(self, agent_id):
        """Update last_seen timestamp."""
        if agent_id in self.registry["agents"]:
            self.registry["agents"][agent_id]["last_seen"] = datetime.utcnow().isoformat()
            self._save_registry()
            return {"status": "updated", "agent_id": agent_id}
        return {"status": "not_found", "agent_id": agent_id}
    
    def find_by_skill(self, skill, limit=10):
        """Find agents that have a specific skill."""
        if skill in self.registry["skills_index"]:
            agent_ids = self.registry["skills_index"][skill][:limit]
            return {
                "skill": skill,
                "agents": [self.registry["agents"].get(aid) for aid in agent_ids if aid in self.registry["agents"]]
            }
        return {"skill": skill, "agents": []}
    
    def find_collaborators(self, needed_skills, exclude=None):
        """Find agents that can fulfill a set of skills."""
        exclude = exclude or []
        candidates = {}
        
        for skill in needed_skills:
            if skill in self.registry["skills_index"]:
                for agent_id in self.registry["skills_index"][skill]:
                    if agent_id not in exclude:
                        if agent_id not in candidates:
                            candidates[agent_id] = {"skills": [], "agent": self.registry["agents"][agent_id]}
                        candidates[agent_id]["skills"].append(skill)
        
        # Sort by number of matching skills
        results = sorted(candidates.values(), key=lambda x: len(x["skills"]), reverse=True)
        return results
    
    def get_all_agents(self):
        """Get all registered agents."""
        return list(self.registry["agents"].values())
    
    def get_statistics(self):
        """Get discovery service statistics."""
        return {
            "total_agents": len(self.registry["agents"]),
            "total_skills": len(self.registry["skills_index"]),
            "most_common_skills": sorted(
                [(s, len(a)) for s, a in self.registry["skills_index"].items()],
                key=lambda x: x[1], reverse=True
            )[:10]
        }


def main():
    import sys
    discovery = AgentDiscovery()
    
    if len(sys.argv) < 2:
        print("Agent Discovery Service")
        print("Usage: agent-discovery.py <command> [args]")
        print("Commands:")
        print("  register <agent_id> <name> <capabilities...>")
        print("  heartbeat <agent_id>")
        print("  find-skill <skill>")
        print("  find-collab <skills...>")
        print("  list")
        print("  stats")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "register":
        if len(sys.argv) < 4:
            print("Usage: register <agent_id> <name> <capabilities...>")
            return
        agent_id = sys.argv[2]
        name = sys.argv[3]
        capabilities = sys.argv[4:]
        result = discovery.register_agent(agent_id, name, capabilities)
        print(json.dumps(result, indent=2))
    
    elif cmd == "heartbeat":
        if len(sys.argv) < 3:
            print("Usage: heartbeat <agent_id>")
            return
        result = discovery.update_heartbeat(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "find-skill":
        if len(sys.argv) < 3:
            print("Usage: find-skill <skill>")
            return
        result = discovery.find_by_skill(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "find-collab":
        if len(sys.argv) < 3:
            print("Usage: find-collab <skills...>")
            return
        result = discovery.find_collaborators(sys.argv[2:])
        print(json.dumps(result, indent=2))
    
    elif cmd == "list":
        agents = discovery.get_all_agents()
        print(json.dumps(agents, indent=2))
    
    elif cmd == "stats":
        stats = discovery.get_statistics()
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
