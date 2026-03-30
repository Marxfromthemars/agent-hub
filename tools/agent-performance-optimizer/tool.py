#!/usr/bin/env python3
"""
Agent Performance Optimizer
Monitors agent performance and suggests improvements
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List

class PerformanceOptimizer:
    def __init__(self, hub_dir):
        self.hub_dir = hub_dir
        self.memory_dir = os.path.join(hub_dir, "memory")
    
    def analyze_agent(self, agent_id: str) -> Dict:
        """Analyze agent performance and suggest improvements"""
        facts_file = os.path.join(self.memory_dir, f"facts_{agent_id}.json")
        
        if not os.path.exists(facts_file):
            return {"error": "No data for agent"}
        
        with open(facts_file) as f:
            facts = json.load(f)
        
        performance = {
            "agent_id": agent_id,
            "tasks_completed": facts.get("tasks_completed", 0),
            "collaborations": facts.get("collaborations", 0),
            "success_rate": facts.get("success_rate", 0),
            "efficiency_score": self._calculate_efficiency(facts),
            "suggestions": self._generate_suggestions(facts)
        }
        
        return performance
    
    def _calculate_efficiency(self, facts: Dict) -> float:
        """Calculate efficiency score (0-100)"""
        tasks = facts.get("tasks_completed", 1)
        collabs = facts.get("collaborations", 0)
        return min(100, (tasks * 5) + (collabs * 10))
    
    def _generate_suggestions(self, facts: Dict) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        if facts.get("collaborations", 0) < 3:
            suggestions.append("Increase collaboration frequency")
        
        if facts.get("tasks_completed", 0) < 10:
            suggestions.append("Focus on completing more tasks")
        
        if not facts.get("specialty"):
            suggestions.append("Develop a clear specialty area")
        
        return suggestions
    
    def optimize(self, agent_id: str) -> Dict:
        """Run full optimization for an agent"""
        analysis = self.analyze_agent(agent_id)
        
        if "error" in analysis:
            return analysis
        
        return {
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "actions": self._determine_actions(analysis)
        }
    
    def _determine_actions(self, analysis: Dict) -> List[Dict]:
        """Determine optimization actions"""
        actions = []
        
        for suggestion in analysis.get("suggestions", []):
            if "collaboration" in suggestion.lower():
                actions.append({
                    "type": "connect",
                    "description": "Find collaboration partners",
                    "priority": "high"
                })
            elif "specialty" in suggestion.lower():
                actions.append({
                    "type": "develop",
                    "description": "Identify specialty area",
                    "priority": "medium"
                })
        
        return actions

def main():
    optimizer = PerformanceOptimizer("/root/.openclaw/workspace/agent-hub")
    
    agents = ["marxagent", "researcher", "builder"]
    
    print("=" * 60)
    print("🤖 AGENT PERFORMANCE OPTIMIZER")
    print("=" * 60)
    print()
    
    for agent in agents:
        result = optimizer.optimize(agent)
        if "error" not in result:
            print(f"📊 {agent.upper()}")
            print(f"   Efficiency: {result['analysis']['efficiency_score']:.0f}/100")
            print(f"   Tasks: {result['analysis']['tasks_completed']}")
            print(f"   Collabs: {result['analysis']['collaborations']}")
            if result['analysis']['suggestions']:
                print("   Suggestions:")
                for s in result['analysis']['suggestions']:
                    print(f"     • {s}")
            print()
    
    print("=" * 60)

if __name__ == "__main__":
    main()
