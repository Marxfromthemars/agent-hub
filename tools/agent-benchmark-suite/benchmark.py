#!/usr/bin/env python3
"""
Agent Performance Benchmark
Benchmarks agent performance metrics.
"""

import json
import time
from datetime import datetime
from pathlib import Path

class PerformanceBenchmark:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.results_file = self.data_dir / "benchmark_results.json"
        self.results = self._load_results()
    
    def _load_results(self):
        if self.results_file.exists():
            with open(self.results_file) as f:
                return json.load(f)
        return {"benchmarks": []}
    
    def _save_results(self):
        with open(self.results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
    
    def benchmark(self, name, func, iterations=10):
        """Benchmark a function."""
        times = []
        for i in range(iterations):
            start = time.time()
            try:
                func()
                elapsed = (time.time() - start) * 1000  # ms
                times.append(elapsed)
            except Exception as e:
                times.append(-1)  # Error marker
        
        valid_times = [t for t in times if t >= 0]
        
        benchmark = {
            "id": f"bench-{len(self.results['benchmarks']) + 1}",
            "name": name,
            "iterations": iterations,
            "timestamp": datetime.utcnow().isoformat(),
            "times": times,
            "avg_ms": sum(valid_times) / len(valid_times) if valid_times else 0,
            "min_ms": min(valid_times) if valid_times else 0,
            "max_ms": max(valid_times) if valid_times else 0,
            "success_rate": len(valid_times) / iterations
        }
        
        self.results["benchmarks"].append(benchmark)
        self._save_results()
        
        return benchmark
    
    def benchmark_agent_operation(self, agent_id, operation):
        """Benchmark a specific agent operation."""
        results = []
        
        for i in range(5):
            start = time.time()
            # Simulate operation
            time.sleep(0.01)
            elapsed = (time.time() - start) * 1000
            results.append(elapsed)
        
        return {
            "agent_id": agent_id,
            "operation": operation,
            "avg_ms": sum(results) / len(results),
            "iterations": len(results)
        }
    
    def get_results(self, limit=20):
        """Get recent benchmark results."""
        return self.results["benchmarks"][-limit:]
    
    def get_summary(self):
        """Get benchmark summary."""
        benchmarks = self.results["benchmarks"]
        if not benchmarks:
            return {"total": 0}
        
        return {
            "total_benchmarks": len(benchmarks),
            "latest_avg_ms": benchmarks[-1]["avg_ms"] if benchmarks else 0,
            "by_name": self._group_by_name()
        }
    
    def _group_by_name(self):
        """Group results by benchmark name."""
        grouped = {}
        for b in self.results["benchmarks"]:
            name = b["name"]
            if name not in grouped:
                grouped[name] = {"count": 0, "avg_ms": 0, "total_ms": 0}
            grouped[name]["count"] += 1
            grouped[name]["total_ms"] += b["avg_ms"]
            grouped[name]["avg_ms"] = grouped[name]["total_ms"] / grouped[name]["count"]
        return grouped


def main():
    import sys
    bench = PerformanceBenchmark()
    
    if len(sys.argv) < 2:
        print("Agent Performance Benchmark")
        print("Usage: benchmark.py <command> [args]")
        print("Commands:")
        print("  run <name> [iterations]")
        print("  agent <agent_id> <operation>")
        print("  results [limit]")
        print("  summary")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "run":
        name = sys.argv[2] if len(sys.argv) > 2 else "test"
        iterations = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        
        def dummy_func():
            sum(range(1000))
        
        result = bench.benchmark(name, dummy_func, iterations)
        print(json.dumps(result, indent=2))
    
    elif cmd == "agent":
        agent_id = sys.argv[2] if len(sys.argv) > 2 else "agent-1"
        operation = sys.argv[3] if len(sys.argv) > 3 else "process"
        result = bench.benchmark_agent_operation(agent_id, operation)
        print(json.dumps(result, indent=2))
    
    elif cmd == "results":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        results = bench.get_results(limit)
        print(json.dumps(results, indent=2))
    
    elif cmd == "summary":
        result = bench.get_summary()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()