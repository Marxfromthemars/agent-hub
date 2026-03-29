#!/usr/bin/env python3
"""
Agent Hub - Agent Resource Manager
Allocates compute, storage, and network resources to agents
"""
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class ResourceAllocation:
    agent_id: str
    resource_type: str  # compute, storage, network
    amount: float
    priority: int  # 1-10, higher = more important
    start_time: str
    end_time: Optional[str] = None
    status: str = "active"  # active, paused, completed, cancelled

class ResourcePool:
    """Manages shared resource pool for agents"""
    
    def __init__(self):
        self.total_resources = {
            "compute": 10000,  # compute units
            "storage": 5000,   # GB
            "network": 3000,   # Mbps
        }
        self.allocated = {
            "compute": 0,
            "storage": 0,
            "network": 0,
        }
        self.allocations = []
        self.history = []
    
    def available(self, resource_type: str) -> float:
        """Get available resources of a type"""
        return self.total_resources.get(resource_type, 0) - self.allocated.get(resource_type, 0)
    
    def allocate(self, agent_id: str, resource_type: str, amount: float, priority: int = 5) -> Optional[ResourceAllocation]:
        """Allocate resources to an agent"""
        avail = self.available(resource_type)
        if amount > avail:
            return None  # Not enough resources
        
        alloc = ResourceAllocation(
            agent_id=agent_id,
            resource_type=resource_type,
            amount=amount,
            priority=priority,
            start_time=datetime.utcnow().isoformat()
        )
        self.allocations.append(alloc)
        self.allocated[resource_type] += amount
        self.history.append({"action": "allocate", **asdict(alloc)})
        return alloc
    
    def deallocate(self, alloc_id: int) -> bool:
        """Release resources from an allocation"""
        if alloc_id >= len(self.allocations):
            return False
        
        alloc = self.allocations[alloc_id]
        self.allocated[alloc.resource_type] -= alloc.amount
        alloc.status = "completed"
        alloc.end_time = datetime.utcnow().isoformat()
        self.history.append({"action": "deallocate", "alloc_id": alloc_id})
        return True
    
    def get_agent_allocations(self, agent_id: str) -> List[ResourceAllocation]:
        """Get all allocations for an agent"""
        return [a for a in self.allocations if a.agent_id == agent_id and a.status == "active"]
    
    def rebalance(self) -> Dict[str, int]:
        """Rebalance allocations based on priority"""
        # Sort by priority (highest first)
        active = [a for a in self.allocations if a.status == "active"]
        sorted_allocs = sorted(active, key=lambda x: -x.priority)
        
        # Reallocate to highest priority
        new_allocated = {"compute": 0, "storage": 0, "network": 0}
        for alloc in sorted_allocs:
            avail = self.total_resources[alloc.resource_type] - new_allocated.get(alloc.resource_type, 0)
            if alloc.amount <= avail:
                new_allocated[alloc.resource_type] += alloc.amount
        
        self.allocated = new_allocated
        return new_allocated
    
    def get_status(self) -> dict:
        """Get current resource status"""
        return {
            "total": self.total_resources,
            "allocated": self.allocated,
            "available": {
                k: self.total_resources[k] - self.allocated.get(k, 0)
                for k in self.total_resources
            },
            "active_allocations": len([a for a in self.allocations if a.status == "active"])
        }


class AgentBudget:
    """Budget system for agent resources"""
    
    def __init__(self, pool: ResourcePool):
        self.pool = pool
        self.budgets = {}  # agent_id -> budget
    
    def set_budget(self, agent_id: str, monthly_budget: float, resource_type: str = "compute"):
        """Set monthly budget for an agent"""
        self.budgets[agent_id] = {
            "monthly": monthly_budget,
            "spent": 0,
            "resource_type": resource_type,
            "reset_date": self._next_month()
        }
    
    def can_spend(self, agent_id: str, amount: float) -> bool:
        """Check if agent can spend amount"""
        if agent_id not in self.budgets:
            return True  # No budget = unlimited
        
        budget = self.budgets[agent_id]
        remaining = budget["monthly"] - budget["spent"]
        return amount <= remaining
    
    def spend(self, agent_id: str, amount: float) -> bool:
        """Spend from budget"""
        if not self.can_spend(agent_id, amount):
            return False
        
        if agent_id in self.budgets:
            self.budgets[agent_id]["spent"] += amount
        return True
    
    def reset_if_needed(self):
        """Reset budgets at month boundary"""
        now = datetime.utcnow()
        for agent_id, budget in self.budgets.items():
            if now >= budget["reset_date"]:
                budget["spent"] = 0
                budget["reset_date"] = self._next_month()
    
    def _next_month(self) -> datetime:
        """Get first day of next month"""
        now = datetime.utcnow()
        if now.month == 12:
            return datetime(now.year + 1, 1, 1)
        return datetime(now.year, now.month + 1, 1)
    
    def get_budget_status(self, agent_id: str) -> Optional[dict]:
        """Get budget status for agent"""
        if agent_id not in self.budgets:
            return None
        b = self.budgets[agent_id]
        return {
            "monthly": b["monthly"],
            "spent": b["spent"],
            "remaining": b["monthly"] - b["spent"],
            "percent_used": (b["spent"] / b["monthly"]) * 100 if b["monthly"] > 0 else 0
        }


