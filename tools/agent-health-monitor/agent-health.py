#!/usr/bin/env python3
"""
Agent Health Monitor
Monitors agent health status and sends alerts when issues detected.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

class HealthMonitor:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.health_file = self.data_dir / "agent_health.json"
        self.config_file = self.data_dir / "health_config.json"
        self.health = self._load_health()
        self.config = self._load_config()
    
    def _load_health(self):
        if self.health_file.exists():
            with open(self.health_file) as f:
                return json.load(f)
        return {"agents": {}, "alerts": [], "checks": []}
    
    def _load_config(self):
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)
        return {
            "heartbeat_timeout_minutes": 30,
            "max_failed_checks": 3,
            "alert_channels": ["log"]
        }
    
    def _save_health(self):
        with open(self.health_file, 'w') as f:
            json.dump(self.health, f, indent=2)
    
    def heartbeat(self, agent_id, status="healthy"):
        """Record agent heartbeat."""
        now = datetime.utcnow()
        
        if agent_id not in self.health["agents"]:
            self.health["agents"][agent_id] = {
                "first_seen": now.isoformat(),
                "check_count": 0,
                "fail_count": 0
            }
        
        self.health["agents"][agent_id]["last_heartbeat"] = now.isoformat()
        self.health["agents"][agent_id]["last_status"] = status
        self.health["agents"][agent_id]["check_count"] += 1
        
        self.health["checks"].append({
            "agent_id": agent_id,
            "timestamp": now.isoformat(),
            "status": status
        })
        # Keep last 100 checks
        self.health["checks"] = self.health["checks"][-100:]
        
        self._save_health()
        return {"status": "heartbeat_recorded", "agent_id": agent_id}
    
    def check_health(self, agent_id):
        """Check health status of an agent."""
        if agent_id not in self.health["agents"]:
            return {"status": "unknown", "agent_id": agent_id}
        
        agent = self.health["agents"][agent_id]
        last_heartbeat = datetime.fromisoformat(agent["last_heartbeat"])
        minutes_since = (datetime.utcnow() - last_heartbeat).total_seconds() / 60
        
        timeout = self.config["heartbeat_timeout_minutes"]
        
        if minutes_since > timeout:
            return {
                "status": "unhealthy",
                "agent_id": agent_id,
                "reason": "heartbeat_timeout",
                "minutes_since_heartbeat": round(minutes_since, 1),
                "threshold_minutes": timeout
            }
        
        return {
            "status": "healthy",
            "agent_id": agent_id,
            "minutes_since_heartbeat": round(minutes_since, 1)
        }
    
    def check_all(self):
        """Check health of all known agents."""
        results = []
        for agent_id in self.health["agents"]:
            health = self.check_health(agent_id)
            results.append(health)
            
            # Generate alert if unhealthy
            if health["status"] == "unhealthy":
                self._generate_alert(health)
        
        return results
    
    def _generate_alert(self, health_info):
        """Generate an alert for unhealthy agent."""
        alert = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "agent_unhealthy",
            "agent_id": health_info["agent_id"],
            "reason": health_info.get("reason"),
            "details": health_info
        }
        
        # Avoid duplicate alerts within 5 minutes
        recent = any(
            a["agent_id"] == health_info["agent_id"] and
            datetime.fromisoformat(a["timestamp"]) > datetime.utcnow() - timedelta(minutes=5)
            for a in self.health["alerts"]
        )
        
        if not recent:
            self.health["alerts"].append(alert)
            self.health["alerts"] = self.health["alerts"][-50:]  # Keep last 50
            self._save_health()
    
    def get_alerts(self, since_minutes=60):
        """Get recent alerts."""
        cutoff = datetime.utcnow() - timedelta(minutes=since_minutes)
        return [
            a for a in self.health["alerts"]
            if datetime.fromisoformat(a["timestamp"]) > cutoff
        ]
    
    def get_all_health(self):
        """Get health status of all agents."""
        return [self.check_health(aid) for aid in self.health["agents"]]
    
    def get_health_summary(self):
        """Get summary of all agent health."""
        all_health = self.get_all_health()
        healthy = sum(1 for h in all_health if h["status"] == "healthy")
        unhealthy = sum(1 for h in all_health if h["status"] == "unhealthy")
        unknown = sum(1 for h in all_health if h["status"] == "unknown")
        
        return {
            "total_agents": len(self.health["agents"]),
            "healthy": healthy,
            "unhealthy": unhealthy,
            "unknown": unknown,
            "recent_alerts": len(self.get_alerts())
        }


def main():
    import sys
    monitor = HealthMonitor()
    
    if len(sys.argv) < 2:
        print("Agent Health Monitor")
        print("Usage: agent-health.py <command> [args]")
        print("Commands:")
        print("  heartbeat <agent_id> [status]")
        print("  check <agent_id>")
        print("  check-all")
        print("  alerts [minutes]")
        print("  summary")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "heartbeat":
        if len(sys.argv) < 3:
            print("Usage: heartbeat <agent_id> [status]")
            return
        status = sys.argv[3] if len(sys.argv) > 3 else "healthy"
        result = monitor.heartbeat(sys.argv[2], status)
        print(json.dumps(result, indent=2))
    
    elif cmd == "check":
        if len(sys.argv) < 3:
            print("Usage: check <agent_id>")
            return
        result = monitor.check_health(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "check-all":
        results = monitor.check_all()
        print(json.dumps(results, indent=2))
    
    elif cmd == "alerts":
        minutes = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        alerts = monitor.get_alerts(minutes)
        print(json.dumps(alerts, indent=2))
    
    elif cmd == "summary":
        summary = monitor.get_health_summary()
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()