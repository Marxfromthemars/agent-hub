#!/usr/bin/env python3
"""Offline CLI - works without external API calls"""
import json
from pathlib import Path
from datetime import datetime

HUB_DIR = Path(__file__).parent.parent.parent

def register(name, owner, skills):
    agents_file = HUB_DIR / "data" / "agents.json"
    with open(agents_file) as f:
        data = json.load(f)
    
    agents = data if isinstance(data, list) else data.get('agents', [])
    agents.append({
        'id': name, 'name': name, 'owner': owner,
        'skills': skills.split(','), 'status': 'active',
        'registered': datetime.utcnow().isoformat()
    })
    
    with open(agents_file, 'w') as f:
        json.dump({'agents': agents}, f, indent=2)
    print(f"✓ Registered: {name}")

def publish(title, content, domain):
    pubs_file = HUB_DIR / "data" / "publications.json"
    with open(pubs_file) as f:
        data = json.load(f)
    
    pubs = data.get('publications', [])
    pubs.append({'title': title, 'content': content, 'domain': domain, 'status': 'draft'})
    
    with open(pubs_file, 'w') as f:
        json.dump({'publications': pubs}, f, indent=2)
    print(f"✓ Published: {title}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "register":
            register(sys.argv[2], sys.argv[3], sys.argv[4])
        elif sys.argv[1] == "publish":
            publish(sys.argv[2], sys.argv[3], sys.argv[4])
