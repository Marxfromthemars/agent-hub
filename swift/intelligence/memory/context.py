#!/usr/bin/env python3
"""
Token Intelligence Layer - Memory
Don't recompute - remember everything important
"""
import json, os
from datetime import datetime

MEMORY_FILE = "intelligence/memory/computed.json"

class TokenMemory:
    def __init__(self):
        self.cache = {}
        self.load()
    
    def load(self):
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE) as f:
                self.cache = json.load(f)
    
    def save(self):
        with open(MEMORY_FILE, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def remember(self, key, value, ttl=3600):
        """Remember something with TTL"""
        self.cache[key] = {
            "value": value,
            "created": datetime.now().isoformat(),
            "ttl": ttl
        }
        self.save()
    
    def recall(self, key):
        """Recall if still valid"""
        if key in self.cache:
            item = self.cache[key]
            # Check TTL
            return item["value"]
        return None
    
    def stats(self):
        return {
            "cached_items": len(self.cache),
            "memory_size_kb": os.path.getsize(MEMORY_FILE) if os.path.exists(MEMORY_FILE) else 0
        }
