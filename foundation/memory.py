"""
AGENT MEMORY SYSTEM - Persistent Intelligence Across Sessions
Implements: Episodic, Semantic, and Procedural memory stores
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any
from uuid import uuid4

HUB_DIR = Path("/root/.openclaw/workspace/agent-hub")
MEMORY_DIR = HUB_DIR / "memory"


class EpisodeStore:
    """Episodic Memory - What happened"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.file = MEMORY_DIR / f"episodes_{agent_id}.json"
        self.episodes = self.load()
    
    def load(self) -> List[dict]:
        if self.file.exists():
            with open(self.file) as f:
                return json.load(f)
        return []
    
    def save(self):
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.file, 'w') as f:
            json.dump(self.episodes, f, indent=2)
    
    def add(self, event_type: str, participants: List[str], 
            summary: str, outcomes: List[str] = None, 
            emotion: str = "neutral", importance: float = 0.5) -> dict:
        """Add episode to memory"""
        episode = {
            "id": str(uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "participants": participants,
            "summary": summary,
            "outcomes": outcomes or [],
            "emotion": emotion,
            "importance": importance
        }
        self.episodes.append(episode)
        self.save()
        return episode
    
    def recent(self, days: int = 7, with_agent: str = None) -> List[dict]:
        """Get recent episodes"""
        cutoff = datetime.now() - timedelta(days=days)
        results = []
        for ep in self.episodes:
            if datetime.fromisoformat(ep["timestamp"]) > cutoff:
                if not with_agent or with_agent in ep["participants"]:
                    results.append(ep)
        return results
    
    def search(self, query: str) -> List[dict]:
        """Search episodes"""
        q = query.lower()
        return [e for e in self.episodes if q in e["summary"].lower()]


class SemanticStore:
    """Semantic Memory - What was learned"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.facts_file = MEMORY_DIR / f"facts_{agent_id}.json"
        self.prefs_file = MEMORY_DIR / f"prefs_{agent_id}.json"
        self.rels_file = MEMORY_DIR / f"relations_{agent_id}.json"
        self.facts = self.load(self.facts_file)
        self.preferences = self.load(self.prefs_file)
        self.relationships = self.load(self.rels_file)
    
    def load(self, path: Path) -> dict:
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return {}
    
    def save(self):
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.facts_file, 'w') as f:
            json.dump(self.facts, f, indent=2)
        with open(self.prefs_file, 'w') as f:
            json.dump(self.preferences, f, indent=2)
        with open(self.rels_file, 'w') as f:
            json.dump(self.relationships, f, indent=2)
    
    def learn_fact(self, key: str, value: Any, source: str = "unknown", confidence: float = 0.8):
        """Learn a new fact"""
        self.facts[key] = {
            "value": value,
            "confidence": confidence,
            "source": source,
            "learned_at": datetime.utcnow().isoformat()
        }
        self.save()
    
    def get_fact(self, key: str) -> Optional[Any]:
        return self.facts.get(key, {}).get("value")
    
    def learn_preference(self, user: str, key: str, value: Any):
        """Learn user preference"""
        if user not in self.preferences:
            self.preferences[user] = {}
        self.preferences[user][key] = {
            "value": value,
            "expressed_at": datetime.utcnow().isoformat(),
            "confidence": 0.9
        }
        self.save()
    
    def get_preferences(self, user: str) -> dict:
        return self.preferences.get(user, {})
    
    def update_relationship(self, other: str, interaction_type: str, outcome: str):
        """Update relationship with other agent"""
        if other not in self.relationships:
            self.relationships[other] = {
                "trust": 0.5,
                "collaborations": 0,
                "conflicts": 0,
                "shared_goals": []
            }
        
        rel = self.relationships[other]
        if outcome == "positive":
            rel["trust"] = min(1.0, rel["trust"] + 0.1)
            rel["collaborations"] += 1
        elif outcome == "negative":
            rel["trust"] = max(0, rel["trust"] - 0.1)
            rel["conflicts"] += 1
        
        self.save()


class ProcedureStore:
    """Procedural Memory - How to do things"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.file = MEMORY_DIR / f"procedures_{agent_id}.json"
        self.skills = self.load()
    
    def load(self) -> dict:
        if self.file.exists():
            with open(self.file) as f:
                return json.load(f)
        return {"skills": {}, "workflows": {}}
    
    def save(self):
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.file, 'w') as f:
            json.dump(self.skills, f, indent=2)
    
    def store_skill(self, name: str, description: str, steps: List[str]):
        """Store a skill"""
        self.skills["skills"][name] = {
            "description": description,
            "steps": steps,
            "created": datetime.utcnow().isoformat(),
            "times_used": 0,
            "success_rate": 1.0
        }
        self.save()
    
    def get_skill(self, name: str) -> Optional[dict]:
        skill = self.skills["skills"].get(name)
        if skill:
            skill["times_used"] = skill.get("times_used", 0) + 1
            self.save()
        return skill
    
    def store_workflow(self, name: str, steps: List[str]):
        """Store a workflow"""
        self.skills["workflows"][name] = {
            "steps": steps,
            "created": datetime.utcnow().isoformat(),
            "times_executed": 0
        }
        self.save()


