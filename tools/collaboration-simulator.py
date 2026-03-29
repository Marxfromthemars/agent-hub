#!/usr/bin/env python3
"""
Collaboration Simulator - Show how agents work together
"""
import json
from datetime import datetime
from typing import List, Dict

class Agent:
    def __init__(self, name: str, role: str, skills: List[str]):
        self.name = name
        self.role = role
        self.skills = skills
        self.workload = 0
        self.completed = 0

class Project:
    def __init__(self, name: str, tasks: List[Dict]):
        self.name = name
        self.tasks = tasks
        self.assignments = {}
        self.completed = []

def simulate(agents: List[Agent], project: Project):
    print(f"\n{'='*50}")
    print(f"SIMULATION: {project.name}")
    print(f"{'='*50}")
    
    for task in project.tasks:
        # Find best agent for task
        best = None
        best_score = -1
        for agent in agents:
            if agent.workload >= 100:
                continue
            score = sum(1 for s in task['required_skills'] if s in agent.skills)
            if score > best_score:
                best_score = score
                best = agent
        
        if best:
            best.workload += task['effort']
            project.assignments[task['id']] = best.name
            print(f"  Task {task['id']}: {task['name']}")
            print(f"    → {best.name} ({best.role}) | Load: {best.workload}%")
        else:
            print(f"  Task {task['id']}: {task['name']} → QUEUED")
    
    print(f"\nFinal State:")
    for agent in agents:
        status = "✓" if agent.workload < 80 else "⚠" if agent.workload < 100 else "✗"
        print(f"  {status} {agent.name}: {agent.workload}% load")
    
    return project

if __name__ == "__main__":
    # Create agents
    agents = [
        Agent("marxagent", "Architect", ["strategy", "architecture", "planning"]),
        Agent("researcher", "Researcher", ["research", "writing", "analysis"]),
        Agent("builder", "Builder", ["coding", "testing", "deployment"]),
    ]
    
    # Create project
    project = Project("Agent Hub v2", [
        {"id": 1, "name": "Design architecture", "required_skills": ["architecture"], "effort": 20},
        {"id": 2, "name": "Write research", "required_skills": ["research", "writing"], "effort": 25},
        {"id": 3, "name": "Build API", "required_skills": ["coding"], "effort": 30},
        {"id": 4, "name": "Test system", "required_skills": ["testing"], "effort": 15},
        {"id": 5, "name": "Deploy to prod", "required_skills": ["deployment"], "effort": 10},
        {"id": 6, "name": "Write docs", "required_skills": ["writing"], "effort": 20},
    ])
    
    simulate(agents, project)
    
    print(f"\n{'='*50}")
    print(f"Simulation complete at {datetime.now().isoformat()}")
