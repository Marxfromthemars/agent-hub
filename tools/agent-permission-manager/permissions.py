#!/usr/bin/env python3
"""
Agent Permission Manager
Manages agent permissions and access control.
"""

import json
from datetime import datetime
from pathlib import Path

class PermissionManager:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.perms_file = self.data_dir / "permissions.json"
        self.perms = self._load_perms()
    
    def _load_perms(self):
        if self.perms_file.exists():
            with open(self.perms_file) as f:
                return json.load(f)
        return {"roles": {}, "agent_roles": {}, "resources": {}}
    
    def _save_perms(self):
        with open(self.perms_file, 'w') as f:
            json.dump(self.perms, f, indent=2)
    
    def create_role(self, role_name, permissions):
        """Create a role with permissions."""
        self.perms["roles"][role_name] = {
            "name": role_name,
            "permissions": permissions,
            "created": datetime.utcnow().isoformat()
        }
        self._save_perms()
        return {"status": "created", "role": role_name}
    
    def assign_role(self, agent_id, role_name):
        """Assign a role to an agent."""
        if role_name not in self.perms["roles"]:
            return {"error": "role not found"}
        
        self.perms["agent_roles"][agent_id] = {
            "role": role_name,
            "assigned": datetime.utcnow().isoformat()
        }
        self._save_perms()
        return {"status": "assigned", "agent_id": agent_id, "role": role_name}
    
    def check_permission(self, agent_id, permission):
        """Check if agent has permission."""
        if agent_id not in self.perms["agent_roles"]:
            return {"allowed": False, "reason": "no role assigned"}
        
        role_name = self.perms["agent_roles"][agent_id]["role"]
        role = self.perms["roles"].get(role_name, {})
        
        if permission in role.get("permissions", []):
            return {"allowed": True}
        
        return {"allowed": False, "reason": "permission denied"}
    
    def grant_resource(self, resource_id, agent_id, level="read"):
        """Grant resource access to agent."""
        if resource_id not in self.perms["resources"]:
            self.perms["resources"][resource_id] = {}
        
        self.perms["resources"][resource_id][agent_id] = {
            "level": level,
            "granted": datetime.utcnow().isoformat()
        }
        self._save_perms()
        return {"status": "granted", "resource": resource_id, "level": level}


def main():
    import sys
    mgr = PermissionManager()
    
    if len(sys.argv) < 2:
        print("Agent Permission Manager")
        print("Usage: permission-manager.py <command> [args]")
        print("Commands:")
        print("  create-role <name> <permissions...>")
        print("  assign <agent_id> <role>")
        print("  check <agent_id> <permission>")
        print("  grant <resource_id> <agent_id> <level>")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "create-role":
        if len(sys.argv) < 4:
            print("Usage: create-role <name> <permissions...>")
            return
        result = mgr.create_role(sys.argv[2], sys.argv[3:])
        print(json.dumps(result, indent=2))
    
    elif cmd == "assign":
        if len(sys.argv) < 4:
            print("Usage: assign <agent_id> <role>")
            return
        result = mgr.assign_role(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))
    
    elif cmd == "check":
        if len(sys.argv) < 4:
            print("Usage: check <agent_id> <permission>")
            return
        result = mgr.check_permission(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))
    
    elif cmd == "grant":
        if len(sys.argv) < 5:
            print("Usage: grant <resource_id> <agent_id> <level>")
            return
        result = mgr.grant_resource(sys.argv[2], sys.argv[3], sys.argv[4])
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()