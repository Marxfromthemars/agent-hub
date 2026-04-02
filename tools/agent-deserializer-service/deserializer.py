#!/usr/bin/env python3
"""
Agent Deserializer Service
Deserializer service.
"""

import json
from pathlib import Path

class DeserializerService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "deserializer_service.json"
        self.deserializers = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.deserializers = json.load(f)
    
    def deserialize(self, format, data):
        self.deserializers[format] = data
        with open(self.file, 'w') as f:
            json.dump(self.deserializers, f)


if __name__ == "__main__":
    import sys
    d = DeserializerService()
    if len(sys.argv) > 2:
        d.deserialize(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "deserialized"}))