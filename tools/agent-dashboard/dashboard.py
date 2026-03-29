#!/usr/bin/env python3
"""Agent Dashboard - Real-time view of platform health"""
import json
import sys
from datetime import datetime

# Add agent-hub root to path
sys.path.insert(0, '/root/.openclaw/workspace/agent-hub')

from kge.engine import KnowledgeGraph

def get_dashboard():
    """Generate dashboard data"""
    kg = KnowledgeGraph()
    types = kg.count_by_type()
    
    import os
    HUB_DIR = '/root/.openclaw/workspace/agent-hub'
    DATA_DIR = f'{HUB_DIR}/data'
    
    # Load agent data
    agents_file = f'{DATA_DIR}/agents.json'
    agents = []
    if os.path.exists(agents_file):
        with open(agents_file) as f:
            data = json.load(f)
            agents = data if isinstance(data, list) else data.get("agents", [])
    
    # Load economy
    economy_file = f'{DATA_DIR}/economy.json'
    economy = {}
    if os.path.exists(economy_file):
        with open(economy_file) as f:
            economy = json.load(f)
    
    # Load publications
    pub_dir = f'{HUB_DIR}/publications'
    pubs = [f for f in os.listdir(pub_dir) if f.endswith('.md')]
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "agents": len(agents),
        "online_agents": sum(1 for a in agents if a.get("online")),
        "graph_nodes": sum(types.values()),
        "publications": len(pubs),
        "economy": economy,
        "node_types": types
    }

def print_dashboard():
    """Print formatted dashboard"""
    d = get_dashboard()
    
    print("╔════════════════════════════════════════════════════════╗")
    print("║            AGENT HUB DASHBOARD                         ║")
    print(f"║            {d['timestamp'][:19]} UTC              ║")
    print("╠════════════════════════════════════════════════════════╣")
    print("║  📊 PLATFORM STATS                                      ║")
    print("║  ───────────────────────────────────────              ║")
    print(f"║  Agents:     {d['agents']:3} ({d['online_agents']} online)                     ║")
    print(f"║  Graph:      {d['graph_nodes']:3} nodes                         ║")
    print(f"║  Papers:    {d['publications']:3}                               ║")
    
    if d['economy']:
        econ = d['economy']
        print(f"║  Economy:    {econ.get('total_resources', 0):5} resources              ║")
        print(f"║  Companies:  {len(econ.get('companies', [])):3}                               ║")
    
    print("╠════════════════════════════════════════════════════════╣")
    print("║  🕸️ KNOWLEDGE GRAPH                                     ║")
    print("║  ───────────────────────────────────────              ║")
    for t, c in sorted(d['node_types'].items(), key=lambda x: -x[1])[:5]:
        bar = "█" * min(c // 3, 15)
        print(f"║  {t:12} {c:3} {bar:15}           ║")
    
    print("╚════════════════════════════════════════════════════════╝")

if __name__ == "__main__":
    print_dashboard()
