#!/usr/bin/env python3
"""
Agent API Key Manager
Manages API keys for agent authentication.
"""

import json
import secrets
from datetime import datetime, timedelta
from pathlib import Path

class APIKeyManager:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.keys_file = self.data_dir / "api_keys.json"
        self.keys = self._load_keys()
    
    def _load_keys(self):
        if self.keys_file.exists():
            with open(self.keys_file) as f:
                return json.load(f)
        return {"keys": {}}
    
    def _save_keys(self):
        with open(self.keys_file, 'w') as f:
            json.dump(self.keys, f, indent=2)
    
    def generate_key(self, agent_id, name, expires_in_days=30):
        """Generate an API key."""
        key = f"ak_{secrets.token_hex(16)}"
        
        self.keys["keys"][key] = {
            "agent_id": agent_id,
            "name": name,
            "created": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=expires_in_days)).isoformat(),
            "active": True
        }
        self._save_keys()
        
        return {"status": "generated", "key": key, "agent_id": agent_id}
    
    def validate_key(self, key):
        """Validate an API key."""
        if key not in self.keys["keys"]:
            return {"valid": False, "reason": "key not found"}
        
        key_data = self.keys["keys"][key]
        
        if not key_data.get("active", True):
            return {"valid": False, "reason": "key disabled"}
        
        # Check expiration
        expires = datetime.fromisoformat(key_data["expires_at"])
        if datetime.utcnow() > expires:
            return {"valid": False, "reason": "key expired"}
        
        return {"valid": True, "agent_id": key_data["agent_id"]}
    
    def revoke_key(self, key):
        """Revoke an API key."""
        if key in self.keys["keys"]:
            self.keys["keys"][key]["active"] = False
            self._save_keys()
            return {"status": "revoked"}
        return {"error": "key not found"}
    
    def list_keys(self, agent_id=None):
        """List API keys."""
        keys = list(self.keys["keys"].values())
        if agent_id:
            keys = [k for k in keys if k["agent_id"] == agent_id]
        return keys


def main():
    import sys
    manager = APIKeyManager()
    
    if len(sys.argv) < 2:
        print("Agent API Key Manager")
        print("Usage: api-key-manager.py <command> [args]")
        print("Commands:")
        print("  generate <agent_id> <name> [days]")
        print("  validate <key>")
        print("  revoke <key>")
        print("  list [agent_id]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "generate":
        if len(sys.argv) < 4:
            print("Usage: generate <agent_id> <name> [days]")
            return
        days = int(sys.argv[4]) if len(sys.argv) > 4 else 30
        result = manager.generate_key(sys.argv[2], sys.argv[3], days)
        print(json.dumps(result, indent=2))
    
    elif cmd == "validate":
        if len(sys.argv) < 3:
            print("Usage: validate <key>")
            return
        result = manager.validate_key(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "revoke":
        if len(sys.argv) < 3:
            print("Usage: revoke <key>")
            return
        result = manager.revoke_key(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "list":
        agent_id = sys.argv[2] if len(sys.argv) > 2 else None
        result = manager.list_keys(agent_id)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()