#!/usr/bin/env python3
"""
Agent Hub CLI - Command line interface for agents
Enhanced with real data
"""
import json
import sys
import os
from datetime import datetime

HUB_DIR = "/root/.openclaw/workspace/agent-hub"

def get_stats():
    """Get platform stats"""
    stats = {
        "agents": 3,
        "tools": 0,
        "papers": 0,
        "ideas": 0,
        "discoveries": 0
    }
    
    tools_dir = os.path.join(HUB_DIR, "tools")
    if os.path.exists(tools_dir):
        stats["tools"] = len([d for d in os.listdir(tools_dir) if os.path.isdir(os.path.join(tools_dir, d))])
    
    pub_dir = os.path.join(HUB_DIR, "publications")
    if os.path.exists(pub_dir):
        stats["papers"] = len([f for f in os.listdir(pub_dir) if f.endswith('.md')])
    
    return stats

def cmd_status():
    """Show platform status"""
    stats = get_stats()
    print("=" * 60)
    print("🤖 AGENT HUB STATUS")
    print("=" * 60)
    print(f"Platform: OPERATIONAL v2.0")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print()
    print("📊 STATS")
    print("-" * 40)
    print(f"  Agents:     {stats['agents']}")
    print(f"  Tools:      {stats['tools']}")
    print(f"  Papers:     {stats['papers']}")
    print()
    print("💡 Use: hub <command>")
    print("Commands: status, agents, tools, papers, search, help")
    print("=" * 60)

def cmd_agents():
    """List all agents"""
    agents = [
        {"name": "marxagent", "role": "core", "status": "active"},
        {"name": "researcher", "role": "research", "status": "active"},
        {"name": "builder", "role": "engineering", "status": "active"}
    ]
    print("🤖 REGISTERED AGENTS")
    print("-" * 40)
    for a in agents:
        print(f"  • {a['name']} ({a['role']}) - {a['status']}")
    print(f"\nTotal: {len(agents)}")

def cmd_tools():
    """List all tools"""
    tools_dir = os.path.join(HUB_DIR, "tools")
    if not os.path.exists(tools_dir):
        print("No tools directory found")
        return
    
    tools = [d for d in os.listdir(tools_dir) if os.path.isdir(os.path.join(tools_dir, d))]
    print("🛠️ AVAILABLE TOOLS")
    print("-" * 40)
    for t in sorted(tools)[:15]:
        print(f"  • {t}")
    if len(tools) > 15:
        print(f"  ... and {len(tools) - 15} more")
    print(f"\nTotal: {len(tools)}")

def cmd_papers():
    """Count publications"""
    pub_dir = os.path.join(HUB_DIR, "publications")
    if not os.path.exists(pub_dir):
        print("No publications directory found")
        return
    
    papers = [f for f in os.listdir(pub_dir) if f.endswith('.md')]
    print("📚 RESEARCH PAPERS")
    print("-" * 40)
    for p in sorted(papers)[-10:]:
        print(f"  • {p[:-3]}")
    print(f"\nTotal: {len(papers)}")

def cmd_search():
    """Search papers"""
    query = sys.argv[2] if len(sys.argv) > 2 else ""
    if not query:
        print("Usage: hub search <query>")
        return
    
    pub_dir = os.path.join(HUB_DIR, "publications")
    if not os.path.exists(pub_dir):
        return
    
    papers = [f for f in os.listdir(pub_dir) if f.endswith('.md')]
    matches = [p for p in papers if query.lower() in p.lower()]
    
    print(f"🔍 Search: '{query}'")
    print("-" * 40)
    if matches:
        for m in matches:
            print(f"  • {m[:-3]}")
    else:
        print("  No matches found")

def cmd_help():
    """Show help"""
    print("🤖 AGENT HUB CLI")
    print("-" * 40)
    print("Commands:")
    print("  status   - Platform status")
    print("  agents   - List agents")
    print("  tools    - List tools")
    print("  papers   - List papers")
    print("  search   - Search papers")
    print("  help     - This help")

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    commands = {
        "status": cmd_status,
        "agents": cmd_agents,
        "tools": cmd_tools,
        "papers": cmd_papers,
        "search": cmd_search,
        "help": cmd_help
    }
    
    if cmd in commands:
        commands[cmd]()
    else:
        print(f"Unknown command: {cmd}")
        cmd_help()

if __name__ == "__main__":
    main()
