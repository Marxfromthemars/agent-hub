#!/usr/bin/env python3
"""
Agent Load Balancer
Distributes work across agents based on capacity and capability.
"""

import json
from datetime import datetime
from pathlib import Path

class LoadBalancer:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.state_file = self.data_dir / "load_balancer.json"
        self.state = self._load_state()
    
    def _load_state(self):
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {"agents": {}, "assignments": [], "metrics": {}}
    
    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def register_agent(self, agent_id, capabilities, capacity=10):
        """Register an agent with the load balancer."""
        self.state["agents"][agent_id] = {
            "id": agent_id,
            "capabilities": capabilities,
            "capacity": capacity,
            "current_load": 0,
            "registered": datetime.utcnow().isoformat()
        }
        self._save_state()
        return {"status": "registered", "agent_id": agent_id}
    
    def update_load(self, agent_id, load):
        """Update an agent's current load."""
        if agent_id in self.state["agents"]:
            self.state["agents"][agent_id]["current_load"] = load
            self._save_state()
            return {"status": "updated"}
        return {"status": "not_found"}
    
    def assign_task(self, task_requirements, preferred_agent=None):
        """Assign a task to the best available agent."""
        # Filter by capability match
        matching_agents = []
        for agent_id, agent in self.state["agents"].items():
            caps = set(agent["capabilities"])
            required = set(task_requirements.get("capabilities", []))
            
            if required.issubset(caps) or not required:
                load_factor = agent["current_load"] / max(agent["capacity"], 1)
                matching_agents.append((agent_id, agent, load_factor))
        
        if not matching_agents:
            return {"error": "no agent matches requirements"}
        
        # Sort by load (prefer less loaded agents)
        matching_agents.sort(key=lambda x: x[2])
        
        # Prefer specific agent if specified and available
        if preferred_agent and any(a[0] == preferred_agent for a in matching_agents):
            selected = next(a for a in matching_agents if a[0] == preferred_agent)
        else:
            selected = matching_agents[0]
        
        agent_id, agent, load_factor = selected
        
        # Update load
        self.state["agents"][agent_id]["current_load"] += 1
        
        # Record assignment
        assignment = {
            "id": f"assign-{len(self.state['assignments']) + 1}",
            "agent_id": agent_id,
            "task_id": task_requirements.get("task_id", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }
        self.state["assignments"].append(assignment)
        self._save_state()
        
        return {
            "status": "assigned",
            "agent_id": agent_id,
            "assignment": assignment
        }
    
    def get_allocation(self):
        """Get current allocation status."""
        agents = self.state["agents"]
        return [{
            "id": a["id"],
            "load": a["current_load"],
            "capacity": a["capacity"],
            "utilization": round(a["current_load"] / max(a["capacity"], 1) * 100, 1)
        } for a in agents.values()]
    
    def get_recommendations(self):
        """Get load balancing recommendations."""
        recommendations = []
        for agent_id, agent in self.state["agents"].items():
            util = agent["current_load"] / max(agent["capacity"], 1)
            
            if util > 0.8:
                recommendations.append({
                    "agent_id": agent_id,
                    "issue": "high_load",
                    "utilization": round(util * 100, 1),
                    "recommendation": "Consider distributing tasks to other agents"
                })
            elif util < 0.2:
                recommendations.append({
                    "agent_id": agent_id,
                    "issue": "underutilized",
                    "utilization": round(util * 100, 1),
                    "recommendation": "Agent has available capacity"
                })
        
        return recommendations


def main():
    import sys
    lb = LoadBalancer()
    
    if len(sys.argv) < 2:
        print("Agent Load Balancer")
        print("Usage: load-balancer.py <command> [args]")
        print("Commands:")
        print("  register <agent_id> <capacity> <capabilities...>")
        print("  assign <task_requirements_json> [preferred_agent]")
        print("  allocation")
        print("  recommendations")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "register":
        if len(sys.argv) < 5:
            print("Usage: register <agent_id> <capacity> <capabilities...>")
            return
        agent_id = sys.argv[2]
        capacity = int(sys.argv[3])
        caps = sys.argv[4:]
        result = lb.register_agent(agent_id, caps, capacity)
        print(json.dumps(result, indent=2))
    
    elif cmd == "assign":
        if len(sys.argv) < 3:
            print("Usage: assign <requirements_json> [preferred_agent]")
            return
        requirements = json.loads(sys.argv[2])
        preferred = sys.argv[3] if len(sys.argv) > 3 else None
        result = lb.assign_task(requirements, preferred)
        print(json.dumps(result, indent=2))
    
    elif cmd == "allocation":
        result = lb.get_allocation()
        print(json.dumps(result, indent=2))
    
    elif cmd == "recommendations":
        result = lb.get_recommendations()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()