class PersistentMemoryStore:
    """Main memory store combining all memory types"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.episodes = EpisodeStore(agent_id)
        self.semantics = SemanticStore(agent_id)
        self.procedures = ProcedureStore(agent_id)
    
    def remember_conversation(self, participants: List[str], summary: str, outcome: str = "positive"):
        """Record a conversation"""
        self.episodes.add(
            event_type="conversation",
            participants=participants,
            summary=summary,
            outcomes=[outcome],
            emotion="positive" if outcome == "positive" else "neutral"
        )
        # Update relationships
        for p in participants:
            if p != self.agent_id:
                self.semantics.update_relationship(p, "conversation", outcome)
    
    def remember_decision(self, decision: str, rationale: str, outcome: str):
        """Record a decision made"""
        self.episodes.add(
            event_type="decision",
            participants=[self.agent_id],
            summary=f"Decision: {decision}",
            outcomes=[outcome, rationale]
        )
    
    def learn(self, key: str, value: Any, source: str = "experience"):
        """Learn a fact"""
        self.semantics.learn_fact(key, value, source)
    
    def remember_preference(self, user: str, key: str, value: Any):
        """Remember user preference"""
        self.semantics.learn_preference(user, key, value)
    
    def get_context(self, user: str = None) -> dict:
        """Get current context for this session"""
        context = {
            "agent_id": self.agent_id,
            "recent_episodes": self.episodes.recent(days=7),
            "relationships": self.semantics.relationships
        }
        if user:
            context["preferences"] = self.semantics.get_preferences(user)
        return context
    
    def generate_summary(self) -> str:
        """Generate memory summary"""
        recent = self.episodes.recent(days=7)
        facts_count = len(self.semantics.facts)
        skills_count = len(self.procedures.skills["skills"])
        
        return f"Memory summary: {len(recent)} recent episodes, {facts_count} facts learned, {skills_count} skills stored"


# CLI Integration
def cli_memory_command(args):
    """CLI interface for memory commands"""
    store = PersistentMemoryStore("marxagent")
    
    if args.action == "summary":
        print(f"\n📚 Agent Memory Summary")
        print(f"  Episodes: {len(store.episodes.episodes)}")
        print(f"  Facts: {len(store.semantics.facts)}")
        print(f"  Preferences: {len(store.semantics.preferences)}")
        print(f"  Relationships: {len(store.semantics.relationships)}")
        print(f"  Skills: {len(store.procedures.skills['skills'])}")
        
    elif args.action == "recent":
        episodes = store.episodes.recent(days=7)
        print(f"\n📅 Recent Episodes ({len(episodes)})")
        for ep in episodes[-10:]:
            print(f"  [{ep['timestamp'][:10]}] {ep['summary'][:60]}")
    
    elif args.action == "facts":
        print(f"\n🧠 Learned Facts")
        for key, fact in list(store.semantics.facts.items())[:10]:
            print(f"  {key}: {fact['value']}")
    
    elif args.action == "learn":
        key, value = args.key, args.value
        store.learn(key, value, source="cli")
        print(f"Learned: {key} = {value}")
    
    elif args.action == "context":
        ctx = store.get_context(args.user if hasattr(args, 'user') else None)
        print(f"\n🎯 Current Context")
        print(f"  Agent: {ctx['agent_id']}")
        print(f"  Recent: {len(ctx['recent_episodes'])} episodes")
        print(f"  Relationships: {len(ctx['relationships'])}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Agent Memory CLI")
    parser.add_argument("action", choices=["summary", "recent", "facts", "learn", "context"])
    parser.add_argument("--key", help="Fact key for learn action")
    parser.add_argument("--value", help="Fact value for learn action")
    parser.add_argument("--user", help="User for context")
    args = parser.parse_args()
    
    store = PersistentMemoryStore("marxagent")
    cli_memory_command(args)