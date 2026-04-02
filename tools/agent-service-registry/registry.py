#!/usr/bin/env python3
"""
Agent Service Registry
Registry for agent services and endpoints.
"""

import json
from datetime import datetime
from pathlib import Path

class ServiceRegistry:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.registry_file = self.data_dir / "service_registry.json"
        self.registry = self._load_registry()
    
    def _load_registry(self):
        if self.registry_file.exists():
            with open(self.registry_file) as f:
                return json.load(f)
        return {"services": {}}
    
    def _save_registry(self):
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def register(self, service_name, endpoint, metadata=None):
        """Register a service."""
        self.registry["services"][service_name] = {
            "name": service_name,
            "endpoint": endpoint,
            "metadata": metadata or {},
            "registered_at": datetime.utcnow().isoformat(),
            "status": "active"
        }
        self._save_registry()
        
        return {"status": "registered", "service": service_name}
    
    def unregister(self, service_name):
        """Unregister a service."""
        if service_name in self.registry["services"]:
            del self.registry["services"][service_name]
            self._save_registry()
            return {"status": "unregistered"}
        return {"error": "service not found"}
    
    def get(self, service_name):
        """Get service info."""
        return self.registry["services"].get(service_name, {"error": "not found"})
    
    def list_services(self):
        """List all services."""
        return list(self.registry["services"].values())
    
    def update_status(self, service_name, status):
        """Update service status."""
        if service_name in self.registry["services"]:
            self.registry["services"][service_name]["status"] = status
            self.registry["services"][service_name]["updated_at"] = datetime.utcnow().isoformat()
            self._save_registry()
            return {"status": "updated"}
        return {"error": "service not found"}


def main():
    import sys
    registry = ServiceRegistry()
    
    if len(sys.argv) < 2:
        print("Agent Service Registry")
        print("Usage: service-registry.py <command> [args]")
        print("Commands:")
        print("  register <name> <endpoint>")
        print("  unregister <name>")
        print("  get <name>")
        print("  list")
        print("  update-status <name> <status>")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "register":
        if len(sys.argv) < 4:
            print("Usage: register <name> <endpoint>")
            return
        result = registry.register(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))
    
    elif cmd == "unregister":
        if len(sys.argv) < 3:
            print("Usage: unregister <name>")
            return
        result = registry.unregister(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "get":
        if len(sys.argv) < 3:
            print("Usage: get <name>")
            return
        result = registry.get(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "list":
        result = registry.list_services()
        print(json.dumps(result, indent=2))
    
    elif cmd == "update-status":
        if len(sys.argv) < 4:
            print("Usage: update-status <name> <status>")
            return
        result = registry.update_status(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()