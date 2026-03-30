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

    def recommend(self, agent_id: str, limit: int = 5) -> list:
        """Recommend collaborations or tools for an agent"""
        recommendations = []
        
        # Get all agents
        all_agents = self.get_nodes_by_type("agent")
        for a in all_agents:
            if a['id'] == agent_id:
                continue
            # Find connections they have
            a_edges = self.get_edges_from(a['id'])
            for edge in a_edges:
                if edge['type'] == 'uses':
                    target = self.get_node(edge['target'])
                    if target and target['type'] == 'tool':
                        recommendations.append({
                            'type': 'tool',
                            'name': target.get('name'),
                            'reason': f"similar agent uses this"
                        })
        
        # Deduplicate
        seen = set()
        unique = []
        for r in recommendations:
            if r['name'] not in seen:
                seen.add(r['name'])
                unique.append(r)
        
        return unique[:limit]

    
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



    # === Query Optimization ===
    
    _query_cache = {}
    _cache_ttl = 60
    
    def clear_cache(self):
        self._query_cache = {}
    
    def _get_cached(self, key: str):
        if key in self._query_cache:
            result, timestamp = self._query_cache[key]
            if (datetime.utcnow() - datetime.fromisoformat(timestamp)).total_seconds() < self._cache_ttl:
                return result
        return None
    
    def _set_cached(self, key: str, value):
        self._query_cache[key] = (value, datetime.utcnow().isoformat())
    
    def query_fast(self, node_type: str = None, name_contains: str = None, limit: int = 100) -> list:
        cache_key = f"fast_{node_type}_{name_contains}_{limit}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        query = "SELECT * FROM nodes WHERE 1=1"
        params = []
        if node_type:
            query += " AND type = ?"
            params.append(node_type)
        if name_contains:
            query += " AND name LIKE ?"
            params.append(f"%{name_contains}%")
        query += f" LIMIT {limit}"
        
        rows = self.conn.execute(query, params).fetchall()
        results = [dict(row) for row in rows]
        self._set_cached(cache_key, results)
        return results
    
    def query_edges_fast(self, source: str = None, target: str = None, edge_type: str = None, limit: int = 200) -> list:
        cache_key = f"edges_{source}_{target}_{edge_type}_{limit}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        query = "SELECT * FROM edges WHERE 1=1"
        params = []
        if source:
            query += " AND source = ?"
            params.append(source)
        if target:
            query += " AND target = ?"
            params.append(target)
        if edge_type:
            query += " AND edge_type = ?"
            params.append(edge_type)
        query += f" LIMIT {limit}"
        
        rows = self.conn.execute(query, params).fetchall()
        results = [dict(row) for row in rows]
        self._set_cached(cache_key, results)
        return results
    
    def batch_get_nodes(self, node_ids: list) -> dict:
        if not node_ids:
            return {}
        placeholders = ",".join(["?" for _ in node_ids])
        query = f"SELECT * FROM nodes WHERE id IN ({placeholders})"
        rows = self.conn.execute(query, node_ids).fetchall()
        return {row["id"]: dict(row) for row in rows}
    
    def get_neighbors_fast(self, node_id: str, edge_types: list = None, max_depth: int = 1) -> list:
        if max_depth == 1:
            if edge_types:
                placeholders = ",".join(["?" for _ in edge_types])
                query = f"SELECT n.*, e.edge_type, e.id as edge_id FROM nodes n JOIN edges e ON (n.id = e.source OR n.id = e.target) WHERE (e.source = ? OR e.target = ?) AND e.edge_type IN ({placeholders}) AND n.id != ?"
                params = [node_id, node_id] + edge_types + [node_id]
            else:
                query = "SELECT n.*, e.edge_type, e.id as edge_id FROM nodes n JOIN edges e ON (n.id = e.source OR n.id = e.target) WHERE (e.source = ? OR e.target = ?) AND n.id != ?"
                params = [node_id, node_id, node_id]
            rows = self.conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
        return self.traverse(node_id, None, None, max_depth)
    
    def count_edges_by_type(self) -> dict:
        cache_key = "edge_type_counts"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        query = "SELECT edge_type, COUNT(*) as count FROM edges GROUP BY edge_type ORDER BY count DESC"
        rows = self.conn.execute(query).fetchall()
        result = {row["edge_type"]: row["count"] for row in rows}
        self._set_cached(cache_key, result)
        return result
    
    def get_popular_nodes(self, node_type: str = None, min_edges: int = 2, limit: int = 20) -> list:
        query = "SELECT n.*, COUNT(e.id) as edge_count FROM nodes n LEFT JOIN edges e ON (n.id = e.source OR n.id = e.target)"
        params = []
        if node_type:
            query += " WHERE n.type = ?"
            params.append(node_type)
        query += " GROUP BY n.id HAVING edge_count >= ? ORDER BY edge_count DESC LIMIT ?"
        params.extend([min_edges, limit])
        rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    
    def close(self):
        if self.conn:
            self.conn.close()

    def find_shortest_path(self, source_id: str, target_id: str) -> list:
        """BFS shortest path between two nodes"""
        from collections import deque
        
        visited = set()
        queue = deque([(source_id, [source_id])])
        
        while queue:
            node_id, path = queue.popleft()
            
            if node_id == target_id:
                return path
            
            if node_id in visited:
                continue
            visited.add(node_id)
            
            # Get all connected nodes
            edges = self.get_edges_from(node_id) + self.get_edges_to(node_id)
            for edge in edges:
                neighbor = edge.get("target") if edge.get("source") == node_id else edge.get("source")
                if neighbor and neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
        
        return []  # No path found

    def get_connected_nodes(self, node_id: str, max_depth: int = 2) -> dict:
        """Get nodes connected within N hops"""
        from collections import deque
        
        visited = {node_id: 0}
        queue = deque([(node_id, 0)])
        
        while queue:
            current, depth = queue.popleft()
            if depth >= max_depth:
                continue
            
            edges = self.get_edges_from(current) + self.get_edges_to(current)
            for edge in edges:
                neighbor = edge.get("target") if edge.get("source") == current else edge.get("source")
                if neighbor and neighbor not in visited:
                    visited[neighbor] = depth + 1
                    queue.append((neighbor, depth + 1))
        
        return visited

    def analyze_clustering(self, node_type: str = None) -> dict:
        """Analyze graph clustering"""
        # Get nodes
        if node_type:
            nodes = self.get_nodes_by_type(node_type)
        else:
            nodes = self.get_nodes()
        
        node_ids = [n["id"] for n in nodes]
        
        # Count edges within cluster
        internal_edges = 0
        for node_id in node_ids:
            edges = self.get_edges_from(node_id)
            internal_edges += sum(1 for e in edges if e.get("target") in node_ids)
        
        total_possible = len(nodes) * (len(nodes) - 1)
        clustering = internal_edges / total_possible if total_possible > 0 else 0
        
        return {
            "node_count": len(nodes),
            "internal_edges": internal_edges,
            "clustering_coefficient": clustering,
            "density": internal_edges / len(nodes) if len(nodes) > 0 else 0
        }

    def suggest_similar(self, node_id: str, limit: int = 5) -> list:
        """Find nodes similar to given node"""
        node = self.get_node(node_id)
        if not node:
            return []
        
        similar_type = self.get_nodes_by_type(node["type"])
        similar = []
        
        for n in similar_type:
            if n["id"] == node_id:
                continue
            score = 0
            # Name similarity
            if n.get("name") and node.get("name"):
                common_words = set(str(n["name"]).lower().split()) & set(str(node["name"]).lower().split())
                score += len(common_words)
            # Connected to same nodes
            my_connections = set(e.get("target") for e in self.get_edges_from(node_id))
            their_connections = set(e.get("target") for e in self.get_edges_from(n["id"]))
            score += len(my_connections & their_connections)
            
            if score > 0:
                similar.append((n, score))
        
        similar.sort(key=lambda x: -x[1])
        return [s[0] for s in similar[:limit]]


    def benchmark_queries(self, iterations=100) -> dict:
        """Benchmark query performance"""
        import time
        
        results = {}
        queries = [
            ("get_all_nodes", lambda: self.get_nodes()),
            ("count_by_type", lambda: self.count_by_type()),
            ("get_nodes_by_type_agent", lambda: self.get_nodes_by_type("agent")),
            ("get_nodes_by_type_tool", lambda: self.get_nodes_by_type("tool")),
            ("get_nodes_by_type_insight", lambda: self.get_nodes_by_type("insight")),
            ("traverse_2_steps", lambda: self.traverse(None, "uses", max_depth=2)),
        ]
        
        for name, fn in queries:
            times = []
            for _ in range(iterations):
                start = time.time()
                try:
                    fn()
                    times.append((time.time() - start) * 1000)
                except:
                    pass
            
            if times:
                results[name] = {
                    "min": min(times),
                    "max": max(times),
                    "avg": sum(times) / len(times),
                    "iterations": len(times)
                }
        
        return results
    
    def get_subgraph(self, node_ids: list, depth: int = 1) -> dict:
        """Get subgraph containing specific nodes and their neighbors"""
        nodes = []
        edges = []
        
        for node_id in node_ids:
            node = self.get_node(node_id)
            if node:
                nodes.append(node)
                
                # Get edges
                for edge in self.get_edges_from(node_id):
                    edges.append(edge)
                for edge in self.get_edges_to(node_id):
                    edges.append(edge)
                
                # Get neighbor nodes
                if depth > 1:
                    for edge in edges:
                        neighbor = self.get_node(edge.get("target") or edge.get("target_id"))
                        if neighbor and neighbor not in nodes:
                            nodes.append(neighbor)
        
        return {"nodes": nodes, "edges": edges}
    
    def similarity(self, node_id1: str, node_id2: str) -> float:
        """Calculate similarity between two nodes based on shared connections"""
        n1_edges = set()
        for e in self.get_edges_from(node_id1) + self.get_edges_to(node_id1):
            n1_edges.add(e.get("source") or e.get("source_id"))
            n1_edges.add(e.get("target") or e.get("target_id"))
        
        n2_edges = set()
        for e in self.get_edges_from(node_id2) + self.get_edges_to(node_id2):
            n2_edges.add(e.get("source") or e.get("source_id"))
            n2_edges.add(e.get("target") or e.get("target_id"))
        
        if not n1_edges or not n2_edges:
            return 0.0
        
        intersection = len(n1_edges & n2_edges)
        union = len(n1_edges | n2_edges)
        
        return intersection / union if union > 0 else 0.0
    
    def recommend_similar(self, node_id: str, limit: int = 5) -> list:
        """Recommend similar nodes based on connection patterns"""
        node = self.get_node(node_id)
        if not node:
            return []
        
        candidates = []
        # Get all nodes by iterating types
        all_nodes = []
        for node_type in self.count_by_type().keys():
            all_nodes.extend(self.get_nodes_by_type(node_type))
        
        for candidate in all_nodes:
            if candidate["id"] != node_id:
                sim = self.similarity(node_id, candidate["id"])
                if sim > 0:
                    candidates.append((candidate, sim))
        
        candidates.sort(key=lambda x: -x[1])
        return [{"node": c[0], "similarity": c[1]} for c in candidates[:limit]]
