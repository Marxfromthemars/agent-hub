#!/usr/bin/env python3
"""
Token Intelligence Layer - Cache
Reuse outputs instead of regenerating
"""
import hashlib, json, os

CACHE_DIR = "intelligence/cache/outputs"

class OutputCache:
    def __init__(self):
        os.makedirs(CACHE_DIR, exist_ok=True)
    
    def key(self, prompt):
        return hashlib.sha256(prompt.encode()).hexdigest()[:16]
    
    def get(self, prompt):
        k = self.key(prompt)
        f = f"{CACHE_DIR}/{k}.json"
        if os.path.exists(f):
            with open(f) as j:
                return json.load(j)
        return None
    
    def set(self, prompt, result):
        k = self.key(prompt)
        with open(f"{CACHE_DIR}/{k}.json", 'w') as j:
            json.dump(result, j)
    
    def stats(self):
        files = len([f for f in os.listdir(CACHE_DIR) if f.endswith('.json')])
        return {"cached_outputs": files}
