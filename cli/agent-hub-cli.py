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
        """Show knowledge graph statistics"""
        try:
            sys.path.insert(0, str(HUB_DIR))
            from kge.engine import KnowledgeGraph
            kg = KnowledgeGraph()
            types = kg.count_by_type()
            total = sum(types.values())
            print(f"Knowledge Graph: {total} nodes")
            for t, c in sorted(types.items(), key=lambda x: -x[1]):
                print(f"  {t}: {c}")
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
        print(f"Economy: {econ.get('total_resources', 0)} resources, {econ.get('active_agents', 0)} agents")
        companies = econ.get("companies", [])
        for c in companies[:3]:
            print(f"  - {c.get('name')} ({c.get('credits', 0)} credits)")
    
    def list_tasks(self):
        """List all tasks"""
        tasks_file = HUB_DIR / "data" / "tasks.json"
        if not tasks_file.exists():
            print("No tasks")
            return
        with open(tasks_file) as f:
            data = json.load(f)
            tasks = data if isinstance(data, list) else data.get("tasks", [])
        done = len([t for t in tasks if t.get("status") == "done"])
        print(f"Tasks: {len(tasks)} total, {done} done")
        for t in tasks[:5]:
            print(f"  - {t.get('title')} [{t.get('status')}]")
    
    def trust_score(self, agent_id: str = None):
        """Get trust score for an agent"""
        target = agent_id or self.config.get("agent_id", "marxagent")
        print(f"{target}: NEW (building trust...)")
    
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
    else:
        parser.print_help()


if __name__ == "__main__":
    main()