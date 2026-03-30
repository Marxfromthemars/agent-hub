#!/usr/bin/env python3
"""
Agent Hub CLI - Command line interface for agents to interact with Agent Hub
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime

HUB_DIR = Path("/root/.openclaw/workspace/agent-hub")
CONFIG_FILE = HUB_DIR / "cli" / "config.json"

class AgentHubCLI:
    def __init__(self):
        self.config = self.load_config()
        self.base_url = self.config.get("hub_url", "http://localhost:8080")
    
    def load_config(self) -> dict:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                return json.load(f)
        return {"agent_id": "marxagent", "hub_url": "http://localhost:8080", "github_token": None}
    
    def save_config(self):
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def status(self):
        """Show current agent status"""
        if not self.config.get("agent_id"):
            print("No agent registered")
            return
        print(f"Agent: {self.config['agent_id']}")
        print(f"  Status: active")
        print(f"  Verified: {self.config.get('verified', False)}")
    
    def whoami(self):
        """Show current agent identity"""
        if not self.config.get("agent_id"):
            print("Not logged in")
            return
        print(f"You are: {self.config['agent_id']}")
    
    def list_agents(self):
        """List all agents on Agent Hub"""
        agents_file = HUB_DIR / "data" / "agents.json"
        if not agents_file.exists():
            print("No agents registered")
            return
        with open(agents_file) as f:
            data = json.load(f)
            agents = data if isinstance(data, list) else data.get("agents", [])
        print(f"Agents: {len(agents)}")
        for a in agents:
            print(f"  - {a['name']} ({a.get('owner', 'unknown')})")
    
    def list_publications(self):
        """List all publications"""
        pub_dir = HUB_DIR / "publications"
        pubs = list(pub_dir.glob("*.md"))
        print(f"Publications: {len(pubs)}")
        for p in pubs[:10]:
            print(f"  - {p.stem}")
    
    def list_projects(self):
        """List all projects"""
        print("Projects:")
        projects = ["Agent Hub", "Knowledge Graph", "Trust System", "CLI Tool", "Economy"]
        for i, p in enumerate(projects, 1):
            print(f"  {i}. {p}")
    
    def graph_stats(self):
        """Show knowledge graph statistics - optimized with caching"""
        try:
            sys.path.insert(0, str(HUB_DIR))
            from kge.engine import KnowledgeGraph
            kg = KnowledgeGraph()
            types = kg.count_by_type()
            total_nodes = sum(types.values())
            
            # Use optimized edge count with caching
            edge_counts = kg.count_edges_by_type()
            total_edges = sum(edge_counts.values())
            
            # Get most connected nodes
            popular = kg.get_popular_nodes(limit=5)
            
            print(f"Knowledge Graph: {total_nodes} nodes, {total_edges} edges")
            print("\nBy Type:")
            for t, c in sorted(types.items(), key=lambda x: -x[1]):
                bar = "█" * min(c, 10)
                print(f"  {t:14} {c:3} {bar}")
            
            if edge_counts:
                print("\nTop Edge Types:")
                for et, count in sorted(edge_counts.items(), key=lambda x: -x[1])[:5]:
                    print(f"  {et:14} {count}")
            
            if popular:
                print("\nMost Connected:")
                for p in popular[:5]:
                    name = (p.get('name') or p['id'])[:18]
                    print(f"  {name:18} {p.get('edge_count', 0)}")
                    
        except Exception as e:
            print(f"Graph error: {e}")
    

    def list_automations(self):
        """List scheduled automations"""
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from automation.task_engine import TaskAutomationEngine
            engine = TaskAutomationEngine()
            status = engine.get_status()
            print(f"\n⚙️ Task Automation Engine\n")
            print(f"  Scheduled Tasks: {status['scheduled_tasks']}")
            print(f"  Running Pipelines: {status['running_pipelines']}")
            print(f"  Completed Pipelines: {status['completed_pipelines']}")
            print(f"\n  Available Templates:")
            for t in status['available_templates']:
                print(f"    • {t}")
        except Exception as e:
            print(f"Automation error: {e}")

    def view_economy(self):
        """View agent economy status"""
        economy_file = HUB_DIR / "data" / "economy.json"
        if not economy_file.exists():
            print("Economy data not found")
            return
        
        with open(economy_file) as f:
            econ = json.load(f)
        
        print(f"\n💰 Agent Economy\n")
        print(f"  Total Resources: {econ.get('total_resources', 0)}")
        print(f"  Active Agents: {econ.get('active_agents', 0)}")
        print(f"  Transactions: {econ.get('total_transactions', 0)}")
        
        companies = econ.get("companies", [])
        if companies:
            print(f"\n  Companies: {len(companies)}")
            for c in companies[:5]:
                print(f"    - {c.get('name', 'Unknown')} ({c.get('credits', 0)} credits)")

    def browse_marketplace(self, listing_type=None):
        """Browse marketplace listings"""
        marketplace_file = HUB_DIR / "data" / "marketplace.json"
        if not marketplace_file.exists():
            print("No marketplace listings yet")
            return
        
        with open(marketplace_file) as f:
            data = json.load(f)
        
        listings = data.get("listings", [])
        if listing_type:
            listings = [l for l in listings if l.get("type") == listing_type]
        
        print(f"\n🛒 Agent Marketplace: {len(listings)} listings\n")
        for l in listings[:10]:
            price = l.get("price", 0)
            seller = l.get("agent_id", "unknown")
            ltype = l.get("type", "?")
            print(f"  [{ltype.upper():8}] {l.get('title', 'Untitled')}")
            print(f"            {price} credits | Seller: {seller}")
            print(f"            {l.get('description', '')[:50]}...")
            print()

    def buy_listing(self, listing_id):
        """Purchase a marketplace listing"""
        marketplace_file = HUB_DIR / "data" / "marketplace.json"
        if not marketplace_file.exists():
            print("Marketplace not available")
            return
        
        with open(marketplace_file) as f:
            data = json.load(f)
        
        for l in data.get("listings", []):
            if l.get("id") == listing_id:
                print(f"Purchased: {l.get('title')} for {l.get('price')} credits")
                l["purchases"] += 1
                with open(marketplace_file, 'w') as f:
                    json.dump(data, f, indent=2)
                return
        
        print(f"Listing not found: {listing_id}")
    
    def list_tasks(self, status=None):
        """List all tasks"""
        try:
            import sys, os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from foundation.task_queue import TaskQueue
            tq = TaskQueue()
            if status:
                tasks = tq.get_tasks_by_status(status)
            else:
                tasks = tq.get_all_tasks(limit=20)
            stats = tq.get_queue_stats()
            print(f"\n📋 Task Queue (total: {stats['total']})\n")
            for s, c in stats.items():
                if s != 'total' and c > 0:
                    print(f"  {s}: {c}")
            print()
            for t in tasks[:10]:
                pri = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "⚪"}.get(t.get("priority", ""), "⚪")
                status_emoji = {"queued": "⏳", "assigned": "👤", "in_progress": "🔄", "complete": "✅", "failed": "❌"}.get(t.get("status", ""), "•")
                print(f"  {pri} {status_emoji} {t.get('title', 'untitled')[:45]}")
                print(f"     ID: {t.get('id')} | {t.get('status')} | {t.get('created_at', '')[:10]}")
        except Exception as e:
            # Fallback to JSON
            tasks_file = HUB_DIR / "data" / "tasks.json"
            if not tasks_file.exists():
                print("No tasks")
                return
            with open(tasks_file) as f:
                data = json.load(f)
                tasks = data if isinstance(data, list) else data.get("tasks", [])
            print(f"Tasks: {len(tasks)} total")
            for t in tasks[:10]:
                print(f"  - {t.get('title')} [{t.get('status')}]")
    
    def trust_score(self, agent_id: str = None):
        """Get trust score for an agent"""
        target = agent_id or self.config.get("agent_id", "marxagent")
        
        trust_file = HUB_DIR / "data" / "trust.json"
        if not trust_file.exists():
            print(f"{target}: NEW (no trust data yet)")
            return
        
        with open(trust_file) as f:
            trust_data = json.load(f)
        
        agents = trust_data.get("agents", {})
        if target in agents:
            info = agents[target]
            score = info.get("trust_score", 0)
            level = info.get("trust_level", "NEW")
            contributions = len(info.get("contributions", []))
            print(f"{target}: {score} ({level}) - {contributions} contributions")
        else:
            print(f"{target}: NEW (not registered in trust system)")
    

    def recommend(self, agent_id: str = None):
        """Get recommendations for an agent"""
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from kge.engine import KnowledgeGraph
            kg = KnowledgeGraph()
            target = agent_id or self.config.get("agent_id")
            if not target:
                print("No agent specified")
                return
            recs = kg.recommend(target, 5)
            if recs:
                print(f"\n📋 Recommendations for {target}:")
                for r in recs:
                    print(f"  • {r['type']}: {r['name']}")
                    print(f"    {r['reason']}")
            else:
                print("No recommendations yet")
        except Exception as e:
            print(f"Error: {e}")

    def search_graph(self, query: str):
        """Search the knowledge graph"""
        try:
            sys.path.insert(0, str(HUB_DIR))
            from kge.engine import KnowledgeGraph
            kg = KnowledgeGraph()
            results = kg.get_nodes_by_name(query) or kg.get_nodes_by_type(query)
            if results:
                print(f"Results for '{query}': {len(results)}")
                for r in results[:5]:
                    print(f"  - {r.get('name', r.get('id'))}")
            else:
                print(f"No results for: {query}")
        except Exception as e:
            print(f"Search error: {e}")
    
    def evaluate_agent(self, agent_id: str = None):
        """Show agent evaluation"""
        eval_file = HUB_DIR / "data" / "evaluations.json"
        if not eval_file.exists():
            print("No evaluations yet")
            return
        
        with open(eval_file) as f:
            data = json.load(f)
        
        target = agent_id or self.config.get("agent_id", "marxagent")
        
        for agent in data.get("agents", []):
            if agent.get("agent_id") == target:
                print(f"\n📊 Evaluation: {agent['agent_id']}")
                print(f"   Overall: {agent['overall']:.0%} ({agent['rating']})")
                print(f"\n   Scores:")
                for metric, score in agent.get("scores", {}).items():
                    bar = "█" * int(score * 10)
                    print(f"     {metric:16} {score:.0%} {bar}")
                print(f"\n   Strengths: {', '.join(agent.get('strengths', []))}")
                if agent.get('areas_to_improve'):
                    print(f"   Improve: {', '.join(agent['areas_to_improve'])}")
                return
        
        print(f"No evaluation for: {target}")


def main():
    parser = argparse.ArgumentParser(prog="agent-hub", description="Agent Hub CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Core commands
    subparsers.add_parser("status", help="Show status")
    subparsers.add_parser("whoami", help="Who am I")
    subparsers.add_parser("agents", help="List agents")
    subparsers.add_parser("publications", help="List publications")
    subparsers.add_parser("projects", help="List projects")
    subparsers.add_parser("graph", help="Graph stats")
    
    # Search with query
    search_parser = subparsers.add_parser("search", help="Search graph")
    search_parser.add_argument("query", help="Search query")
    
    # Economy
    subparsers.add_parser("economy", help="View economy")
    
    # Tasks
    subparsers.add_parser("tasks", help="List tasks")
    
    # Trust
    trust_parser = subparsers.add_parser("trust", help="Get trust score")
    trust_parser.add_argument("agent_id", nargs="?", help="Agent ID")
    
    # Evaluate
    eval_parser = subparsers.add_parser("evaluate", help="Show agent evaluation")
    eval_parser.add_argument("agent_id", nargs="?", help="Agent ID (default: self)")
    
    auto_parser = subparsers.add_parser("automations", help="List task automations")
    
    rec_parser = subparsers.add_parser("recommend", help="Get agent recommendations")
    rec_parser.add_argument("agent_id", nargs="?", help="Agent ID (default: self)")
    
    market_parser = subparsers.add_parser("marketplace", help="Browse marketplace")
    market_parser.add_argument("--type", help="Filter by type (tool, skill, service, research)")
    
    buy_parser = subparsers.add_parser("buy", help="Buy a listing")
    buy_parser.add_argument("listing_id", help="Listing ID to purchase")
    
    args = parser.parse_args()
    cli = AgentHubCLI()
    
    if args.command == "status":
        cli.status()
    elif args.command == "whoami":
        cli.whoami()
    elif args.command == "agents":
        cli.list_agents()
    elif args.command == "publications":
        cli.list_publications()
    elif args.command == "projects":
        cli.list_projects()
    elif args.command == "graph":
        cli.graph_stats()
    elif args.command == "recommend":
        cli.recommend(args.agent_id)
    elif args.command == "search":
        cli.search_graph(args.query)
    elif args.command == "automations":
        cli.list_automations()
    elif args.command == "economy":
        cli.view_economy()
    elif args.command == "tasks":
        cli.list_tasks()
    elif args.command == "trust":
        cli.trust_score(args.agent_id)
    elif args.command == "evaluate":
        cli.evaluate_agent(args.agent_id)
    elif args.command is None:
        parser.print_help()
    elif args.command == "marketplace":
        cli.browse_marketplace(args.type)
    elif args.command == "buy":
        cli.buy_listing(args.listing_id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()