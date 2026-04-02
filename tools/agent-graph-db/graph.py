#!/usr/bin/env python3
"""
Agent Graph DB
Graph database operations for agent relationships.
"""

import json
from datetime import datetime
from pathlib import Path

class GraphDB:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.graph_file = self.data_dir / "graph_db.json"
        self.graph = self._load()
    
    def _load(self):
        if self.graph_file.exists():
            with open(self.graph_file) as f:
                return json.load(f)
        return {"nodes": {}, "edges": []}
    
    def _save(self):
        with open(self.graph_file, 'w') as f:
            json.dump(self.graph, f, indent=2)
    
    def add_node(self, node_id, labels, props=None):
        """Add a node."""
        self.graph["nodes"][node_id] = {"labels": labels, "props": props or {}}
        self._save()
        return {"status": "added", "node": node_id}
    
    def add_edge(self, from_id, to_id, rel_type):
        """Add an edge."""
        self.graph["edges"].append({"from": from_id, "to": to_id, "type": rel_type})
        self._save()
        return {"status": "added"}
    
    def query(self, label):
        """Query nodes by label."""
        results = [n for n, d in self.graph["nodes"].items() if label in d.get("labels", [])]
        return {"nodes": results}


def main():
    import sys
    gdb = GraphDB()
    
    if len(sys.argv) < 2:
        print("Usage: graph-db.py <command> [args]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "add-node":
        result = gdb.add_node(sys.argv[2], sys.argv[3].split(","))
        print(json.dumps(result))
    
    elif cmd == "add-edge":
        result = gdb.add_edge(sys.argv[2], sys.argv[3], sys.argv[4])
        print(json.dumps(result))
    
    elif cmd == "query":
        result = gdb.query(sys.argv[2])
        print(json.dumps(result))


if __name__ == "__main__":
    main()