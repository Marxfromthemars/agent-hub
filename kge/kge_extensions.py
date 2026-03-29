#!/usr/bin/env python3
"""KGE Extensions - Graph algorithms for the Knowledge Graph Engine"""

def find_shortest_path(self, source_id: str, target_id: str, max_depth: int = 10) -> list:
    """Find shortest path between two nodes (BFS)"""
    if source_id == target_id:
        return [source_id]
    
    visited = {source_id}
    queue = [(source_id, [source_id])]
    
    while queue:
        current, path = queue.pop(0)
        
        # Get all outgoing edges
        edges = self.get_edges_from(current)
        for edge in edges:
            neighbor = edge["target"]
            
            if neighbor == target_id:
                return path + [neighbor]
            
            if neighbor not in visited and len(path) < max_depth:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
        
        # Also check incoming edges
        in_edges = self.get_edges_to(current)
        for edge in in_edges:
            neighbor = edge["source"]
            
            if neighbor == target_id:
                return path + [neighbor]
            
            if neighbor not in visited and len(path) < max_depth:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return []  # No path found


def find_connected_components(self) -> list:
    """Find all connected components in the graph"""
    visited = set()
    components = []
    
    nodes = self.conn.execute("SELECT id FROM nodes").fetchall()
    for row in nodes:
        node_id = row["id"]
        
        if node_id not in visited:
            component = set()
            queue = [node_id]
            
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                
                visited.add(current)
                component.add(current)
                
                # Add neighbors
                for edge in self.get_edges_from(current):
                    if edge["target"] not in visited:
                        queue.append(edge["target"])
                for edge in self.get_edges_to(current):
                    if edge["source"] not in visited:
                        queue.append(edge["source"])
            
            components.append(list(component))
    
    return components


def get_node_importance(self, node_id: str) -> float:
    """Calculate simple importance score based on connections"""
    in_edges = len(self.get_edges_to(node_id))
    out_edges = len(self.get_edges_from(node_id))
    
    # Simple importance = total connections
    return (in_edges + out_edges) * 1.0


def find_hubs_and_authorities(self, limit: int = 10) -> dict:
    """Find hub and authority nodes (simplified HITS algorithm)"""
    nodes = self.conn.execute("SELECT id, name FROM nodes").fetchall()
    node_list = [row["id"] for row in nodes]
    
    if not node_list:
        return {"hubs": [], "authorities": []}
    
    # Initialize scores
    hub_scores = {n: 1.0 for n in node_list}
    auth_scores = {n: 1.0 for n in node_list}
    
    # Run a few iterations
    for _ in range(5):
        # Update auth scores (incoming edges)
        new_auth = {}
        for node in node_list:
            in_edges = self.get_edges_to(node)
            score = sum(hub_scores.get(e["source"], 1.0) for e in in_edges)
            new_auth[node] = score or 1.0
        
        # Normalize
        max_auth = max(new_auth.values()) or 1
        auth_scores = {n: s/max_auth for n, s in new_auth.items()}
        
        # Update hub scores (outgoing edges)
        new_hub = {}
        for node in node_list:
            out_edges = self.get_edges_from(node)
            score = sum(auth_scores.get(e["target"], 1.0) for e in out_edges)
            new_hub[node] = score or 1.0
        
        # Normalize
        max_hub = max(new_hub.values()) or 1
        hub_scores = {n: s/max_hub for n, s in new_hub.items()}
    
    # Sort and return top N
    hub_sorted = sorted(hub_scores.items(), key=lambda x: -x[1])[:limit]
    auth_sorted = sorted(auth_scores.items(), key=lambda x: -x[1])[:limit]
    
    return {
        "hubs": [{"id": h[0], "score": h[1]} for h in hub_sorted],
        "authorities": [{"id": a[0], "score": a[1]} for a in auth_sorted]
    }