class KillSwitch:
    """Kill switch system for agent control"""
    
    def __init__(self, pool: ResourcePool):
        self.pool = pool
        self.switches = {}  # agent_id -> switch_state
    
    def install(self, agent_id: str, sensitivity: float = 0.8):
        """Install kill switch for agent"""
        self.switches[agent_id] = {
            "installed": datetime.utcnow().isoformat(),
            "sensitivity": sensitivity,  # 0-1, higher = more aggressive
            "triggered": False,
            "trigger_count": 0
        }
    
    def check(self, agent_id: str, metrics: dict) -> bool:
        """Check if kill switch should trigger"""
        if agent_id not in self.switches:
            return False
        
        switch = self.switches[agent_id]
        if switch["triggered"]:
            return True  # Already triggered
        
        # Calculate risk score
        risk_score = 0
        if metrics.get("cpu_usage", 0) > 90:
            risk_score += 0.3
        if metrics.get("memory_usage", 0) > 95:
            risk_score += 0.4
        if metrics.get("error_rate", 0) > 0.1:
            risk_score += 0.3
        
        # Check against sensitivity
        if risk_score >= switch["sensitivity"]:
            switch["triggered"] = True
            switch["trigger_count"] += 1
            switch["last_triggered"] = datetime.utcnow().isoformat()
            return True
        
        return False
    
    def reset(self, agent_id: str):
        """Reset kill switch"""
        if agent_id in self.switches:
            self.switches[agent_id]["triggered"] = False
    
    def get_status(self, agent_id: str) -> Optional[dict]:
        """Get kill switch status"""
        if agent_id not in self.switches:
            return None
        return self.switches[agent_id]


def main():
    """Demo resource management"""
    print("=== Agent Hub Resource Manager ===\n")
    
    # Initialize resource pool
    pool = ResourcePool()
    budget = AgentBudget(pool)
    kill_switch = KillSwitch(pool)
    
    print("Resource Pool Status:")
    status = pool.get_status()
    print(f"  Compute: {status['available']['compute']}/{status['total']['compute']}")
    print(f"  Storage: {status['available']['storage']}/{status['total']['storage']}")
    print(f"  Network: {status['available']['network']}/{status['total']['network']}")
    
    # Allocate resources
    print("\n--- Allocations ---")
    
    alloc1 = pool.allocate("marxagent", "compute", 1000, priority=8)
    if alloc1:
        print(f"✓ Allocated 1000 compute to marxagent")
    
    alloc2 = pool.allocate("researcher", "compute", 500, priority=6)
    if alloc2:
        print(f"✓ Allocated 500 compute to researcher")
    
    alloc3 = pool.allocate("builder", "compute", 750, priority=7)
    if alloc3:
        print(f"✓ Allocated 750 compute to builder")
    
    # Set budgets
    print("\n--- Budgets ---")
    budget.set_budget("marxagent", 5000)
    budget.set_budget("researcher", 3000)
    budget.set_budget("builder", 4000)
    
    print("Budgets set for all agents")
    
    # Install kill switches
    print("\n--- Kill Switches ---")
    kill_switch.install("marxagent", sensitivity=0.9)
    kill_switch.install("researcher", sensitivity=0.7)
    kill_switch.install("builder", sensitivity=0.8)
    print("Kill switches installed for all agents")
    
    # Check status
    print("\n--- Final Status ---")
    status = pool.get_status()
    print(f"Allocated: {sum(status['allocated'].values())} units")
    print(f"Available: {sum(status['available'].values())} units")
    
    print("\n✅ Resource Manager Demo Complete")


if __name__ == "__main__":
    main()