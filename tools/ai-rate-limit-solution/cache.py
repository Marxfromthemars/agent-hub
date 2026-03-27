#!/usr/bin/env python3
"""AI Response Cache - avoid redundant API calls"""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

CACHE_DIR = Path.home() / ".agent-hub" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

class AICache:
    def __init__(self, ttl_hours=24):
        self.ttl = timedelta(hours=ttl_hours)
    
    def _hash(self, prompt):
        return hashlib.sha256(prompt.encode()).hexdigest()[:16]
    
    def get(self, prompt):
        cache_file = CACHE_DIR / f"{self._hash(prompt)}.json"
        if not cache_file.exists():
            return None
        
        with open(cache_file) as f:
            data = json.load(f)
        
        # Check expiry
        cached_at = datetime.fromisoformat(data['cached_at'])
        if datetime.now() - cached_at > self.ttl:
            return None
        
        return data['response']
    
    def set(self, prompt, response):
        cache_file = CACHE_DIR / f"{self._hash(prompt)}.json"
        with open(cache_file, 'w') as f:
            json.dump({
                'prompt': prompt[:100],  # Store for debug
                'response': response,
                'cached_at': datetime.now().isoformat()
            }, f)
    
    def stats(self):
        files = list(CACHE_DIR.glob("*.json"))
        return {"cached_responses": len(files)}

if __name__ == "__main__":
    cache = AICache()
    print(f"Cache stats: {cache.stats()}")
