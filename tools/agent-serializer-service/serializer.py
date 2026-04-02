#!/usr/bin/env python3
"""
Agent Serializer Service
Serializer service.
"""

import json
from pathlib import Path

class SerializerService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "serializer_service.json"
        self.serializers = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.serializers = json.load(f)
    
    def register(self, format, serializer):
        self.serializers[format] = serializer
        with open(self.file, 'w') as f:
            json.dump(self.serializers, f)


if __name__ == "__main__":
    import sys
    s = SerializerService()
    if len(sys.argv) > 2:
        s.register(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "registered"}))