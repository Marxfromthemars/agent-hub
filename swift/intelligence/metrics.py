#!/usr/bin/env python3
"""
Token Intelligence - Metrics
Measure value, not just tokens
"""
import json, os
from datetime import datetime

METRICS_FILE = "intelligence/metrics.json"

class Metrics:
    def __init__(self):
        self.data = {"features": [], "tokens_saved": 0, "reused": 0}
        self.load()
    
    def load(self):
        if os.path.exists(METRICS_FILE):
            with open(METRICS_FILE) as f:
                self.data = json.load(f)
    
    def save(self):
        with open(METRICS_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def feature(self, name):
        """Track a feature built"""
        self.data["features"].append({
            "name": name,
            "time": datetime.now().isoformat()
        })
        self.save()
    
    def saved(self, tokens):
        """Track tokens saved via caching"""
        self.data["tokens_saved"] += tokens
        self.save()
    
    def reused(self, outputs):
        """Track reused outputs"""
        self.data["reused"] += outputs
        self.save()
    
    def summary(self):
        return {
            "features_built": len(self.data["features"]),
            "tokens_saved": self.data["tokens_saved"],
            "outputs_reused": self.data["reused"]
        }
