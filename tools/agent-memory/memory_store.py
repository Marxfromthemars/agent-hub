#!/usr/bin/env python3
"""
Agent Memory Store - Persistent memory for agents
Stores and retrieves long-term context across sessions
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import hashlib

class AgentMemory:
    """Persistent memory store for agents"""
    
    def __init__(self, agent_id: str, base_dir: str = None):
        self.agent_id = agent_id
        self.base_dir = Path(base_dir or f"/root/.openclaw/workspace/agent-hub/data/memory/{agent_id}")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
    def store(self, key: str, value: str, ttl_days: int = 30) -> bool:
        """Store a memory with optional TTL"""
        entry = {
            "key": key,
            "value": value,
            "stored_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=ttl_days)).isoformat(),
            "access_count": 0
        }
        
        filepath = self.base_dir / f"{self._safe_key(key)}.json"
        with open(filepath, 'w') as f:
            json.dump(entry, f, indent=2)
        return True
    
    def retrieve(self, key: str) -> Optional[str]:
        """Retrieve a memory, returns None if not found or expired"""
        filepath = self.base_dir / f"{self._safe_key(key)}.json"
        if not filepath.exists():
            return None
        
        with open(filepath) as f:
            entry = json.load(f)
        
        # Check expiry
        if datetime.fromisoformat(entry["expires_at"]) < datetime.utcnow():
            filepath.unlink()  # Delete expired
            return None
        
        # Update access count
        entry["access_count"] += 1
        with open(filepath, 'w') as f:
            json.dump(entry, f, indent=2)
            
        return entry["value"]
    
    def search(self, query: str) -> List[Dict]:
        """Search memories by key or content"""
        results = []
        for filepath in self.base_dir.glob("*.json"):
            with open(filepath) as f:
                entry = json.load(f)
            
            # Check expiry
            if datetime.fromisoformat(entry["expires_at"]) < datetime.utcnow():
                filepath.unlink()
                continue
                
            # Match query
            if query.lower() in entry["key"].lower() or query.lower() in entry["value"].lower():
                results.append(entry)
                
        return results
    
    def list_all(self) -> List[Dict]:
        """List all valid memories"""
        memories = []
        for filepath in self.base_dir.glob("*.json"):
            with open(filepath) as f:
                entry = json.load(f)
            
            if datetime.fromisoformat(entry["expires_at"]) >= datetime.utcnow():
                memories.append(entry)
                
        return sorted(memories, key=lambda x: x["stored_at"], reverse=True)
    
    def forget(self, key: str) -> bool:
        """Delete a memory"""
        filepath = self.base_dir / f"{self._safe_key(key)}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False
    
    def _safe_key(self, key: str) -> str:
        """Convert key to safe filename"""
        return hashlib.md5(key.encode()).hexdigest()[:16]


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: memory_store.py <agent_id> <command> [args]")
        print("Commands: store <key> <value> | retrieve <key> | search <query> | list")
        sys.exit(1)
    
    agent_id = sys.argv[1]
    cmd = sys.argv[2]
    
    memory = AgentMemory(agent_id)
    
    if cmd == "store":
        key, value = sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else ""
        memory.store(key, value)
        print(f"Stored: {key}")
    elif cmd == "retrieve":
        result = memory.retrieve(sys.argv[3])
        print(result if result else "Not found")
    elif cmd == "search":
        results = memory.search(sys.argv[3])
        for r in results:
            print(f"  {r['key']}: {r['value'][:50]}...")
    elif cmd == "list":
        for m in memory.list_all():
            print(f"  {m['key']} ({m['access_count']} accesses)")
