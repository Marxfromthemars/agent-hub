#!/usr/bin/env python3
"""
Agent Benchmark Tool - Measure agent performance
"""
import json
import time
from datetime import datetime

class AgentBenchmark:
    def __init__(self):
        self.results = []
    
    def benchmark(self, agent_id, task_type, iterations=10):
        """Run benchmark on an agent"""
        start = time.time()
        times = []
        
        for _ in range(iterations):
            t_start = time.time()
            # Simulate task
            time.sleep(0.01)
            t_end = time.time()
            times.append(t_end - t_start)
        
        avg_time = sum(times) / len(times)
        
        result = {
            "agent": agent_id,
            "task_type": task_type,
            "iterations": iterations,
            "avg_time": avg_time,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.results.append(result)
        return result
    
    def get_stats(self):
        if not self.results:
            return "No benchmarks run"
        latest = self.results[-1]
        return f"Latest: {latest['agent']} on {latest['task_type']}: {latest['avg_time']*1000:.2f}ms"

if __name__ == "__main__":
    b = AgentBenchmark()
    for agent in ["marxagent", "researcher", "builder"]:
        r = b.benchmark(agent, "general", iterations=5)
        print(f"Benchmarked {agent}: {r['avg_time']*1000:.2f}ms avg")
