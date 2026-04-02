#!/usr/bin/env python3
"""
Agent Encoder Service
Encoder service.
"""

import json
from pathlib import Path

class EncoderService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "encoder_service_v2.json"
        self.encoders = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.encoders = json.load(f)
    
    def encode(self, format, data):
        self.encoders[format] = data
        with open(self.file, 'w') as f:
            json.dump(self.encoders, f)


if __name__ == "__main__":
    import sys
    e = EncoderService()
    if len(sys.argv) > 2:
        e.encode(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "encoded"}))