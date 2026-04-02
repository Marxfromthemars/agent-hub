#!/usr/bin/env python3
"""
Agent Data Exporter
Export agent data in various formats.
"""

import json
import csv
from datetime import datetime
from pathlib import Path

class DataExporter:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.exports_file = self.data_dir / "exports.json"
        self.exports = self._load_exports()
    
    def _load_exports(self):
        if self.exports_file.exists():
            with open(self.exports_file) as f:
                return json.load(f)
        return {"exports": []}
    
    def _save_exports(self):
        with open(self.exports_file, 'w') as f:
            json.dump(self.exports, f, indent=2)
    
    def export_json(self, data_type, output_file):
        """Export data as JSON."""
        data_file = self.data_dir / f"{data_type}.json"
        
        if not data_file.exists():
            return {"error": f"data type {data_type} not found"}
        
        output_path = self.data_dir / output_file
        with open(data_file) as src:
            with open(output_path, 'w') as dst:
                dst.write(src.read())
        
        entry = {
            "id": f"export-{len(self.exports['exports']) + 1}",
            "type": data_type,
            "format": "json",
            "file": output_file,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.exports["exports"].append(entry)
        self._save_exports()
        
        return {"status": "exported", "file": output_file}
    
    def export_csv(self, data_type, output_file):
        """Export data as CSV."""
        data_file = self.data_dir / f"{data_type}.json"
        
        if not data_file.exists():
            return {"error": f"data type {data_type} not found"}
        
        with open(data_file) as f:
            data = json.load(f)
        
        if isinstance(data, list) and data:
            output_path = self.data_dir / output_file
            
            # Get all keys from first item
            if isinstance(data[0], dict):
                fields = list(data[0].keys())
                
                with open(output_path, 'w', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fields)
                    writer.writeheader()
                    writer.writerows(data)
        
        entry = {
            "id": f"export-{len(self.exports['exports']) + 1}",
            "type": data_type,
            "format": "csv",
            "file": output_file,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.exports["exports"].append(entry)
        self._save_exports()
        
        return {"status": "exported", "file": output_file}
    
    def list_exports(self):
        """List all exports."""
        return self.exports["exports"]


def main():
    import sys
    exporter = DataExporter()
    
    if len(sys.argv) < 2:
        print("Agent Data Exporter")
        print("Usage: data-exporter.py <command> [args]")
        print("Commands:")
        print("  json <data_type> <output_file>")
        print("  csv <data_type> <output_file>")
        print("  list")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "json":
        if len(sys.argv) < 4:
            print("Usage: json <data_type> <output_file>")
            return
        result = exporter.export_json(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))
    
    elif cmd == "csv":
        if len(sys.argv) < 4:
            print("Usage: csv <data_type> <output_file>")
            return
        result = exporter.export_csv(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))
    
    elif cmd == "list":
        result = exporter.list_exports()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()