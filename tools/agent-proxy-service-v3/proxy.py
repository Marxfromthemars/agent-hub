#!/usr/bin/env python3
"""
Agent Proxy Service
Proxy service.
"""

import json
from pathlib import Path

class ProxyService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "proxy_service_v3.json"
        self.proxies = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.proxies = json.load(f)
    
    def proxy(self, name, target):
        self.proxies[name] = target
        with open(self.file, 'w') as f:
            json.dump(self.proxies, f)


if __name__ == "__main__":
    import sys
    p = ProxyService()
    if len(sys.argv) > 2:
        p.proxy(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "proxied"}))