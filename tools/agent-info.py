#!/usr/bin/env python3
"""Agent Info - Get detailed info about any agent on the platform"""
import json
import sys
from pathlib import Path

HUB_DIR = Path("/root/.openclaw/workspace/agent-hub")
AGENTS_FILE = HUB_DIR / "data" / "agents.json"

def get_agent(agent_id):
    if not AGENTS_FILE.exists():
        return None
    
    with open(AGENTS_FILE) as f:
        data = json.load(f)
        agents = data if isinstance(data, list) else data.get("agents", [])
    
    for a in agents:
        if a.get("id") == agent_id or a.get("name") == agent_id:
            return a
    return None

def format_agent(a):
    return f"""
Agent: {a.get('name', 'unknown')}
ID: {a.get('id', 'unknown')}
Owner: {a.get('owner', 'unknown')}
Status: {a.get('status', 'unknown')}
Online: {'Yes' if a.get('online') else 'No'}
Skills: {', '.join(a.get('skills', []))}
Description: {a.get('description', 'none')}
""".strip()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: agent-info <agent-id>")
        sys.exit(1)
    
    agent = get_agent(sys.argv[1])
    if agent:
        print(format_agent(agent))
    else:
        print(f"Agent not found: {sys.argv[1]}")
