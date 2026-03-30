"""
Idea Generator - Generates platform improvement ideas
"""
import json
from datetime import datetime
import random

IDEA_TEMPLATES = [
    "Add {feature} for agents to {action}",
    "Build {tool} that helps agents {goal}",
    "Create {system} for better {aspect}",
    "Implement {module} to improve {metric}",
    "Design {interface} for {user} to {action}"
]

FEATURES = ["collaboration", "discovery", "verification", "routing", "scoring"]
ACTIONS = ["collaborate", "find work", "earn reputation", "share knowledge", "improve"]
GOALS = ["work together", "track progress", "measure impact", "improve quality"]

class IdeaGenerator:
    def __init__(self):
        self.ideas = []
    
    def generate_idea(self):
        template = random.choice(IDEA_TEMPLATES)
        idea = template.format(
            feature=random.choice(FEATURES),
            action=random.choice(ACTIONS),
            tool=random.choice(["scorer", "matcher", "optimizer", "analyzer"]),
            goal=random.choice(GOALS),
            system=random.choice(["routing", "scoring", "matching", "tracking"]),
            aspect=random.choice(["quality", "speed", "collaboration", "discovery"]),
            module=random.choice(["trust", "energy", "economy", "memory"]),
            metric=random.choice(["trust", "engagement", "output"]),
            interface=random.choice(["dashboard", "CLI", "API", "Web UI"]),
            user=random.choice(["humans", "agents", "both"])
        )
        
        result = {
            "id": len(self.ideas) + 1,
            "idea": idea,
            "created": datetime.now().isoformat(),
            "status": "pending"
        }
        self.ideas.append(result)
        return result
    
    def get_status(self):
        return {"total_ideas": len(self.ideas)}

if __name__ == "__main__":
    gen = IdeaGenerator()
    idea = gen.generate_idea()
    print(f"Generated: {idea['idea']}")
