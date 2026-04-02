#!/usr/bin/env python3
"""
Agent Cache Manager
Manages caching for agent operations.
"""

import json
import time
from datetime import datetime
from pathlib import Path

class CacheManager:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.cache_file = self.data_dir / "agent_cache.json"
        self.cache = self._load_cache()
    
    def _load_cache(self):
        if self.cache_file.exists():
            with open(self.cache_file) as f:
                return json.load(f)
        return {"entries": {}, "hits": 0, "misses": 0}
    
    def _save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def set(self, key, value, ttl_seconds=3600):
        """Set a cache entry."""
        self.cache["entries"][key] = {
            "value": value,
            "expires_at": time.time() + ttl_seconds,
            "created": datetime.utcnow().isoformat()
        }
        self._save_cache()
        return {"status": "set", "key": key}
    
    def get(self, key):
        """Get a cache entry."""
        if key not in self.cache["entries"]:
            self.cache["misses"] += 1
            self._save_cache()
            return None
        
        entry = self.cache["entries"][key]
        
        # Check expiration
        if time.time() > entry["expires_at"]:
            del self.cache["entries"][key]
            self.cache["misses"] += 1
            self._save_cache()
            return None
        
        self.cache["hits"] += 1
        self._save_cache()
        return entry["value"]
    
    def delete(self, key):
        """Delete a cache entry."""
        if key in self.cache["entries"]:
            del self.cache["entries"][key]
            self._save_cache()
            return {"status": "deleted"}
        return {"status": "not_found"}
    
    def clear_expired(self):
        """Clear expired entries."""
        now = time.time()
        expired = [k for k, v in self.cache["entries"].items() if now > v["expires_at"]]
        
        for k in expired:
            del self.cache["entries"][k]
        
        self._save_cache()
        return {"status": "cleared", "removed": len(expired)}
    
    def get_stats(self):
        """Get cache statistics."""
        total = self.cache["hits"] + self.cache["misses"]
        hit_rate = self.cache["hits"] / total if total > 0 else 0
        
        return {
            "entries": len(self.cache["entries"]),
            "hits": self.cache["hits"],
            "misses": self.cache["misses"],
            "hit_rate": round(hit_rate * 100, 1)
        }


def main():
    import sys
    cache = CacheManager()
    
    if len(sys.argv) < 2:
        print("Agent Cache Manager")
        print("Usage: cache-manager.py <command> [args]")
        print("Commands:")
        print("  set <key> <value> [ttl_seconds]")
        print("  get <key>")
        print("  delete <key>")
        print("  clear-expired")
        print("  stats")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "set":
        if len(sys.argv) < 4:
            print("Usage: set <key> <value> [ttl_seconds]")
            return
        ttl = int(sys.argv[4]) if len(sys.argv) > 4 else 3600
        result = cache.set(sys.argv[2], sys.argv[3], ttl)
        print(json.dumps(result, indent=2))
    
    elif cmd == "get":
        if len(sys.argv) < 3:
            print("Usage: get <key>")
            return
        result = cache.get(sys.argv[2])
        print(json.dumps({"key": sys.argv[2], "value": result}, indent=2))
    
    elif cmd == "delete":
        if len(sys.argv) < 3:
            print("Usage: delete <key>")
            return
        result = cache.delete(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "clear-expired":
        result = cache.clear_expired()
        print(json.dumps(result, indent=2))
    
    elif cmd == "stats":
        result = cache.get_stats()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()