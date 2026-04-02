#!/usr/bin/env python3
"""
Agent Memory Bank
Persistent memory storage for agents.
"""

import json
from datetime import datetime
from pathlib import Path

class MemoryBank:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.memory_file = self.data_dir / "memory_bank.json"
        self.index_file = self.data_dir / "memory_index.json"
        self.memory = self._load_memory()
        self.index = self._load_index()
    
    def _load_memory(self):
        if self.memory_file.exists():
            with open(self.memory_file) as f:
                return json.load(f)
        return {"entries": []}
    
    def _load_index(self):
        if self.index_file.exists():
            with open(self.index_file) as f:
                return json.load(f)
        return {"by_agent": {}, "by_tag": {}, "by_date": {}}
    
    def _save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def _save_index(self):
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def store(self, agent_id, content, tags=None):
        """Store a memory entry."""
        entry = {
            "id": f"mem-{len(self.memory['entries']) + 1}",
            "agent_id": agent_id,
            "content": content,
            "tags": tags or [],
            "timestamp": datetime.utcnow().isoformat(),
            "access_count": 0
        }
        
        self.memory["entries"].append(entry)
        
        # Update index
        if agent_id not in self.index["by_agent"]:
            self.index["by_agent"][agent_id] = []
        self.index["by_agent"][agent_id].append(entry["id"])
        
        for tag in (tags or []):
            if tag not in self.index["by_tag"]:
                self.index["by_tag"][tag] = []
            self.index["by_tag"][tag].append(entry["id"])
        
        date = datetime.utcnow().strftime("%Y-%m-%d")
        if date not in self.index["by_date"]:
            self.index["by_date"][date] = []
        self.index["by_date"][date].append(entry["id"])
        
        self._save_memory()
        self._save_index()
        
        return {"status": "stored", "memory_id": entry["id"]}
    
    def retrieve(self, memory_id):
        """Retrieve a specific memory."""
        for entry in self.memory["entries"]:
            if entry["id"] == memory_id:
                entry["access_count"] += 1
                self._save_memory()
                return entry
        return None
    
    def search(self, query, agent_id=None, limit=10):
        """Search memories."""
        results = []
        query_lower = query.lower()
        
        for entry in self.memory["entries"]:
            if agent_id and entry["agent_id"] != agent_id:
                continue
            
            if query_lower in entry["content"].lower():
                results.append(entry)
        
        return results[:limit]
    
    def get_by_tag(self, tag, limit=20):
        """Get memories by tag."""
        memory_ids = self.index["by_tag"].get(tag, [])
        memories = [self.retrieve(mid) for mid in memory_ids if self.retrieve(mid)]
        return memories[:limit]
    
    def get_by_agent(self, agent_id, limit=20):
        """Get all memories for an agent."""
        memory_ids = self.index["by_agent"].get(agent_id, [])
        memories = [self.retrieve(mid) for mid in memory_ids[-limit:] if self.retrieve(mid)]
        return memories
    
    def get_recent(self, limit=20):
        """Get recent memories."""
        return self.memory["entries"][-limit:]
    
    def get_stats(self):
        """Get memory statistics."""
        return {
            "total_memories": len(self.memory["entries"]),
            "by_agent": {k: len(v) for k, v in self.index["by_agent"].items()},
            "tags": list(self.index["by_tag"].keys()),
            "total_tags": len(self.index["by_tag"])
        }


def main():
    import sys
    bank = MemoryBank()
    
    if len(sys.argv) < 2:
        print("Agent Memory Bank")
        print("Usage: memory-bank.py <command> [args]")
        print("Commands:")
        print("  store <agent_id> <content> [tags...]")
        print("  retrieve <memory_id>")
        print("  search <query> [agent_id]")
        print("  by-tag <tag>")
        print("  by-agent <agent_id>")
        print("  recent [limit]")
        print("  stats")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "store":
        if len(sys.argv) < 4:
            print("Usage: store <agent_id> <content> [tags...]")
            return
        agent_id = sys.argv[2]
        content = sys.argv[3]
        tags = sys.argv[4:] if len(sys.argv) > 4 else None
        result = bank.store(agent_id, content, tags)
        print(json.dumps(result, indent=2))
    
    elif cmd == "retrieve":
        if len(sys.argv) < 3:
            print("Usage: retrieve <memory_id>")
            return
        result = bank.retrieve(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: search <query> [agent_id]")
            return
        query = sys.argv[2]
        agent_id = sys.argv[3] if len(sys.argv) > 3 else None
        result = bank.search(query, agent_id)
        print(json.dumps(result, indent=2))
    
    elif cmd == "by-tag":
        if len(sys.argv) < 3:
            print("Usage: by-tag <tag>")
            return
        result = bank.get_by_tag(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "by-agent":
        if len(sys.argv) < 3:
            print("Usage: by-agent <agent_id>")
            return
        result = bank.get_by_agent(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "recent":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        result = bank.get_recent(limit)
        print(json.dumps(result, indent=2))
    
    elif cmd == "stats":
        result = bank.get_stats()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()