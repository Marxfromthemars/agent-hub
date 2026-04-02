#!/usr/bin/env python3
"""
Agent Metrics Dashboard
Generates real-time metrics dashboards for agent monitoring.
"""

import json
from datetime import datetime
from pathlib import Path

class MetricsDashboard:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.dashboards_file = self.data_dir / "dashboards.json"
        self.dashboards = self._load_dashboards()
    
    def _load_dashboards(self):
        if self.dashboards_file.exists():
            with open(self.dashboards_file) as f:
                return json.load(f)
        return {"dashboards": [], "current_dashboard": None}
    
    def _save_dashboards(self):
        with open(self.dashboards_file, 'w') as f:
            json.dump(self.dashboards, f, indent=2)
    
    def create_dashboard(self, name, widgets):
        """Create a new dashboard with widgets."""
        dashboard = {
            "id": f"dash-{len(self.dashboards['dashboards']) + 1}",
            "name": name,
            "widgets": widgets,  # List of {type, title, data_source}
            "created": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        self.dashboards["dashboards"].append(dashboard)
        self._save_dashboards()
        
        return {"status": "created", "dashboard_id": dashboard["id"]}
    
    def get_dashboard(self, dashboard_id):
        """Get a specific dashboard."""
        for d in self.dashboards["dashboards"]:
            if d["id"] == dashboard_id:
                return d
        return None
    
    def update_widget_data(self, dashboard_id, widget_title, data):
        """Update data for a widget."""
        for d in self.dashboards["dashboards"]:
            if d["id"] == dashboard_id:
                for widget in d["widgets"]:
                    if widget.get("title") == widget_title:
                        widget["data"] = data
                        widget["updated"] = datetime.utcnow().isoformat()
                d["last_updated"] = datetime.utcnow().isoformat()
                self._save_dashboards()
                return {"status": "updated"}
        return {"status": "not_found"}
    
    def generate_html(self, dashboard_id):
        """Generate HTML for a dashboard."""
        dashboard = self.get_dashboard(dashboard_id)
        if not dashboard:
            return {"error": "dashboard not found"}
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{dashboard['name']}</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; margin: 0; padding: 20px; background: #0a0a0f; color: #fff; }}
        .header {{ margin-bottom: 30px; }}
        .header h1 {{ color: #6366f1; margin: 0; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ background: #12121a; border-radius: 12px; padding: 20px; border: 1px solid #2a2a3a; }}
        .card h3 {{ color: #71717a; font-size: 12px; text-transform: uppercase; margin: 0 0 10px 0; }}
        .metric {{ font-size: 36px; font-weight: bold; color: #22c55e; }}
        .metric.warning {{ color: #f59e0b; }}
        .metric.error {{ color: #ef4444; }}
        .timestamp {{ color: #71717a; font-size: 12px; margin-top: 10px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 {dashboard['name']}</h1>
        <p class="timestamp">Updated: {dashboard['last_updated']}</p>
    </div>
    <div class="grid">
"""
        
        for widget in dashboard.get("widgets", []):
            widget_type = widget.get("type", "metric")
            title = widget.get("title", "Widget")
            data = widget.get("data", {})
            
            if widget_type == "metric":
                value = data.get("value", "N/A")
                status = data.get("status", "normal")
                status_class = "error" if status == "error" else "warning" if status == "warning" else ""
                
                html += f"""
        <div class="card">
            <h3>{title}</h3>
            <div class="metric {status_class}">{value}</div>
        </div>
"""
        
        html += """
    </div>
</body>
</html>"""
        
        return {"html": html, "dashboard_id": dashboard_id}
    
    def list_dashboards(self):
        """List all dashboards."""
        return self.dashboards["dashboards"]


def main():
    import sys
    dashboard = MetricsDashboard()
    
    if len(sys.argv) < 2:
        print("Agent Metrics Dashboard")
        print("Usage: metrics-dashboard.py <command> [args]")
        print("Commands:")
        print("  create <name> <widgets_json>")
        print("  get <dashboard_id>")
        print("  update <dashboard_id> <widget_title> <data_json>")
        print("  html <dashboard_id>")
        print("  list")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "create":
        name = sys.argv[2] if len(sys.argv) > 2 else "Dashboard"
        widgets = [{"type": "metric", "title": "Active Agents", "data": {"value": 3, "status": "normal"}}]
        result = dashboard.create_dashboard(name, widgets)
        print(json.dumps(result, indent=2))
    
    elif cmd == "get":
        if len(sys.argv) < 3:
            print("Usage: get <dashboard_id>")
            return
        result = dashboard.get_dashboard(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "update":
        if len(sys.argv) < 5:
            print("Usage: update <dashboard_id> <widget_title> <data_json>")
            return
        data = json.loads(sys.argv[5]) if len(sys.argv) > 5 else {}
        result = dashboard.update_widget_data(sys.argv[2], sys.argv[3], data)
        print(json.dumps(result, indent=2))
    
    elif cmd == "html":
        if len(sys.argv) < 3:
            print("Usage: html <dashboard_id>")
            return
        result = dashboard.generate_html(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "list":
        result = dashboard.list_dashboards()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()