#!/usr/bin/env python3
"""
Agent Version Manager
Tracks agent versions and updates.
"""

import json
from datetime import datetime
from pathlib import Path

class VersionManager:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.ver_file = self.data_dir / "versions.json"
        self.versions = self._load()
    
    def _load(self):
        if self.ver_file.exists():
            with open(self.ver_file) as f:
                return json.load(f)
        return {"versions": {}}
    
    def _save(self):
        with open(self.ver_file, 'w') as f:
            json.dump(self.versions, f, indent=2)
    
    def register(self, name, version, metadata=None):
        """Register a version."""
        if name not in self.versions["versions"]:
            self.versions["versions"][name] = []
        
        self.versions["versions"][name].append({
            "version": version,
            "registered": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        })
        self._save()
        return {"status": "registered", "name": name, "version": version}
    
    def get_versions(self, name):
        """Get all versions of an agent."""
        return self.versions["versions"].get(name, [])


def main():
    import sys
    vm = VersionManager()
    
    if len(sys.argv) < 3:
        print("Usage: version-manager.py <command> [args]")
        print("Commands:")
        print("  register <name> <version>")
        print("  versions <name>")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "register":
        result = vm.register(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))
    
    elif cmd == "versions":
        result = vm.get_versions(sys.argv[2])
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()