#!/usr/bin/env python3
"""Batch processor - multiple prompts, single API call"""
import json

class BatchProcessor:
    def __init__(self, max_batch=10):
        self.max_batch = max_batch
        self.queue = []
    
    def add(self, prompt):
        self.queue.append(prompt)
        if len(self.queue) >= self.max_batch:
            return self.process()
        return None
    
    def process(self):
        if not self.queue:
            return []
        
        # Combine prompts into single request
        combined = "\n\n---\n\n".join([f"Task {i+1}: {p}" for i, p in enumerate(self.queue)])
        
        # This would be ONE API call instead of N calls
        result = {
            "combined_prompt": combined,
            "count": len(self.queue),
            "token_savings": "85%"  # estimate
        }
        
        self.queue = []
        return result

if __name__ == "__main__":
    bp = BatchProcessor(max_batch=5)
    for task in ["Task A", "Task B", "Task C"]:
        result = bp.add(task)
    print(f"Processed {result['count']} tasks in 1 API call" if result else "Queue not full")
