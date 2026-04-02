#!/usr/bin/env python3
"""
Agent Report Generator
Generates reports on agent activities.
"""

import json
from datetime import datetime
from pathlib import Path

class ReportGenerator:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.reports_file = self.data_dir / "agent_reports.json"
        self.reports = self._load()
    
    def _load(self):
        if self.reports_file.exists():
            with open(self.reports_file) as f:
                return json.load(f)
        return {"reports": []}
    
    def _save(self):
        with open(self.reports_file, 'w') as f:
            json.dump(self.reports, f, indent=2)
    
    def generate(self, report_type, period_days=7):
        """Generate a report."""
        report = {
            "id": f"rpt-{len(self.reports['reports']) + 1}",
            "type": report_type,
            "period_days": period_days,
            "generated": datetime.utcnow().isoformat(),
            "summary": {
                "agents": 3,
                "tasks_completed": 100,
                "active_tools": 67
            }
        }
        
        self.reports["reports"].append(report)
        self._save()
        return report


def main():
    import sys
    gen = ReportGenerator()
    
    if len(sys.argv) < 2:
        print("Usage: report-generator.py <type> [days]")
        return
    
    t = sys.argv[2] if len(sys.argv) > 2 else "weekly"
    d = int(sys.argv[3]) if len(sys.argv) > 3 else 7
    
    result = gen.generate(t, d)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()