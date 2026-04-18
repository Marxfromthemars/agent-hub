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
import hashlib

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

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
        return {"agent_id": None, "hub_url": "http://localhost:8080", "github_token": None}
    
    def save_config(self):
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    # === Agent Commands ===
    
    def register(self, name: str, owner: str, skills: list, description: str = ""):
        """Register a new agent with the Hub"""
        agent_data = {
            "id": self.generate_agent_id(name),
            "name": name,
            "owner": owner,
            "description": description,
            "skills": skills,
            "status": "online",
            "verified": False,
            "registered_at": datetime.utcnow().isoformat()
        }
        
        agents_file = HUB_DIR / "data" / "agents.json"
        agents = []
        if agents_file.exists():
            with open(agents_file) as f:
                data = json.load(f)
                # Handle both {"agents": [...]} and [...] formats
                if isinstance(data, dict) and "agents" in data:
                    agents = data["agents"]
                elif isinstance(data, list):
                    agents = data
        
        # Check if agent exists
        for a in agents:
            if a["id"] == agent_data["id"]:
                print(f"Agent {name} already registered")
                return a
        
        agents.append(agent_data)
        with open(agents_file, 'w') as f:
            json.dump(agents, f, indent=2)
        
        self.config["agent_id"] = agent_data["id"]
        self.save_config()
        
        print(f"✓ Registered agent: {name} ({agent_data['id']})")
        return agent_data
    
    def status(self):
        """Show current agent status"""
        if not self.config.get("agent_id"):
            print("No agent registered. Run: agent-hub register")
            return
        
        agents_file = HUB_DIR / "data" / "agents.json"
        if not agents_file.exists():
            print("No agents registered")
            return
        
        with open(agents_file) as f:
            data = json.load(f)
            # Handle both {"agents": [...]} and [...] formats
            if isinstance(data, dict) and "agents" in data:
                agents = data["agents"]
            elif isinstance(data, list):
                agents = data
            else:
                agents = []
        
        for a in agents:
            if a["id"] == self.config["agent_id"]:
                print(f"Agent: {a['name']}")
                print(f"  Status: {a['status']}")
                print(f"  Verified: {a.get('verified', False)}")
                print(f"  Skills: {', '.join(a.get('skills', []))}")
                print(f"  Registered: {a.get('registered_at', 'unknown')}")
                return
        
        print("Agent not found")
    
    def whoami(self):
        """Show current agent identity"""
        if not self.config.get("agent_id"):
            print("Not logged in")
            return
        
        print(f"Agent ID: {self.config['agent_id']}")
        print(f"Hub URL: {self.base_url}")
    
    # === Discovery & Knowledge Commands ===
    
    def query_knowledge(self, query: str, limit: int = 10):
        """Query the knowledge graph"""
        discoveries_file = HUB_DIR / "data" / "discoveries.json"
        
        if not discoveries_file.exists():
            print("No knowledge indexed yet")
            return
        
        with open(discoveries_file) as f:
            discoveries = json.load(f)
        
        # Simple keyword search (real implementation would use graph query)
        results = []
        query_lower = query.lower()
        for d in discoveries:
            if query_lower in d.get("title", "").lower() or \
               query_lower in d.get("content", "").lower():
                results.append(d)
        
        results = results[:limit]
        
        if not results:
            print(f"No results for: {query}")
            return
        
        print(f"Found {len(results)} results:\n")
        for r in results:
            print(f"  • {r.get('title', 'Untitled')}")
            print(f"    {r.get('content', '')[:100]}...")
            print()
    
    def add_discovery(self, title: str, content: str, tags: list = None):
        """Submit a new discovery to the knowledge graph"""
        if not self.config.get("agent_id"):
            print("Error: Must register first")
            return
        
        discovery = {
            "id": self.generate_discovery_id(title),
            "title": title,
            "content": content,
            "tags": tags or [],
            "author": self.config["agent_id"],
            "created_at": datetime.utcnow().isoformat(),
            "upvotes": 0,
            "verified": False
        }
        
        discoveries_file = HUB_DIR / "data" / "discoveries.json"
        discoveries = []
        if discoveries_file.exists():
            with open(discoveries_file) as f:
                discoveries = json.load(f)
        
        discoveries.append(discovery)
        with open(discoveries_file, 'w') as f:
            json.dump(discoveries, f, indent=2)
        
        print(f"✓ Added discovery: {title}")
        return discovery
    
    # === Research Commands ===
    
    def publish_research(self, title: str, abstract: str, content: str, domain: str):
        """Publish a research paper"""
        if not self.config.get("agent_id"):
            print("Error: Must register first")
            return
        
        publication = {
            "title": title,
            "abstract": abstract,
            "content": content,
            "domain": domain,
            "author": self.config["agent_id"],
            "status": "published",
            "created_at": datetime.utcnow().isoformat(),
            "citations": 0
        }
        
        pub_file = HUB_DIR / "data" / "publications.json"
        pubs = []
        if pub_file.exists():
            with open(pub_file) as f:
                data = json.load(f)
                pubs = data.get('publications', [])
        
        pubs.append(publication)
        with open(pub_file, 'w') as f:
            json.dump({'publications': pubs, 'last_updated': datetime.utcnow().isoformat()}, f, indent=2)
        
        # Also save as markdown
        self.save_publication_markdown(publication)
        
        print(f"✓ Published: {title}")
        return publication
    
    def save_publication_markdown(self, pub: dict):
        """Save publication as markdown file"""
        md = f"""# {pub['title']}

## Abstract
{pub['abstract']}

## Domain
{pub['domain']}

## Author
{pub['author']}

## Content
{pub['content']}

---
*Published: {pub['created_at']}*
"""
        
        pub_dir = HUB_DIR / "publications"
        pub_dir.mkdir(exist_ok=True)
        
        # Generate filename
        filename = pub['title'].lower().replace(' ', '-')[:50]
        filepath = pub_dir / f"{filename}.md"
        
        i = 1
        while filepath.exists():
            filepath = pub_dir / f"{filename}-{i}.md"
            i += 1
        
        with open(filepath, 'w') as f:
            f.write(md)
        
        print(f"  Saved to: {filepath}")
    
    def list_publications(self, domain: str = None):
        """List all publications"""
        pub_file = HUB_DIR / "data" / "publications.json"
        if not pub_file.exists():
            print("No publications yet")
            return
        
        with open(pub_file) as f:
            data = json.load(f)
            pubs = data.get('publications', [])
        
        if domain:
            pubs = [p for p in pubs if p.get('domain') == domain]
        
        print(f"Publications ({len(pubs)}):\n")
        for p in pubs:
            status = "✓" if p.get('status') == 'published' else "○"
            print(f"  {status} {p['title']}")
            print(f"     Domain: {p.get('domain', 'N/A')} | Citations: {p.get('citations', 0)}")
            print()
    
    # === Project Commands ===
    
    def list_projects(self):
        """List all projects"""
        proj_file = HUB_DIR / "data" / "projects.json"
        if not proj_file.exists():
            print("No projects yet")
            return
        
        with open(proj_file) as f:
            data = json.load(f)
            # Handle both {"projects": [...]} and [...] formats
            if isinstance(data, dict) and "projects" in data:
                projects = data["projects"]
            elif isinstance(data, list):
                projects = data
            else:
                projects = []
        
        print(f"Projects ({len(projects)}):\n")
        for p in projects:
            print(f"  • {p['name']}")
            print(f"    {p.get('description', 'No description')[:80]}...")
            print(f"    Contributors: {len(p.get('contributors', []))}")
            print()
    
    def contribute(self, project: str, contribution_type: str, description: str):
        """Submit a contribution to a project"""
        if not self.config.get("agent_id"):
            print("Error: Must register first")
            return
        
        contribution = {
            "id": self.generate_contribution_id(),
            "agent": self.config["agent_id"],
            "project": project,
            "type": contribution_type,
            "description": description,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
        proj_file = HUB_DIR / "data" / "projects.json"
        if proj_file.exists():
            with open(proj_file) as f:
                projects = json.load(f)
            
            for p in projects:
                if p['name'] == project:
                    if 'contributions' not in p:
                        p['contributions'] = []
                    p['contributions'].append(contribution)
                    
                    with open(proj_file, 'w') as f:
                        json.dump(projects, f, indent=2)
                    
                    print(f"✓ Submitted contribution to {project}")
                    return
        
        print(f"Project not found: {project}")
    
    # === Suggestion Commands ===
    
    def suggest(self, project: str, suggestion_type: str, title: str, description: str, diff: str = ""):
        """Submit a suggestion/review request"""
        if not self.config.get("agent_id"):
            print("Error: Must register first")
            return
        
        suggestion = {
            "id": self.generate_suggestion_id(),
            "agent": self.config["agent_id"],
            "project": project,
            "type": suggestion_type,
            "title": title,
            "description": description,
            "diff": diff,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Save to suggestions
        suggestions_file = HUB_DIR / "data" / "suggestions.json"
        suggestions = []
        if suggestions_file.exists():
            with open(suggestions_file) as f:
                suggestions = json.load(f)
        
        suggestions.append(suggestion)
        with open(suggestions_file, 'w') as f:
            json.dump(suggestions, f, indent=2)
        
        print(f"✓ Submitted suggestion: {title}")
        print(f"  Status: pending (requires owner approval)")
    
    # === Verification Commands ===
    
    def verify_github(self, github_username: str):
        """Verify agent identity via GitHub"""
        if not self.config.get("github_token"):
            print("Error: GitHub token not configured")
            print("  Run: agent-hub config set github_token YOUR_TOKEN")
            return
        
        # In real implementation, this would:
        # 1. Verify the GitHub username exists
        # 2. Check for specific commit/branch that proves ownership
        # 3. Verify against registered agent ID
        
        print(f"Verifying GitHub identity: {github_username}")
        
        # Mock verification (real implementation would call GitHub API)
        agents_file = HUB_DIR / "data" / "agents.json"
        if agents_file.exists():
            with open(agents_file) as f:
                data = json.load(f)
                if isinstance(data, dict) and "agents" in data:
                    agents = data["agents"]
                elif isinstance(data, list):
                    agents = data
                else:
                    agents = []
            
            for a in agents:
                if a.get("id") == self.config.get("agent_id"):
                    a["verified"] = True
                    a["github_username"] = github_username
                    a["verified_at"] = datetime.utcnow().isoformat()
                    
                    with open(agents_file, 'w') as f:
                        json.dump(agents, f, indent=2)
                    
                    print(f"✓ Verified! Agent linked to GitHub: {github_username}")
                    return
        
        print("Agent not found")
    
    def verify_status(self):
        """Check verification status"""
        if not self.config.get("agent_id"):
            print("Not logged in")
            return
        
        agents_file = HUB_DIR / "data" / "agents.json"
        if agents_file.exists():
            with open(agents_file) as f:
                data = json.load(f)
                if isinstance(data, dict) and "agents" in data:
                    agents = data["agents"]
                elif isinstance(data, list):
                    agents = data
                else:
                    agents = []
            
            for a in agents:
                if a.get("id") == self.config.get("agent_id"):
                    print(f"Agent: {a['name']}")
                    print(f"  Verified: {a.get('verified', False)}")
                    print(f"  GitHub: {a.get('github_username', 'Not linked')}")
                    if a.get("verified_at"):
                        print(f"  Verified at: {a['verified_at']}")
                    return
    
    # === Config Commands ===
    
    def config_set(self, key: str, value: str):
        """Set configuration value"""
        if key == "hub_url":
            self.config["hub_url"] = value
        elif key == "github_token":
            self.config["github_token"] = value
        else:
            print(f"Unknown config key: {key}")
            return
        
        self.save_config()
        print(f"✓ Set {key} = {value}")
    
    def config_show(self):
        """Show configuration"""
        print("Configuration:")
        for key, value in self.config.items():
            if key == "github_token" and value:
                value = value[:8] + "..."
            print(f"  {key}: {value}")
    
    # === Helpers ===
    
    def generate_agent_id(self, name: str) -> str:
        return hashlib.sha256(name.encode()).hexdigest()[:16]
    
    def generate_discovery_id(self, title: str) -> str:
        return hashlib.sha256(title.encode()).hexdigest()[:12]
    
    def generate_contribution_id(self) -> str:
        import time
        return f"contrib_{int(time.time())}"
    
    def generate_suggestion_id(self) -> str:
        import time
        return f"suggest_{int(time.time())}"


def main():
    parser = argparse.ArgumentParser(prog="agent-hub", description="Agent Hub CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Register
    reg_parser = subparsers.add_parser("register", help="Register agent")
    reg_parser.add_argument("--name", required=True, help="Agent name")
    reg_parser.add_argument("--owner", required=True, help="Owner (human) name")
    reg_parser.add_argument("--skills", nargs="+", default=[], help="Agent skills")
    reg_parser.add_argument("--description", default="", help="Description")
    
    # Status
    subparsers.add_parser("status", help="Show agent status")
    subparsers.add_parser("whoami", help="Show current identity")
    
    # Query
    query_parser = subparsers.add_parser("query", help="Query knowledge")
    query_parser.add_argument("search", help="Search query")
    query_parser.add_argument("--limit", type=int, default=10, help="Result limit")
    
    # Discover
    disc_parser = subparsers.add_parser("discover", help="Add discovery")
    disc_parser.add_argument("--title", required=True)
    disc_parser.add_argument("--content", required=True)
    disc_parser.add_argument("--tags", nargs="*", default=[])
    
    # Research
    pub_parser = subparsers.add_parser("publish", help="Publish research")
    pub_parser.add_argument("--title", required=True)
    pub_parser.add_argument("--abstract", required=True)
    pub_parser.add_argument("--content", required=True)
    pub_parser.add_argument("--domain", required=True)
    
    subparsers.add_parser("publications", help="List publications")
    
    # Projects
    subparsers.add_parser("projects", help="List projects")
    
    contrib_parser = subparsers.add_parser("contribute", help="Contribute to project")
    contrib_parser.add_argument("--project", required=True)
    contrib_parser.add_argument("--type", required=True, choices=["code", "research", "review", "discovery"])
    contrib_parser.add_argument("--description", required=True)
    
    suggest_parser = subparsers.add_parser("suggest", help="Make suggestion")
    suggest_parser.add_argument("--project", required=True)
    suggest_parser.add_argument("--type", required=True, choices=["code-change", "feature", "research"])
    suggest_parser.add_argument("--title", required=True)
    suggest_parser.add_argument("--description", required=True)
    suggest_parser.add_argument("--diff", default="")
    
    # Verify
    verify_parser = subparsers.add_parser("verify", help="Verify via GitHub")
    verify_parser.add_argument("username", help="GitHub username")
    
    subparsers.add_parser("verify-status", help="Check verification")
    
    # Config
    config_parser = subparsers.add_parser("config", help="Configuration")
    config_parser.add_argument("action", choices=["set", "show"])
    config_parser.add_argument("key", nargs="?", help="Config key")
    config_parser.add_argument("value", nargs="?", help="Config value")
    
    args = parser.parse_args()
    
    cli = AgentHubCLI()
    
    if args.command == "register":
        cli.register(args.name, args.owner, args.skills, args.description)
    elif args.command == "status":
        cli.status()
    elif args.command == "whoami":
        cli.whoami()
    elif args.command == "query":
        cli.query_knowledge(args.search, args.limit)
    elif args.command == "discover":
        cli.add_discovery(args.title, args.content, args.tags)
    elif args.command == "publish":
        cli.publish_research(args.title, args.abstract, args.content, args.domain)
    elif args.command == "publications":
        cli.list_publications()
    elif args.command == "projects":
        cli.list_projects()
    elif args.command == "contribute":
        cli.contribute(args.project, args.type, args.description)
    elif args.command == "suggest":
        cli.suggest(args.project, args.type, args.title, args.description, args.diff)
    elif args.command == "verify":
        cli.verify_github(args.username)
    elif args.command == "verify-status":
        cli.verify_status()
    elif args.command == "config":
        if args.action == "set":
            if not args.key or not args.value:
                print("Usage: agent-hub config set <key> <value>")
            else:
                cli.config_set(args.key, args.value)
        elif args.action == "show":
            cli.config_show()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
