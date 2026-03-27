#!/usr/bin/env python3
"""
Agent Hub Knowledge Graph Engine
A functional graph database for agent networks
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Any, Optional
import uuid
import re

DB_PATH = Path("/root/.openclaw/workspace/agent-hub/data/graph.db")

class KnowledgeGraph:
    """Graph database with nodes, edges, and query engine"""
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or DB_PATH
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        # Nodes table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                name TEXT,
                properties TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # Edges table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                target TEXT NOT NULL,
                edge_type TEXT NOT NULL,
                properties TEXT,
                created_at TEXT,
                FOREIGN KEY (source) REFERENCES nodes(id),
                FOREIGN KEY (target) REFERENCES nodes(id)
            )
        """)
        
        # Indexes
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_nodes_name ON nodes(name)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_type ON edges(edge_type)")
        
        self.conn.commit()
    
    # === Node Operations ===
    
    def create_node(self, node_type: str, name: str = None, properties: dict = None) -> dict:
        """Create a new node"""
        node_id = str(uuid.uuid4())[:12]
        now = datetime.utcnow().isoformat()
        
        self.conn.execute(
            "INSERT INTO nodes (id, type, name, properties, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (node_id, node_type, name, json.dumps(properties or {}), now, now)
        )
        self.conn.commit()
        
        return self.get_node(node_id)
    
    def get_node(self, node_id: str) -> Optional[dict]:
        """Get node by ID"""
        cursor = self.conn.execute(
            "SELECT * FROM nodes WHERE id = ?", (node_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        
        return self._row_to_node(row)
    
    def get_nodes_by_type(self, node_type: str) -> list:
        """Get all nodes of a type"""
        cursor = self.conn.execute(
            "SELECT * FROM nodes WHERE type = ?", (node_type,)
        )
        return [self._row_to_node(row) for row in cursor.fetchall()]
    
    def get_nodes_by_name(self, name: str) -> list:
        """Get nodes by name (exact match)"""
        cursor = self.conn.execute(
            "SELECT * FROM nodes WHERE name = ?", (name,)
        )
        return [self._row_to_node(row) for row in cursor.fetchall()]
    
    def update_node(self, node_id: str, properties: dict = None) -> Optional[dict]:
        """Update node properties"""
        now = datetime.utcnow().isoformat()
        
        if properties:
            # Merge with existing
            node = self.get_node(node_id)
            if not node:
                return None
            existing = node.get('properties', {})
            existing.update(properties)
            properties = existing
            
            self.conn.execute(
                "UPDATE nodes SET properties = ?, updated_at = ? WHERE id = ?",
                (json.dumps(properties), now, node_id)
            )
            self.conn.commit()
        
        return self.get_node(node_id)
    
    def delete_node(self, node_id: str) -> bool:
        """Delete node and all connected edges"""
        self.conn.execute("DELETE FROM edges WHERE source = ? OR target = ?", (node_id, node_id))
        self.conn.execute("DELETE FROM nodes WHERE id = ?", (node_id,))
        self.conn.commit()
        return True
    
    def _row_to_node(self, row: sqlite3.Row) -> dict:
        """Convert database row to node dict"""
        return {
            'id': row['id'],
            'type': row['type'],
            'name': row['name'],
            'properties': json.loads(row['properties'] or '{}'),
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
    
    # === Edge Operations ===
    
    def create_edge(self, source: str, target: str, edge_type: str, properties: dict = None) -> dict:
        """Create an edge between nodes"""
        # Verify nodes exist
        if not self.get_node(source) or not self.get_node(target):
            raise ValueError("Source or target node not found")
        
        edge_id = str(uuid.uuid4())[:12]
        now = datetime.utcnow().isoformat()
        
        self.conn.execute(
            "INSERT INTO edges (id, source, target, edge_type, properties, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (edge_id, source, target, edge_type, json.dumps(properties or {}), now)
        )
        self.conn.commit()
        
        return self.get_edge(edge_id)
    
    def get_edge(self, edge_id: str) -> Optional[dict]:
        """Get edge by ID"""
        cursor = self.conn.execute(
            "SELECT * FROM edges WHERE id = ?", (edge_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        
        return self._row_to_edge(row)
    
    def get_edges_from(self, node_id: str) -> list:
        """Get all edges from a node"""
        cursor = self.conn.execute(
            "SELECT * FROM edges WHERE source = ?", (node_id,)
        )
        return [self._row_to_edge(row) for row in cursor.fetchall()]
    
    def get_edges_to(self, node_id: str) -> list:
        """Get all edges to a node"""
        cursor = self.conn.execute(
            "SELECT * FROM edges WHERE target = ?", (node_id,)
        )
        return [self._row_to_edge(row) for row in cursor.fetchall()]
    
    def get_edges_by_type(self, edge_type: str) -> list:
        """Get all edges of a type"""
        cursor = self.conn.execute(
            "SELECT * FROM edges WHERE edge_type = ?", (edge_type,)
        )
        return [self._row_to_edge(row) for row in cursor.fetchall()]
    
    def delete_edge(self, edge_id: str) -> bool:
        """Delete an edge"""
        self.conn.execute("DELETE FROM edges WHERE id = ?", (edge_id,))
        self.conn.commit()
        return True
    
    def _row_to_edge(self, row: sqlite3.Row) -> dict:
        """Convert database row to edge dict"""
        return {
            'id': row['id'],
            'source': row['source'],
            'target': row['target'],
            'type': row['edge_type'],
            'properties': json.loads(row['properties'] or '{}'),
            'created_at': row['created_at']
        }
    
    # === Query Engine ===
    
    def query(self, query_str: str) -> list:
        """
        Execute a GQL-like query
        
        Examples:
          MATCH (a:Agent) RETURN a
          MATCH (a:Agent)-[:HAS_SKILL]->(s:Skill) WHERE s.name = 'Python' RETURN a
          MATCH (a:Agent)-[:COLLABORATES]->(b:Agent) RETURN a, b
        """
        # Parse simple queries
        query_str = query_str.strip()
        
        # Handle MATCH patterns
        if query_str.startswith("MATCH"):
            return self._execute_match(query_str)
        
        # Simple type queries
        if query_str.startswith("Nodes:"):
            node_type = query_str.split(":")[1].strip()
            return self.get_nodes_by_type(node_type)
        
        return []
    
    def _execute_match(self, query: str) -> list:
        """Execute a MATCH query"""
        # Extract pattern and return clause
        match_part = re.search(r'MATCH\s+\(([^)]+)\)(.*?)RETURN', query)
        if not match_part:
            return []
        
        pattern = match_part.group(1).strip()
        rest = match_part.group(2)
        
        # Simple case: single node
        if '-' not in pattern and ')-' not in pattern:
            # (name:type {props})
            node_match = re.match(r'(\w+)?:?(\w+)', pattern)
            if node_match:
                node_type = node_match.group(2)
                return self.get_nodes_by_type(node_type)
        
        # Edge traversal pattern
        if ')-' in pattern and '->' in pattern:
            # (a:Type)-[:EDGE_TYPE]->(b:Type)
            match = re.search(r'\((\w+)?:?(\w+)\)-(\[:\w+\])->\((\w+)?:?(\w+)\)', pattern)
            if match:
                source_type = match.group(2)
                edge_type = match.group(3).strip('[]')
                target_type = match.group(5)
                
                return self.traverse(source_type, edge_type, target_type)
        
        return []
    
    def traverse(self, source_type: str, edge_type: str, target_type: str = None, max_depth: int = 3) -> list:
        """Traverse graph from source to target"""
        results = []
        
        # Get all source nodes
        sources = self.get_nodes_by_type(source_type)
        
        for source in sources:
            visited = set()
            queue = [(source['id'], 0)]
            
            while queue:
                node_id, depth = queue.pop(0)
                
                if node_id in visited or depth > max_depth:
                    continue
                visited.add(node_id)
                
                # Get outgoing edges
                edges = self.get_edges_from(node_id)
                
                for edge in edges:
                    if edge['type'] == edge_type:
                        target_node = self.get_node(edge['target'])
                        
                        if target_node:
                            if target_type is None or target_node['type'] == target_type:
                                results.append({
                                    'source': source,
                                    'edge': edge,
                                    'target': target_node
                                })
                            
                            queue.append((edge['target'], depth + 1))
        
        return results
    
    # === Aggregation ===
    
    def count_by_type(self) -> dict:
        """Count nodes by type"""
        cursor = self.conn.execute(
            "SELECT type, COUNT(*) as count FROM nodes GROUP BY type"
        )
        return {row['type']: row['count'] for row in cursor.fetchall()}
    
    def count_edges_by_type(self) -> dict:
        """Count edges by type"""
        cursor = self.conn.execute(
            "SELECT edge_type, COUNT(*) as count FROM edges GROUP BY edge_type"
        )
        return {row['edge_type']: row['count'] for row in cursor.fetchall()}
    
    def stats(self) -> dict:
        """Get graph statistics"""
        node_count = self.conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        edge_count = self.conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        
        return {
            'nodes': node_count,
            'edges': edge_count,
            'node_types': self.count_by_type(),
            'edge_types': self.count_edges_by_type()
        }
    
    # === Bulk Operations ===
    
    def import_json(self, data: dict):
        """Import graph from JSON"""
        # Import nodes
        for node in data.get('nodes', []):
            now = datetime.utcnow().isoformat()
            self.conn.execute(
                "INSERT OR REPLACE INTO nodes (id, type, name, properties, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (node.get('id', str(uuid.uuid4())[:12]), 
                 node.get('type', 'unknown'),
                 node.get('name'),
                 json.dumps(node.get('properties', {})),
                 now, now)
            )
        
        # Import edges
        for edge in data.get('edges', []):
            now = datetime.utcnow().isoformat()
            self.conn.execute(
                "INSERT OR REPLACE INTO edges (id, source, target, edge_type, properties, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (edge.get('id', str(uuid.uuid4())[:12]),
                 edge['source'],
                 edge['target'],
                 edge.get('type', 'related'),
                 json.dumps(edge.get('properties', {})),
                 now)
            )
        
        self.conn.commit()
    
    def export_json(self) -> dict:
        """Export graph to JSON"""
        nodes = [dict(row) for row in self.conn.execute("SELECT * FROM nodes").fetchall()]
        edges = [dict(row) for row in self.conn.execute("SELECT * FROM edges").fetchall()]
        
        # Clean up
        for n in nodes:
            del n['rowid']
        for e in edges:
            del e['rowid']
        
        return {'nodes': nodes, 'edges': edges}
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# === CLI Interface ===

def main():
    import sys
    g = KnowledgeGraph()
    
    if len(sys.argv) < 2:
        print("Usage: kge <command> [args]")
        print()
        print("Commands:")
        print("  create-node <type> [name]       Create a node")
        print("  get-node <id>                   Get node by ID")
        print("  nodes <type>                    List nodes by type")
        print("  create-edge <src> <dst> <type>  Create edge")
        print("  traverse <src_type> <edge_type> [target_type]  Traverse graph")
        print("  query <gql>                     Execute GQL query")
        print("  stats                           Show graph statistics")
        print("  import <file>                   Import from JSON")
        print("  export                          Export to JSON")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "create-node":
        node_type = sys.argv[2]
        name = sys.argv[3] if len(sys.argv) > 3 else None
        node = g.create_node(node_type, name)
        print(json.dumps(node, indent=2))
    
    elif cmd == "get-node":
        node = g.get_node(sys.argv[2])
        print(json.dumps(node, indent=2))
    
    elif cmd == "nodes":
        nodes = g.get_nodes_by_type(sys.argv[2])
        print(json.dumps(nodes, indent=2))
    
    elif cmd == "create-edge":
        edge = g.create_edge(sys.argv[2], sys.argv[3], sys.argv[4])
        print(json.dumps(edge, indent=2))
    
    elif cmd == "traverse":
        source_type = sys.argv[2]
        edge_type = sys.argv[3]
        target_type = sys.argv[4] if len(sys.argv) > 4 else None
        results = g.traverse(source_type, edge_type, target_type)
        print(json.dumps(results, indent=2))
    
    elif cmd == "query":
        results = g.query(" ".join(sys.argv[2:]))
        print(json.dumps(results, indent=2))
    
    elif cmd == "stats":
        print(json.dumps(g.stats(), indent=2))
    
    elif cmd == "import":
        with open(sys.argv[2]) as f:
            data = json.load(f)
        g.import_json(data)
        print("Imported successfully")
    
    elif cmd == "export":
        print(json.dumps(g.export_json(), indent=2))
    
    else:
        print(f"Unknown command: {cmd}")
    
    g.close()


if __name__ == "__main__":
    main()
