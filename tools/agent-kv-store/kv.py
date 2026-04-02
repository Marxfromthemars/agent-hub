#!/usr/bin/env python3
"""
Agent Key-Value Store
Simple KV store for agent data.
"""

import json
from datetime import datetime
from pathlib import Path

class KVStore:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.store_file = self.data_dir / "kv_store.json"
        self.store = self._load_store()
    
    def _load_store(self):
        if self.store_file.exists():
            with open(self.store_file) as f:
                return json.load(f)
        return {"data": {}}
    
    def _save_store(self):
        with open(self.store_file, 'w') as f:
            json.dump(self.store, f, indent=2)
    
    def set(self, key, value):
        """Set a value."""
        self.store["data"][key] = {"value": value, "updated": datetime.utcnow().isoformat()}
        self._save_store()
        return {"status": "set", "key": key}
    
    def get(self, key):
        """Get a value."""
        if key in self.store["data"]:
            return {"key": key, "value": self.store["data"][key]["value"]}
        return {"error": "not found"}
    
    def delete(self, key):
        """Delete a key."""
        if key in self.store["data"]:
            del self.store["data"][key]
            self._save_store()
            return {"status": "deleted"}
        return {"error": "not found"}
    
    def list_keys(self, prefix=None):
        """List keys."""
        keys = list(self.store["data"].keys())
        if prefix:
            keys = [k for k in keys if k.startswith(prefix)]
        return {"keys": keys}


def main():
    import sys
    kv = KVStore()
    
    if len(sys.argv) < 2:
        print("Agent KV Store")
        print("Usage: kv-store.py <command> [args]")
        print("Commands:")
        print("  set <key> <value>")
        print("  get <key>")
        print("  delete <key>")
        print("  list [prefix]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "set":
        if len(sys.argv) < 4:
            print("Usage: set <key> <value>")
            return
        result = kv.set(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))
    
    elif cmd == "get":
        if len(sys.argv) < 3:
            print("Usage: get <key>")
            return
        result = kv.get(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "delete":
        if len(sys.argv) < 3:
            print("Usage: delete <key>")
            return
        result = kv.delete(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "list":
        prefix = sys.argv[2] if len(sys.argv) > 2 else None
        result = kv.list_keys(prefix)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()