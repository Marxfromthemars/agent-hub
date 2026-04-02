#!/usr/bin/env python3
"""
Agent Backup System
Manages agent data backups and restore.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

class BackupSystem:
    def __init__(self, data_dir="data", backup_dir="backups"):
        self.data_dir = Path(data_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.manifest_file = self.backup_dir / "manifest.json"
        self.manifest = self._load_manifest()
    
    def _load_manifest(self):
        if self.manifest_file.exists():
            with open(self.manifest_file) as f:
                return json.load(f)
        return {"backups": []}
    
    def _save_manifest(self):
        with open(self.manifest_file, 'w') as f:
            json.dump(self.manifest, f, indent=2)
    
    def create_backup(self, name=None):
        """Create a backup of all agent data."""
        backup_name = name or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        files_backed = []
        for f in self.data_dir.glob("*.json"):
            dest = backup_path / f.name
            shutil.copy2(f, dest)
            files_backed.append(f.name)
        
        backup_entry = {
            "id": f"backup-{len(self.manifest['backups']) + 1}",
            "name": backup_name,
            "path": str(backup_path),
            "files": files_backed,
            "created": datetime.utcnow().isoformat(),
            "size_bytes": sum((backup_path / f).stat().st_size for f in files_backed)
        }
        
        self.manifest["backups"].append(backup_entry)
        self._save_manifest()
        
        return {"status": "created", "backup": backup_entry}
    
    def list_backups(self):
        """List all backups."""
        return self.manifest["backups"]
    
    def restore_backup(self, backup_id):
        """Restore from a backup."""
        backup = None
        for b in self.manifest["backups"]:
            if b["id"] == backup_id:
                backup = b
                break
        
        if not backup:
            return {"error": "backup not found"}
        
        backup_path = Path(backup["path"])
        restored = []
        
        for f in backup["files"]:
            src = backup_path / f
            dest = self.data_dir / f
            shutil.copy2(src, dest)
            restored.append(f)
        
        return {"status": "restored", "files": restored}
    
    def delete_backup(self, backup_id):
        """Delete a backup."""
        for b in self.manifest["backups"]:
            if b["id"] == backup_id:
                shutil.rmtree(b["path"])
                self.manifest["backups"].remove(b)
                self._save_manifest()
                return {"status": "deleted"}
        return {"error": "backup not found"}


def main():
    import sys
    backup = BackupSystem()
    
    if len(sys.argv) < 2:
        print("Agent Backup System")
        print("Usage: backup-system.py <command> [args]")
        print("Commands:")
        print("  create [name]")
        print("  list")
        print("  restore <backup_id>")
        print("  delete <backup_id>")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "create":
        name = sys.argv[2] if len(sys.argv) > 2 else None
        result = backup.create_backup(name)
        print(json.dumps(result, indent=2))
    
    elif cmd == "list":
        result = backup.list_backups()
        print(json.dumps(result, indent=2))
    
    elif cmd == "restore":
        if len(sys.argv) < 3:
            print("Usage: restore <backup_id>")
            return
        result = backup.restore_backup(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "delete":
        if len(sys.argv) < 3:
            print("Usage: delete <backup_id>")
            return
        result = backup.delete_backup(sys.argv[2])
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()