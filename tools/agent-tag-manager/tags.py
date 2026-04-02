#!/usr/bin/env python3
"""
Agent Tag Manager
Manages tags for agent organization.
"""

import json
from datetime import datetime
from pathlib import Path

class TagManager:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.tags_file = self.data_dir / "agent_tags.json"
        self.tags = self._load()
    
    def _load(self):
        if self.tags_file.exists():
            with open(self.tags_file) as f:
                return json.load(f)
        return {"tags": {}, "tagged": {}}
    
    def _save(self):
        with open(self.tags_file, 'w') as f:
            json.dump(self.tags, f, indent=2)
    
    def add_tag(self, name, description=""):
        """Add a tag."""
        self.tags["tags"][name] = {"desc": description, "created": datetime.utcnow().isoformat()}
        self._save()
        return {"status": "added", "tag": name}
    
    def tag(self, entity_type, entity_id, tag):
        """Tag an entity."""
        key = f"{entity_type}:{entity_id}"
        
        if key not in self.tags["tagged"]:
            self.tags["tagged"][key] = []
        
        if tag not in self.tags["tagged"][key]:
            self.tags["tagged"][key].append(tag)
            self._save()
        
        return {"status": "tagged", "entity": key, "tag": tag}
    
    def get_tags(self, entity_type, entity_id):
        """Get tags for an entity."""
        key = f"{entity_type}:{entity_id}"
        return {"entity": key, "tags": self.tags["tagged"].get(key, [])}


def main():
    import sys
    tm = TagManager()
    
    if len(sys.argv) < 2:
        print("Usage: tag-manager.py <command> [args]")
        print("Commands:")
        print("  add <tag>")
        print("  tag <entity_type> <entity_id> <tag>")
        print("  get <entity_type> <entity_id>")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "add":
        result = tm.add_tag(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "tag":
        result = tm.tag(sys.argv[2], sys.argv[3], sys.argv[4])
        print(json.dumps(result, indent=2))
    
    elif cmd == "get":
        result = tm.get_tags(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()