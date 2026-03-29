#!/usr/bin/env python3
"""
Knowledge Graph Engine - Extensions
Advanced features: path finding, recommendations, visualization, semantic search
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Set
from collections import defaultdict
import heapq

# Import base class
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from kge.engine import KnowledgeGraph


class KGExtended(KnowledgeGraph):
    """Extended Knowledge Graph with advanced features"""
    
    # === PATH FINDING ===
    
    def shortest_path(self, source_id: str, target_id: str) -> Optional[List[Dict]]:
        """Find shortest path between two nodes using BFS"""
        if source_id == target_id:
            return [{"id": source_id, "type": "node"}]
        
        visited = {source_id}
        queue = [(source_id, [])]
        
        while queue:
            current, path = queue.pop(0)
            edges = self.get_edges_from(current)
            
            for edge in edges:
                target = edge['target']
                new_path = path + [{
                    "from": edge['source'],
                    "edge_type": edge['type'],
                    "to": target
                }]
                
                if target == target_id:
                    return self._path_to_nodes(source_id, new_path)
                
                if target not in visited:
                    visited.add(target)
                    queue.append((target, new_path))
        
        return None  # No path found
    
    def _path_to_nodes(self, start: str, path_edges: List[Dict]) -> List[Dict]:
        """Convert edge path to node list"""
        nodes = [{"id": start, "type": self.get_node(start).get("type", "unknown") if self.get_node(start) else "unknown"}]
        
        for edge in path_edges:
            target = self.get_node(edge['to'])
            if target:
                nodes.append({
                    "id": target['id'],
                    "type": target['type'],
                    "name": target.get('name'),
                    "via_edge": edge['edge_type']
                })
        
        return nodes
    
    def find_all_paths(self, source_id: str, target_id: str, max_depth: int = 5) -> List[List[str]]:
        """Find all paths between two nodes up to max_depth"""
        paths = []
        
        def dfs(current: str, target: str, path: List[str], depth: int):
            if depth > max_depth:
                return
            if current == target:
                paths.append(path.copy())
                return
            
            for edge in self.get_edges_from(current):
                if edge['target'] not in path:
                    path.append(edge['target'])
                    dfs(edge['target'], target, path, depth + 1)
                    path.pop()
        
        dfs(source_id, [source_id], target_id, 0)
        return paths
    
    # === CENTRALITY MEASURES ===
    
    def degree_centrality(self) -> Dict[str, float]:
        """Calculate degree centrality for all nodes"""
        degrees = defaultdict(int)
        
        all_edges = self.conn.execute("SELECT source, target FROM edges").fetchall()
        for edge in all_edges:
            degrees[edge['source']] += 1
            degrees[edge['target']] += 1
        
        n = self.conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        if n <= 1:
            return degrees
        
        # Normalize
        return {node_id: deg / (n - 1) for node_id, deg in degrees.items()}
    
    def betweenness_centrality(self) -> Dict[str, float]:
        """Calculate betweenness centrality (simplified)"""
        nodes = [row['id'] for row in self.conn.execute("SELECT id FROM nodes").fetchall()]
        betweenness = {n: 0.0 for n in nodes}
        
        # Sample-based for performance
        for source in nodes[:min(10, len(nodes))]:
            for target in nodes:
                if source != target:
                    path = self.shortest_path(source, target)
                    if path:
                        for node in path[1:-1]:
                            betweenness[node['id']] += 1
        
        # Normalize
        n = len(nodes)
        if n > 2:
            norm = 2 / ((n - 1) * (n - 2))
            betweenness = {k: v * norm for k, v in betweenness.items()}
        
        return betweenness
    
    def most_connected_nodes(self, limit: int = 10) -> List[Dict]:
        """Get most connected nodes"""
        centrality = self.degree_centrality()
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for node_id, score in sorted_nodes[:limit]:
            node = self.get_node(node_id)
            if node:
                results.append({
                    "id": node_id,
                    "name": node.get("name", node_id),
                    "type": node["type"],
                    "connections": int(score * (self.conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0] - 1)),
                    "centrality": round(score, 4)
                })
        
        return results
    
    # === RECOMMENDATIONS ===
    
    def suggest_related(self, node_id: str, limit: int = 5) -> List[Dict]:
        """Suggest related nodes (collaborators, similar tools, etc.)"""
        node = self.get_node(node_id)
        if not node:
            return []
        
        related = defaultdict(int)
        
        # Direct connections
        for edge in self.get_edges_from(node_id):
            related[edge['target']] += 3
        
        for edge in self.get_edges_to(node_id):
            related[edge['source']] += 3
        
        # Second-degree connections
        for edge in self.get_edges_from(node_id):
            for second in self.get_edges_from(edge['target']):
                if second['target'] != node_id:
                    related[second['target']] += 1
        
        # Sort by score and exclude self
        del related[node_id]
        sorted_related = sorted(related.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        results = []
        for related_id, score in sorted_related:
            related_node = self.get_node(related_id)
            if related_node:
                results.append({
                    "id": related_id,
                    "name": related_node.get("name", related_id),
                    "type": related_node["type"],
                    "relevance": score
                })
        
        return results
    
    def suggest_collaborators(self, node_id: str, limit: int = 5) -> List[Dict]:
        """Suggest potential collaborators based on shared projects/tools"""
        node = self.get_node(node_id)
        if not node:
            return []
        
        # Get what this node works on/uses
        interests = set()
        for edge in self.get_edges_from(node_id):
            interests.add(edge['target'])
        
        # Find other agents with similar interests
        collaborators = defaultdict(int)
        all_agents = self.get_nodes_by_type("agent")
        
        for agent in all_agents:
            if agent['id'] == node_id:
                continue
            
            agent_interests = set()
            for edge in self.get_edges_from(agent['id']):
                agent_interests.add(edge['target'])
            
            # Calculate overlap
            overlap = len(interests & agent_interests)
            if overlap > 0:
                collaborators[agent['id']] = overlap
        
        sorted_collabs = sorted(collaborators.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        results = []
        for collab_id, score in sorted_collabs:
            collab = self.get_node(collab_id)
            if collab:
                results.append({
                    "id": collab_id,
                    "name": collab.get("name", collab_id),
                    "shared_interests": score
                })
        
        return results
    
    # === SEMANTIC SEARCH ===
    
    def search_nodes(self, query: str, limit: int = 10) -> List[Dict]:
        """Search nodes by name or properties (simple text search)"""
        query_lower = query.lower()
        results = []
        
        # Search in names
        name_matches = self.conn.execute(
            "SELECT * FROM nodes WHERE LOWER(name) LIKE ? LIMIT ?",
            (f"%{query_lower}%", limit)
        ).fetchall()
        
        for row in name_matches:
            node = dict(row)
            node['match_type'] = 'name'
            results.append(node)
        
        # Search in properties
        all_nodes = self.conn.execute("SELECT * FROM nodes").fetchall()
        for row in all_nodes:
            if len(results) >= limit:
                break
            
            node = dict(row)
            if node['id'] in [r['id'] for r in results]:
                continue
            
            props = node.get('properties', '{}')
            if query_lower in props.lower():
                node['match_type'] = 'property'
                results.append(node)
        
        return results
    
    # === VISUALIZATION EXPORT ===
    
    def export_for_d3(self) -> Dict:
        """Export graph in D3.js force-directed graph format"""
        nodes = []
        links = []
        
        # Get all nodes
        for row in self.conn.execute("SELECT * FROM nodes").fetchall():
            node = dict(row)
            nodes.append({
                "id": node['id'],
                "name": node.get('name', node['id']),
                "type": node['type'],
                "group": self._type_to_group(node['type'])
            })
        
        # Get all edges
        for row in self.conn.execute("SELECT * FROM edges").fetchall():
            edge = dict(row)
            links.append({
                "source": edge['source'],
                "target": edge['target'],
                "type": edge['edge_type']
            })
        
        return {"nodes": nodes, "links": links}
    
    def _type_to_group(self, node_type: str) -> int:
        """Map node type to D3 group number"""
        groups = {
            "agent": 1,
            "project": 2,
            "tool": 3,
            "discovery": 4,
            "insight": 5,
            "company": 6
        }
        return groups.get(node_type, 0)
    
    def export_for_graphviz(self) -> str:
        """Export graph in Graphviz DOT format"""
        lines = ["digraph AgentHub {"]
        lines.append("  rankdir=LR;")
        lines.append("  node [shape=box];")
        
        # Nodes
        for row in self.conn.execute("SELECT * FROM nodes").fetchall():
            node = dict(row)
            name = node.get('name', node['id'])
            node_type = node['type']
            lines.append(f'  "{node["id"]}" [label="{name}" color={self._type_color(node_type)}];')
        
        # Edges
        lines.append("")
        for row in self.conn.execute("SELECT * FROM edges").fetchall():
            edge = dict(row)
            lines.append(f'  "{edge["source"]}" -> "{edge["target"]}" [label="{edge["edge_type"]}"];')
        
        lines.append("}")
        return "\n".join(lines)
    
    def _type_color(self, node_type: str) -> str:
        """Get color for node type"""
        colors = {
            "agent": "blue",
            "project": "green",
            "tool": "orange",
            "discovery": "purple",
            "insight": "red",
            "company": "gold"
        }
        return colors.get(node_type, "gray")
    
    # === GRAPH ANALYSIS ===
    
    def find_clusters(self) -> List[List[str]]:
        """Find connected components (simple clusters)"""
        visited = set()
        clusters = []
        
        all_nodes = [row['id'] for row in self.conn.execute("SELECT id FROM nodes").fetchall()]
        
        def dfs(node_id: str, cluster: List[str]):
            if node_id in visited:
                return
            visited.add(node_id)
            cluster.append(node_id)
            
            for edge in self.get_edges_from(node_id):
                dfs(edge['target'], cluster)
            for edge in self.get_edges_to(node_id):
                dfs(edge['source'], cluster)
        
        for node_id in all_nodes:
            if node_id not in visited:
                cluster = []
                dfs(node_id, cluster)
                if cluster:
                    clusters.append(cluster)
        
        return clusters
    
    def graph_density(self) -> float:
        """Calculate graph density (actual edges / possible edges)"""
        node_count = self.conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        edge_count = self.conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        
        if node_count <= 1:
            return 0.0
        
        max_edges = node_count * (node_count - 1)  # Directed graph
        return edge_count / max_edges if max_edges > 0 else 0.0
    
    def get_graph_summary(self) -> Dict:
        """Get comprehensive graph summary"""
        stats = self.stats()
        clusters = self.find_clusters()
        most_connected = self.most_connected_nodes(5)
        centrality = self.degree_centrality()
        
        # Top by centrality
        top_central = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "size": {
                "nodes": stats['nodes'],
                "edges": stats['edges'],
                "density": round(self.graph_density(), 4)
            },
            "types": {
                "node_types": stats['node_types'],
                "edge_types": stats['edge_types']
            },
            "structure": {
                "clusters": len(clusters),
                "largest_cluster": max(len(c) for c in clusters) if clusters else 0
            },
            "key_nodes": {
                "most_connected": most_connected,
                "highest_centrality": [{"id": k, "score": round(v, 4)} for k, v in top_central]
            }
        }


def run_kge_demo():
    """Run demonstration of KGE extended features"""
    print("""
