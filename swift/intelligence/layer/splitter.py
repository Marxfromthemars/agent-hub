#!/usr/bin/env python3
"""
Token Intelligence Layer - Task Splitter
Split large tasks into smaller reusable pieces
"""
import json

class TaskSplitter:
    @staticmethod
    def split(task, max_tokens=2000):
        """Split task into smaller pieces"""
        words = task.split()
        pieces = []
        current = []
        token_count = 0
        
        for word in words:
            current.append(word)
            token_count += 1  # rough estimate
            if token_count >= max_tokens:
                pieces.append(" ".join(current))
                current = []
                token_count = 0
        
        if current:
            pieces.append(" ".join(current))
        
        return pieces
    
    @staticmethod
    def should_early_stop(results, quality_threshold=0.8):
        """Check if we can stop early"""
        # If we have good enough results, stop
        return len(results) > 0 and results[-1].get("quality", 0) > quality_threshold

# Usage: from intelligence.layer.splitter import TaskSplitter
# pieces = TaskSplitter.split("large task...")
# if TaskSplitter.should_early_stop(results): break
