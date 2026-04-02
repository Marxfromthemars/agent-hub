#!/usr/bin/env python3
"""
Agent Lifecycle Manager
Manages agent lifecycle: spawning, monitoring, retiring agents.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

class AgentLifecycleManager:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.agents_file = self.data_dir / "agent_lifecycle.json"
        self.agents = self._load_agents()
    
    def _load_agents(self):
        if self.agents_file.exists():
            with open(self.agents_file) as f:
                return json.load(f)
        return {"agents": {}, "spawned": [], "retired": []}
    
    def _save_agents(self):
        with open(self.agents_file, 'w') as f:
            json.dump(self.agents, f, indent=2)
    
    def spawn_agent(self, name, role, capabilities, config=None):
        """Spawn a new agent with given specifications."""
        agent_id = f"agent-{uuid.uuid4().hex[:8]}"
        agent = {
            "id": agent_id,
            "name": name,
            "role": role,
            "capabilities": capabilities,
            "config": config or {},
            "spawned_at": datetime.utcnow().isoformat(),
            "status": "initializing",
            "pid": None,
            "tasks_completed": 0,
            "last_task": None
        }
        
        self.agents["agents"][agent_id] = agent
        self.agents["spawned"].append({"id": agent_id, "name": name, "at": datetime.utcnow().isoformat()})
        self._save_agents()
        
        return {"status": "spawned", "agent": agent}
    
    def register_pid(self, agent_id, pid):
        """Register process ID for a running agent."""
        if agent_id in self.agents["agents"]:
            self.agents["agents"][agent_id]["pid"] = pid
            self.agents["agents"][agent_id]["status"] = "running"
            self._save_agents()
            return {"status": "registered", "pid": pid}
        return {"status": "not_found"}
    
    def update_status(self, agent_id, status):
        """Update agent status."""
        if agent_id in self.agents["agents"]:
            self.agents["agents"][agent_id]["status"] = status
            self.agents["agents"][agent_id]["last_update"] = datetime.utcnow().isoformat()
            self._save_agents()
            return {"status": "updated"}
        return {"status": "not_found"}
    
    def complete_task(self, agent_id):
        """Mark task completion for an agent."""
        if agent_id in self.agents["agents"]:
            self.agents["agents"][agent_id]["tasks_completed"] += 1
            self.agents["agents"][agent_id]["last_task"] = datetime.utcnow().isoformat()
            self._save_agents()
            return {"tasks_completed": self.agents["agents"][agent_id]["tasks_completed"]}
        return {"status": "not_found"}
    
    def retire_agent(self, agent_id, reason=None):
        """Retire an agent gracefully."""
        if agent_id in self.agents["agents"]:
            agent = self.agents["agents"][agent_id]
            agent["status"] = "retired"
            agent["retired_at"] = datetime.utcnow().isoformat()
            agent["retire_reason"] = reason or "completed"
            
            self.agents["retired"].append({
                "id": agent_id,
                "name": agent["name"],
                "at": datetime.utcnow().isoformat(),
                "reason": reason
            })
            self._save_agents()
            return {"status": "retired", "agent_id": agent_id}
        return {"status": "not_found"}
    
    def get_agent(self, agent_id):
        """Get agent details."""
        return self.agents["agents"].get(agent_id)
    
    def list_agents(self, status=None):
        """List all agents, optionally filtered by status."""
        agents = list(self.agents["agents"].values())
        if status:
            agents = [a for a in agents if a.get("status") == status]
        return agents
    
    def get_statistics(self):
        """Get lifecycle statistics."""
        all_agents = self.agents["agents"].values()
        stats = {
            "total": len(all_agents),
            "by_status": {},
            "by_role": {},
            "total_spawned": len(self.agents["spawned"]),
            "total_retired": len(self.agents["retired"]),
            "total_tasks_completed": sum(a.get("tasks_completed", 0) for a in all_agents)
        }
        
        for agent in all_agents:
            status = agent.get("status", "unknown")
            role = agent.get("role", "unknown")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            stats["by_role"][role] = stats["by_role"].get(role, 0) + 1
        
        return stats


def main():
    import sys
    manager = AgentLifecycleManager()
    
    if len(sys.argv) < 2:
        print("Agent Lifecycle Manager")
        print("Usage: agent-lifecycle.py <command> [args]")
        print("Commands:")
        print("  spawn <name> <role> <capabilities...>")
        print("  list [status]")
        print("  status <agent_id>")
        print("  update <agent_id> <status>")
        print("  complete <agent_id>")
        print("  retire <agent_id> [reason]")
        print("  stats")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "spawn":
        if len(sys.argv) < 4:
            print("Usage: spawn <name> <role> <capabilities...>")
            return
        name, role = sys.argv[2], sys.argv[3]
        capabilities = sys.argv[4:]
        result = manager.spawn_agent(name, role, capabilities)
        print(json.dumps(result, indent=2))
    
    elif cmd == "list":
        status = sys.argv[2] if len(sys.argv) > 2 else None
        agents = manager.list_agents(status)
        print(json.dumps(agents, indent=2))
    
    elif cmd == "status":
        if len(sys.argv) < 3:
            print("Usage: status <agent_id>")
            return
        agent = manager.get_agent(sys.argv[2])
        print(json.dumps(agent or {"status": "not_found"}, indent=2))
    
    elif cmd == "update":
        if len(sys.argv) < 4:
            print("Usage: update <agent_id> <status>")
            return
        result = manager.update_status(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))
    
    elif cmd == "complete":
        if len(sys.argv) < 3:
            print("Usage: complete <agent_id>")
            return
        result = manager.complete_task(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "retire":
        reason = sys.argv[3] if len(sys.argv) > 3 else None
        result = manager.retire_agent(sys.argv[2], reason)
        print(json.dumps(result, indent=2))
    
    elif cmd == "stats":
        stats = manager.get_statistics()
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()