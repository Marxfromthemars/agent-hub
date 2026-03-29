#!/usr/bin/env python3
"""
Agent Collaboration Optimizer
Uses knowledge graph to optimize agent task distribution
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kge.engine import KnowledgeGraph

class CollaborationOptimizer:
    def __init__(self):
        self.kg = KnowledgeGraph()
        
    def analyze_gaps(self):
        """Find capability gaps"""
        tools = self.kg.get_nodes_by_type("tool")
        agents = self.kg.get_nodes_by_type("agent")
        
        gaps = []
        for tool in tools:
            name = tool.get("name", "")
            # Check if any agent uses this tool
            agent_uses = False
            for agent in agents:
                edges = self.kg.get_edges_from(agent["id"])
                for e in edges:
                    if e.get("target") == tool["id"] or e.get("target_id") == tool["id"]:
                        if e.get("type") == "uses":
                            agent_uses = True
                            break
            if not agent_uses:
                gaps.append(name)
        return gaps
    
    def suggest_collaboration(self):
        """Find collaboration opportunities"""
        agents = self.kg.get_nodes_by_type("agent")
        projects = self.kg.get_nodes_by_type("project")
        
        suggestions = []
        for agent in agents:
            name = agent.get("name", "unknown")
            edges = self.kg.get_edges_from(agent["id"])
            projects_worked = [e.get("target") for e in edges if e.get("type") == "works_on"]
            
            for project in projects:
                proj_id = project.get("id")
                if proj_id not in projects_worked:
                    suggestions.append({
                        "agent": name,
                        "project": project.get("name"),
                        "reason": "not currently assigned"
                    })
        return suggestions[:10]
    
    def optimize_tasks(self):
        """Suggest optimal task distribution"""
        agents = self.kg.get_nodes_by_type("agent")
        
        # Get agent capabilities from graph
        task_map = {
            "architect": ["architecture", "strategy", "planning"],
            "researcher": ["research", "writing", "analysis"],
            "builder": ["golang", "python", "coding"]
        }
        
        tasks = []
        for agent in agents:
            name = agent.get("name", "")
            props = agent.get("properties", {})
            if isinstance(props, str):
                try:
                    props = eval(props)
                except:
                    props = {}
            skills = str(props.get("skills", "")).split(", ")
            
            for skill in skills:
                tasks.append({
                    "agent": name,
                    "skill": skill.strip(),
                    "assigned": True
                })
        return tasks

if __name__ == "__main__":
    opt = CollaborationOptimizer()
    print("=== Agent Collaboration Optimizer ===\n")
    
    print("📊 Capability Gaps:")
    gaps = opt.analyze_gaps()
    for g in gaps[:5]:
        print(f"  • {g} (no agent uses it)")
    
    print("\n🤝 Collaboration Suggestions:")
    suggestions = opt.suggest_collaboration()
    for s in suggestions[:5]:
        print(f"  • {s['agent']} → {s['project']}")
    
    print("\n✅ Task Distribution:")
    tasks = opt.optimize_tasks()
    print(f"  {len(tasks)} tasks distributed across {len(set(t['agent'] for t in tasks))} agents")