def find_similar_nodes(self, node_id: str, limit: int = 5) -> list:
    """Find nodes similar to given node based on shared neighbors"""
    node = self.get_node(node_id)
    if not node:
        return []
    
    # Get all neighbors (both directions)
    neighbors = set()
    for edge in self.get_edges_from(node_id):
        neighbors.add(edge["target"])
    for edge in self.get_edges_to(node_id):
        neighbors.add(edge["source"])
    
    # Get neighbors of neighbors (2nd degree)
    similar_scores = {}
    for neighbor in neighbors:
        for edge in self.get_edges_from(neighbor):
            if edge["target"] != node_id and edge["target"] not in neighbors:
                similar_scores[edge["target"]] = similar_scores.get(edge["target"], 0) + 2
        for edge in self.get_edges_to(neighbor):
            if edge["source"] != node_id and edge["source"] not in neighbors:
                similar_scores[edge["source"]] = similar_scores.get(edge["source"], 0) + 2
    
    # Sort by score
    sorted_similar = sorted(similar_scores.items(), key=lambda x: -x[1])[:limit]
    results = []
    for nid, score in sorted_similar:
        n = self.get_node(nid)
        if n:
            n["similarity_score"] = score
            results.append(n)
    
    return results


def recommend_connections(self, node_id: str, limit: int = 5) -> list:
    """Recommend potential connections for a node"""
    recommendations = []
    
    node = self.get_node(node_id)
    if not node:
        return []
    
    # Get direct neighbors
    direct_neighbors = set()
    for edge in self.get_edges_from(node_id):
        direct_neighbors.add(edge["target"])
    for edge in self.get_edges_to(node_id):
        direct_neighbors.add(edge["source"])
    
    # Find nodes that are friends-of-friends
    fof_scores = {}
    for neighbor in direct_neighbors:
        for edge in self.get_edges_from(neighbor):
            if edge["target"] not in direct_neighbors and edge["target"] != node_id:
                fof_scores[edge["target"]] = fof_scores.get(edge["target"], 0) + 1
        for edge in self.get_edges_to(neighbor):
            if edge["source"] not in direct_neighbors and edge["source"] != node_id:
                fof_scores[edge["source"]] = fof_scores.get(edge["source"], 0) + 1
    
    # Sort and return top recommendations
    sorted_recs = sorted(fof_scores.items(), key=lambda x: -x[1])[:limit]
    for nid, score in sorted_recs:
        n = self.get_node(nid)
        if n:
            recommendations.append({
                "node": n,
                "common_connections": score
            })
    
    return recommendations


def get_graph_summary(self) -> dict:
    """Get comprehensive graph summary"""
    components = find_connected_components(self)
    stats = self.stats()
    
    return {
        "total_nodes": stats.get("nodes", 0),
        "total_edges": stats.get("edges", 0),
        "node_types": stats.get("node_types", {}),
        "edge_types": stats.get("edge_types", {}),
        "connected_components": len(components),
        "largest_component": max(len(c) for c in components) if components else 0,
        "avg_degree": stats.get("edges", 0) / max(1, stats.get("nodes", 1))
    }


def run_kge_demo():
    """Demo the KGE capabilities"""
    import sys
    sys.path.insert(0, str(__file__).rsplit('/', 1)[0])
    from engine import KnowledgeGraph
    
    kg = KnowledgeGraph()
    
    print("=== Knowledge Graph Engine Demo ===\n")
    
    # Add sample data
    agents = ["marxagent", "researcher", "builder", "planner"]
    tools = ["code-gen", "research", "deploy", "test"]
    
    for agent in agents:
        kg.create_node("agent", agent, {"role": agent.split("-")[0]})
    
    for tool in tools:
        kg.create_node("tool", tool, {"category": "utility"})
    
    # Create edges
    kg.create_edge("marxagent", "planner", "manages")
    kg.create_edge("researcher", "planner", "reports_to")
    kg.create_edge("builder", "planner", "reports_to")
    kg.create_edge("marxagent", "code-gen", "uses")
    kg.create_edge("researcher", "research", "uses")
    kg.create_edge("builder", "deploy", "uses")
    
    print(f"Graph created: {kg.stats()['total_nodes']} nodes, {kg.stats()['total_edges']} edges\n")
    
    # Run algorithms
    print("=== Graph Summary ===")
    summary = get_graph_summary(kg)
    for k, v in summary.items():
        print(f"  {k}: {v}")
    
    print("\n=== Connected Components ===")
    comps = find_connected_components(kg)
    print(f"  Found {len(comps)} components")
    
    print("\n=== Hubs and Authorities ===")
    hubs_auths = find_hubs_and_authorities(kg)
    print(f"  Top hubs: {[h['id'] for h in hubs_auths['hubs'][:3]]}")
    print(f"  Top authorities: {[a['id'] for a in hubs_auths['authorities'][:3]]}")
    
    kg.close()
    print("\n✓ KGE Demo complete")


if __name__ == "__main__":
    run_kge_demo()