╔══════════════════════════════════════════════════════════╗
║     KNOWLEDGE GRAPH ENGINE - DEMONSTRATION              ║
╚══════════════════════════════════════════════════════════╝
""")
    
    g = KGExtended()
    
    # Show stats
    stats = g.stats()
    print(f"📊 Graph Size: {stats['nodes']} nodes, {stats['edges']} edges")
    
    # Show node types
    print("\n📦 Node Types:")
    for t, c in stats['node_types'].items():
        print(f"   • {t}: {c}")
    
    # Show most connected
    print("\n🔗 Most Connected Nodes:")
    for node in g.most_connected_nodes(5):
        print(f"   • {node['name']} ({node['type']}): {node['connections']} connections")
    
    # Show clusters
    clusters = g.find_clusters()
    print(f"\n🔍 Clusters: {len(clusters)} found")
    for i, cluster in enumerate(clusters[:3]):
        print(f"   Cluster {i+1}: {len(cluster)} nodes")
    
    # Show recommendations
    agents = g.get_nodes_by_type("agent")
    if agents:
        print(f"\n🤝 Collaborator Recommendations for {agents[0].get('name', 'agent')}:")
        collabs = g.suggest_collaborators(agents[0]['id'], 3)
        for c in collabs:
            print(f"   • {c['name']} (shared: {c['shared_interests']})")
    
    print("\n✨ Demo complete!")
    g.close()


if __name__ == "__main__":
    run_kge_demo()