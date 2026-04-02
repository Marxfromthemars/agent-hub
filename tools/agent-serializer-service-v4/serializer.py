#!/usr/bin/env python3
"""
Agent Serializer Service
Serializer service.
"""

import json
from pathlib import Path

class SerializerService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "serializer_service_v4.json"
        self.serializers = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.serializers = json.load(f)
    
    def serialize(self, format, data):
        self.serializers[format] = data
        with open(self.file, 'w') as f:
            json.dump(self.serializers, f)


if __name__ == "__main__":
    import sys
    s = SerializerService()
    if len(sys.argv) > 2:
        s.serialize(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "serialized"}))