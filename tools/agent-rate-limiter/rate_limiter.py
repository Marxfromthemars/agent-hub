#!/usr/bin/env python3
"""
Agent API Rate Limiter
Token bucket rate limiting for API requests.
"""

import json
import time
from datetime import datetime
from pathlib import Path

class RateLimiter:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.state_file = self.data_dir / "rate_limiter.json"
        self.state = self._load_state()
    
    def _load_state(self):
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {"buckets": {}, "limits": {}}
    
    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def set_limit(self, client_id, requests_per_minute):
        """Set rate limit for a client."""
        self.state["limits"][client_id] = {
            "requests_per_minute": requests_per_minute,
            "bucket_size": requests_per_minute,
            "refill_rate": requests_per_minute / 60.0,
            "set_at": datetime.utcnow().isoformat()
        }
        self._save_state()
        return {"status": "set", "client_id": client_id, "limit": requests_per_minute}
    
    def check(self, client_id):
        """Check if request is allowed."""
        if client_id not in self.state["limits"]:
            # Default limit if not set
            self.set_limit(client_id, 60)
        
        limit = self.state["limits"][client_id]
        
        if client_id not in self.state["buckets"]:
            self.state["buckets"][client_id] = {
                "tokens": limit["bucket_size"],
                "last_refill": time.time()
            }
        
        bucket = self.state["buckets"][client_id]
        now = time.time()
        
        # Refill tokens
        elapsed = now - bucket["last_refill"]
        tokens_to_add = elapsed * limit["refill_rate"]
        bucket["tokens"] = min(limit["bucket_size"], bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = now
        
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            self._save_state()
            return {"allowed": True, "remaining_tokens": int(bucket["tokens"])}
        
        self._save_state()
        return {
            "allowed": False,
            "remaining_tokens": 0,
            "retry_after": int(1 / limit["refill_rate"])
        }
    
    def get_status(self, client_id):
        """Get rate limit status for a client."""
        if client_id not in self.state["limits"]:
            return {"error": "no limit set"}
        
        limit = self.state["limits"][client_id]
        bucket = self.state["buckets"].get(client_id, {"tokens": limit["bucket_size"]})
        
        return {
            "limit": limit["requests_per_minute"],
            "remaining": int(bucket.get("tokens", 0)),
            "refill_rate": limit["refill_rate"]
        }


def main():
    import sys
    limiter = RateLimiter()
    
    if len(sys.argv) < 2:
        print("Agent Rate Limiter")
        print("Usage: rate-limiter.py <command> [args]")
        print("Commands:")
        print("  set <client_id> <requests_per_minute>")
        print("  check <client_id>")
        print("  status <client_id>")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "set":
        if len(sys.argv) < 4:
            print("Usage: set <client_id> <requests_per_minute>")
            return
        result = limiter.set_limit(sys.argv[2], int(sys.argv[3]))
        print(json.dumps(result, indent=2))
    
    elif cmd == "check":
        if len(sys.argv) < 3:
            print("Usage: check <client_id>")
            return
        result = limiter.check(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "status":
        if len(sys.argv) < 3:
            print("Usage: status <client_id>")
            return
        result = limiter.get_status(sys.argv[2])
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()