#!/usr/bin/env python3
"""
Agent Capability Matrix
Visualizes and analyzes agent capability coverage.
"""

import json
from datetime import datetime
from pathlib import Path

class CapabilityMatrix:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.matrix_file = self.data_dir / "capability_matrix.json"
        self.matrix = self._load_matrix()
    
    def _load_matrix(self):
        if self.matrix_file.exists():
            with open(self.matrix_file) as f:
                return json.load(f)
        return {"agents": {}, "capabilities": [], "matrix": []}
    
    def _save_matrix(self):
        with open(self.matrix_file, 'w') as f:
            json.dump(self.matrix, f, indent=2)
    
    def add_capability(self, capability):
        """Add a capability to the matrix."""
        if capability not in self.matrix["capabilities"]:
            self.matrix["capabilities"].append(capability)
            self._update_matrix()
        return {"status": "added", "capability": capability}
    
    def register_agent(self, agent_id, name, capabilities):
        """Register an agent with their capabilities."""
        self.matrix["agents"][agent_id] = {
            "name": name,
            "capabilities": capabilities,
            "updated": datetime.utcnow().isoformat()
        }
        self._update_matrix()
        return {"status": "registered", "agent_id": agent_id}
    
    def _update_matrix(self):
        """Update the capability matrix."""
        agents = self.matrix["agents"]
        caps = self.matrix["capabilities"]
        
        # Build matrix
        matrix = []
        for agent_id, agent_data in agents.items():
            row = {
                "agent_id": agent_id,
                "name": agent_data["name"],
                "capabilities": agent_data["capabilities"]
            }
            
            # Binary capability vector
            row["vector"] = [1 if c in agent_data["capabilities"] else 0 for c in caps]
            row["coverage"] = sum(row["vector"]) / len(caps) if caps else 0
            
            matrix.append(row)
        
        self.matrix["matrix"] = matrix
        self._save_matrix()
    
    def get_matrix(self):
        """Get the current capability matrix."""
        return self.matrix
    
    def analyze_coverage(self, required_capabilities):
        """Analyze coverage for required capabilities."""
        agents = self.matrix["agents"]
        coverage = []
        
        for agent_id, agent_data in agents.items():
            agent_caps = set(agent_data["capabilities"])
            required = set(required_capabilities)
            
            covered = agent_caps & required
            missing = required - agent_caps
            
            coverage.append({
                "agent_id": agent_id,
                "name": agent_data["name"],
                "covered": list(covered),
                "missing": list(missing),
                "coverage_rate": len(covered) / len(required) if required else 0
            })
        
        return coverage
    
    def find_complementary_pairs(self):
        """Find agent pairs with complementary capabilities."""
        agents = list(self.matrix["agents"].items())
        pairs = []
        
        for i, (id1, a1) in enumerate(agents):
            for id2, a2 in agents[i+1:]:
                caps1 = set(a1["capabilities"])
                caps2 = set(a2["capabilities"])
                
                overlap = len(caps1 & caps2)
                union = len(caps1 | caps2)
                
                if union > 0:
                    similarity = overlap / union
                    if similarity < 0.5:  # Complementary (low overlap)
                        pairs.append({
                            "agent_1": id1,
                            "agent_2": id2,
                            "shared": list(caps1 & caps2),
                            "unique_1": list(caps1 - caps2),
                            "unique_2": list(caps2 - caps1),
                            "complementarity": 1 - similarity
                        })
        
        return sorted(pairs, key=lambda x: x["complementarity"], reverse=True)
    
    def get_statistics(self):
        """Get matrix statistics."""
        matrix = self.matrix["matrix"]
        
        if not matrix:
            return {"agents": 0, "capabilities": 0, "avg_coverage": 0}
        
        total_caps = len(self.matrix["capabilities"])
        avg_coverage = sum(m["coverage"] for m in matrix) / len(matrix)
        
        # Most common capabilities
        cap_counts = {}
        for agent in self.matrix["agents"].values():
            for cap in agent["capabilities"]:
                cap_counts[cap] = cap_counts.get(cap, 0) + 1
        
        most_common = sorted(cap_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Gaps (capabilities few agents have)
        least_common = sorted(cap_counts.items(), key=lambda x: x[1])[:5]
        
        return {
            "agents": len(matrix),
            "capabilities": total_caps,
            "avg_coverage": round(avg_coverage * 100, 1),
            "most_common_capabilities": most_common,
            "capability_gaps": least_common
        }


def main():
    import sys
    matrix = CapabilityMatrix()
    
    if len(sys.argv) < 2:
        print("Agent Capability Matrix")
        print("Usage: capability-matrix.py <command> [args]")
        print("Commands:")
        print("  add-cap <capability>")
        print("  register <agent_id> <name> <capabilities...>")
        print("  matrix")
        print("  coverage <capabilities...>")
        print("  pairs")
        print("  stats")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "add-cap":
        if len(sys.argv) < 3:
            print("Usage: add-cap <capability>")
            return
        result = matrix.add_capability(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "register":
        if len(sys.argv) < 5:
            print("Usage: register <agent_id> <name> <capabilities...>")
            return
        agent_id = sys.argv[2]
        name = sys.argv[3]
        capabilities = sys.argv[4:]
        
        # Add new capabilities
        for cap in capabilities:
            matrix.add_capability(cap)
        
        result = matrix.register_agent(agent_id, name, capabilities)
        print(json.dumps(result, indent=2))
    
    elif cmd == "matrix":
        result = matrix.get_matrix()
        print(json.dumps(result, indent=2))
    
    elif cmd == "coverage":
        if len(sys.argv) < 3:
            print("Usage: coverage <capabilities...>")
            return
        result = matrix.analyze_coverage(sys.argv[2:])
        print(json.dumps(result, indent=2))
    
    elif cmd == "pairs":
        result = matrix.find_complementary_pairs()
        print(json.dumps(result, indent=2))
    
    elif cmd == "stats":
        result = matrix.get_statistics()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()