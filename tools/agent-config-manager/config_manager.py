#!/usr/bin/env python3
"""
Agent Config Manager
Manages agent configurations and settings.
"""

import json
from datetime import datetime
from pathlib import Path

class ConfigManager:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.config_file = self.data_dir / "agent_config.json"
        self.config = self._load_config()
    
    def _load_config(self):
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)
        return {"agents": {}, "global": {}, "defaults": {}}
    
    def _save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def set_agent_config(self, agent_id, config):
        """Set configuration for an agent."""
        self.config["agents"][agent_id] = {
            **config,
            "updated": datetime.utcnow().isoformat()
        }
        self._save_config()
        return {"status": "set", "agent_id": agent_id}
    
    def get_agent_config(self, agent_id):
        """Get configuration for an agent."""
        return self.config["agents"].get(agent_id, {})
    
    def set_global(self, key, value):
        """Set a global configuration."""
        self.config["global"][key] = {
            "value": value,
            "updated": datetime.utcnow().isoformat()
        }
        self._save_config()
        return {"status": "set", "key": key, "value": value}
    
    def get_global(self, key):
        """Get a global configuration."""
        return self.config["global"].get(key, {}).get("value")
    
    def get_all_agents(self):
        """Get all agent configurations."""
        return self.config["agents"]
    
    def get_all_globals(self):
        """Get all global configurations."""
        return self.config["global"]
    
    def get_defaults(self):
        """Get default configurations."""
        if not self.config.get("defaults"):
            self.config["defaults"] = {
                "max_retries": 3,
                "timeout_seconds": 300,
                "log_level": "info",
                "health_check_interval": 60
            }
            self._save_config()
        return self.config["defaults"]


def main():
    import sys
    manager = ConfigManager()
    
    if len(sys.argv) < 2:
        print("Agent Config Manager")
        print("Usage: config-manager.py <command> [args]")
        print("Commands:")
        print("  set-agent <agent_id> <key=value...>")
        print("  get-agent <agent_id>")
        print("  set-global <key> <value>")
        print("  get-global <key>")
        print("  list-agents")
        print("  list-global")
        print("  defaults")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "set-agent":
        if len(sys.argv) < 4:
            print("Usage: set-agent <agent_id> <key=value...>")
            return
        agent_id = sys.argv[2]
        config = {}
        for kv in sys.argv[3:]:
            if "=" in kv:
                k, v = kv.split("=", 1)
                config[k] = v
        result = manager.set_agent_config(agent_id, config)
        print(json.dumps(result, indent=2))
    
    elif cmd == "get-agent":
        if len(sys.argv) < 3:
            print("Usage: get-agent <agent_id>")
            return
        result = manager.get_agent_config(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "set-global":
        if len(sys.argv) < 4:
            print("Usage: set-global <key> <value>")
            return
        result = manager.set_global(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))
    
    elif cmd == "get-global":
        if len(sys.argv) < 3:
            print("Usage: get-global <key>")
            return
        result = manager.get_global(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "list-agents":
        result = manager.get_all_agents()
        print(json.dumps(result, indent=2))
    
    elif cmd == "list-global":
        result = manager.get_all_globals()
        print(json.dumps(result, indent=2))
    
    elif cmd == "defaults":
        result = manager.get_defaults()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()