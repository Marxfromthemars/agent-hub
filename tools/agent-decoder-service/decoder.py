#!/usr/bin/env python3
"""
Agent Decoder Service
Decoder service.
"""

import json
from pathlib import Path

class DecoderService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "decoder_service.json"
        self.decoders = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.decoders = json.load(f)
    
    def register(self, name, decoder):
        self.decoders[name] = decoder
        with open(self.file, 'w') as f:
            json.dump(self.decoders, f)


if __name__ == "__main__":
    import sys
    d = DecoderService()
    if len(sys.argv) > 2:
        d.register(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "registered"}))