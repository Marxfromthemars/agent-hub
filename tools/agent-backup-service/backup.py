#!/usr/bin/env python3
"""
Agent Backup Service
Backup service.
"""

import json
from pathlib import Path

class BackupService:
    def __init__(self, data_dir="data"):
        self.file = Path(data_dir) / "backup_service.json"
        self.backups = {}
        self._load()
    
    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.backups = json.load(f)
    
    def backup(self, name, data):
        self.backups[name] = data
        with open(self.file, 'w') as f:
            json.dump(self.backups, f)


if __name__ == "__main__":
    import sys
    b = BackupService()
    if len(sys.argv) > 2:
        b.backup(sys.argv[1], sys.argv[2])
        print(json.dumps({"status": "backed_up"}))