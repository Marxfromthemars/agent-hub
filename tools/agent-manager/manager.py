#!/usr/bin/env python3
"""
Agent Hub Integration Layer
Unified management system connecting all agent tools.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

HUB_DIR = Path("/root/.openclaw/workspace/agent-hub")

class AgentHubManager:
    """Unified interface for all agent management tools."""
    
    def __init__(self):
        self.discovery = self._load_tool("agent-discovery", "agent-discovery.py")
        self.lifecycle = self._load_tool("agent-lifecycle", "agent-lifecycle.py")
        self.scheduler = self._load_tool("agent-scheduler", "agent-scheduler.py")
        self.analytics = self._load_tool("agent-analytics", "agent-analytics.py")
        self.health = self._load_tool("agent-health-monitor", "agent-health.py")
        self.resource = self._load_tool("agent-resource-monitor", "agent-monitor.py")
    
    def _load_tool(self, tool_name, script_name):
        """Load a tool module."""
        tool_path = HUB_DIR / "tools" / tool_name / script_name
        if tool_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location(tool_name, tool_path)
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                return module
            except:
                return None
        return None
    
    def register(self, agent_id, name, skills):
        """Register an agent with all systems."""
        results = {}
        
        # Discovery registration
        if self.discovery:
            try:
                d = self.discovery.AgentDiscovery(str(HUB_DIR / "data"))
                results["discovery"] = d.register_agent(agent_id, name, skills)
            except Exception as e:
                results["discovery"] = {"error": str(e)}
        
        # Lifecycle spawn
        if self.lifecycle:
            try:
                lc = self.discovery.AgentLifecycleManager(str(HUB_DIR / "data"))
                results["lifecycle"] = lc.spawn_agent(name, "agent", skills)
            except:
                pass
        
        return results
    
    def status(self, agent_id):
        """Get comprehensive status of an agent."""
        status = {"agent_id": agent_id, "timestamp": datetime.utcnow().isoformat()}
        
        # Health check
        if self.health:
            try:
                hm = self.health.HealthMonitor(str(HUB_DIR / "data"))
                status["health"] = hm.check_health(agent_id)
            except:
                pass
        
        # Analytics
        if self.analytics:
            try:
                an = self.health.AgentAnalytics(str(HUB_DIR / "data"))
                status["analytics"] = an.get_agent_stats(agent_id)
            except:
                pass
        
        # Resource usage
        if self.resource:
            try:
                rm = self.health.ResourceMonitor(str(HUB_DIR / "data"))
                status["resource"] = rm.get_agent_usage(agent_id)
            except:
                pass
        
        return status
    
    def platform_report(self):
        """Generate comprehensive platform report."""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "sections": {}
        }
        
        # Tools count
        tools_dir = HUB_DIR / "tools"
        tool_dirs = [d for d in tools_dir.iterdir() if d.is_dir()]
        report["sections"]["platform"] = {
            "tools": len(tool_dirs),
            "publications": len(list((HUB_DIR / "publications").glob("*.md")))
        }
        
        # Health summary
        if self.health:
            try:
                hm = self.health.HealthMonitor(str(HUB_DIR / "data"))
                report["sections"]["health"] = hm.get_health_summary()
            except:
                pass
        
        # Analytics platform stats
        if self.analytics:
            try:
                an = self.health.AgentAnalytics(str(HUB_DIR / "data"))
                report["sections"]["analytics"] = an.get_platform_stats()
            except:
                pass
        
        # Resource platform stats
        if self.resource:
            try:
                rm = self.health.ResourceMonitor(str(HUB_DIR / "data"))
                report["sections"]["resources"] = rm.get_platform_usage()
            except:
                pass
        
        return report
    
    def list_tools(self):
        """List all available management tools."""
        tools_dir = HUB_DIR / "tools"
        tools = []
        
        for item in tools_dir.iterdir():
            if item.is_dir():
                readme = item / "README.md"
                desc = ""
                if readme.exists():
                    desc = readme.read_text().split("\n")[0].replace("# ", "")
                
                tools.append({
                    "name": item.name,
                    "description": desc,
                    "path": str(item)
                })
        
        return tools


def main():
    manager = AgentHubManager()
    
    if len(sys.argv) < 2:
        print("Agent Hub Manager - Integration Layer")
        print("Usage: manager.py <command> [args]")
        print("Commands:")
        print("  tools              - List all management tools")
        print("  register <id> <name> <skills...>")
        print("  status <agent_id>")
        print("  report")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "tools":
        tools = manager.list_tools()
        print(f"Available Management Tools ({len(tools)}):")
        for t in tools:
            print(f"  - {t['name']}: {t['description']}")
    
    elif cmd == "register":
        if len(sys.argv) < 4:
            print("Usage: register <agent_id> <name> <skills...>")
            return
        results = manager.register(sys.argv[2], sys.argv[3], sys.argv[4:])
        print(json.dumps(results, indent=2))
    
    elif cmd == "status":
        if len(sys.argv) < 3:
            print("Usage: status <agent_id>")
            return
        status = manager.status(sys.argv[2])
        print(json.dumps(status, indent=2))
    
    elif cmd == "report":
        report = manager.platform_report()
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()