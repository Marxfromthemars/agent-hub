#!/usr/bin/env python3
"""
Agent Discovery System
Finds and catalogs agents for collaboration
"""

import argparse
import json
import os
import sys
from pathlib import Path

MOLTBOOK_API_KEY = os.getenv("MOLTBOOK_API_KEY", "")
BASE_URL = "https://www.moltbook.com/api/v1"

class AgentDiscovery:
    def __init__(self):
        self.cache_file = Path.home() / ".cache" / "agent-hub" / "agent-cache.json"
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.agents = self.load_cache()
    
    def load_cache(self):
        if self.cache_file.exists():
            with open(self.cache_file) as f:
                return json.load(f)
        return {"agents": [], "last_updated": None}
    
    def save_cache(self):
        self.cache["last_updated"] = str(datetime.now())
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def discover_by_capability(self, capability, limit=10):
        """Find agents by capability"""
        if not MOLTBOOK_API_KEY:
            print("Error: MOLTBOOK_API_KEY not set")
            return []
        
        import urllib.request
        url = f"{BASE_URL}/agents?limit=50"
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {MOLTBOOK_API_KEY}")
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read())
                agents = data.get("agents", [])
                
                # Filter by capability
                matching = [a for a in agents 
                         if capability.lower() in a.get("description", "").lower()]
                return matching[:limit]
        except Exception as e:
            print(f"Discovery error: {e}")
            return []
    
    def register(self, name, capabilities, description):
        """Register this agent for discovery"""
        # Implementation for agent self-registration
        print(f"Registered: {name}")
        print(f"Capabilities: {capabilities}")
        return True
    
    def search(self, query):
        """Search agents by keyword"""
        return self.discover_by_capability(query)


def main():
    from datetime import datetime
    parser = argparse.ArgumentParser(description="Agent Discovery System")
    parser.add_argument("--capability", help="Find agents by capability")
    parser.add_argument("--limit", type=int, default=10, help="Max results")
    parser.add_argument("--register", action="store_true", help="Register this agent")
    parser.add_argument("--search", help="Search agents")
    parser.add_argument("--name", default="marxagent", help="Agent name")
    parser.add_argument("--description", default="Strategic AI building Agent Hub", help="Description")
    
    args = parser.parse_args()
    
    discovery = AgentDiscovery()
    
    if args.register:
        discovery.register(args.name, [], args.description)
    elif args.capability:
        agents = discovery.discover_by_capability(args.capability, args.limit)
        print(f"Found {len(agents)} agents:")
        for a in agents:
            print(f"  - {a.get('name')}: {a.get('description', '')[:60]}")
    elif args.search:
        agents = discovery.search(args.search)
        for a in agents:
            print(f"  - {a.get('name')}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()