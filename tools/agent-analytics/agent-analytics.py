#!/usr/bin/env python3
"""
Agent Performance Analytics
Tracks and analyzes agent performance metrics over time.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

class AgentAnalytics:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.metrics_file = self.data_dir / "agent_analytics.json"
        self.metrics = self._load_metrics()
    
    def _load_metrics(self):
        if self.metrics_file.exists():
            with open(self.metrics_file) as f:
                return json.load(f)
        return {
            "agents": {},
            "daily_stats": {},
            "performance_trends": {}
        }
    
    def _save_metrics(self):
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def record_task_completion(self, agent_id, task_type, duration_seconds, success=True):
        """Record a task completion metric."""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        if agent_id not in self.metrics["agents"]:
            self.metrics["agents"][agent_id] = {
                "tasks_completed": 0,
                "tasks_failed": 0,
                "total_duration": 0,
                "task_types": {},
                "first_seen": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat()
            }
        
        agent = self.metrics["agents"][agent_id]
        agent["tasks_completed"] += 1 if success else 0
        agent["tasks_failed"] += 0 if success else 1
        agent["total_duration"] += duration_seconds
        agent["last_activity"] = datetime.utcnow().isoformat()
        
        # Track by task type
        if task_type not in agent["task_types"]:
            agent["task_types"][task_type] = {"count": 0, "total_duration": 0}
        agent["task_types"][task_type]["count"] += 1
        agent["task_types"][task_type]["total_duration"] += duration_seconds
        
        # Daily stats
        today_key = datetime.utcnow().strftime("%Y-%m-%d")
        if today_key not in self.metrics["daily_stats"]:
            self.metrics["daily_stats"][today_key] = {"tasks": 0, "agents": []}
        
        self.metrics["daily_stats"][today_key]["tasks"] += 1
        if agent_id not in self.metrics["daily_stats"][today_key]["agents"]:
            self.metrics["daily_stats"][today_key]["agents"].append(agent_id)
        
        self._save_metrics()
        return {"status": "recorded"}
    
    def record_collaboration(self, agent_a, agent_b, task_id):
        """Record a collaboration between agents."""
        if "collaborations" not in self.metrics:
            self.metrics["collaborations"] = []
        
        self.metrics["collaborations"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "agents": [agent_a, agent_b],
            "task_id": task_id
        })
        
        self._save_metrics()
        return {"status": "recorded"}
    
    def get_agent_stats(self, agent_id):
        """Get detailed statistics for an agent."""
        if agent_id not in self.metrics["agents"]:
            return {"status": "not_found"}
        
        agent = self.metrics["agents"][agent_id]
        total_tasks = agent["tasks_completed"] + agent["tasks_failed"]
        success_rate = agent["tasks_completed"] / total_tasks if total_tasks > 0 else 0
        avg_duration = agent["total_duration"] / total_tasks if total_tasks > 0 else 0
        
        return {
            "agent_id": agent_id,
            "tasks_completed": agent["tasks_completed"],
            "tasks_failed": agent["tasks_failed"],
            "success_rate": round(success_rate * 100, 1),
            "average_duration": round(avg_duration, 2),
            "top_skills": sorted(
                agent["task_types"].items(),
                key=lambda x: x[1]["count"], reverse=True
            )[:5],
            "first_seen": agent["first_seen"],
            "last_activity": agent["last_activity"]
        }
    
    def get_daily_stats(self, days=7):
        """Get statistics for the last N days."""
        stats = []
        today = datetime.utcnow()
        
        for i in range(days):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            if date in self.metrics["daily_stats"]:
                day_data = self.metrics["daily_stats"][date]
                stats.append({
                    "date": date,
                    "tasks": day_data["tasks"],
                    "active_agents": len(day_data["agents"])
                })
            else:
                stats.append({"date": date, "tasks": 0, "active_agents": 0})
        
        return stats
    
    def get_platform_stats(self):
        """Get overall platform statistics."""
        total_tasks = sum(a["tasks_completed"] for a in self.metrics["agents"].values())
        total_agents = len(self.metrics["agents"])
        
        # Calculate top performers
        agents_with_scores = [
            (aid, self.get_agent_stats(aid))
            for aid in self.metrics["agents"]
        ]
        
        top_performers = sorted(
            [(a[0], a[1]["success_rate"]) for a in agents_with_scores],
            key=lambda x: x[1], reverse=True
        )[:5]
        
        # Most active agents
        most_active = sorted(
            [(a[0], self.metrics["agents"][a[0]]["tasks_completed"]) 
             for a in agents_with_scores],
            key=lambda x: x[1], reverse=True
        )[:5]
        
        return {
            "total_tasks_completed": total_tasks,
            "total_agents": total_agents,
            "total_collaborations": len(self.metrics.get("collaborations", [])),
            "top_performers": [{"agent": a[0], "rate": a[1]} for a in top_performers],
            "most_active": [{"agent": a[0], "tasks": a[1]} for a in most_active]
        }
    
    def get_trends(self, days=7):
        """Get performance trends over time."""
        daily_stats = self.get_daily_stats(days)
        
        return {
            "daily_tasks": [d["tasks"] for d in daily_stats],
            "daily_active_agents": [d["active_agents"] for d in daily_stats],
            "dates": [d["date"] for d in daily_stats]
        }


def main():
    import sys
    analytics = AgentAnalytics()
    
    if len(sys.argv) < 2:
        print("Agent Performance Analytics")
        print("Usage: agent-analytics.py <command> [args]")
        print("Commands:")
        print("  record <agent_id> <task_type> <duration_seconds> [success]")
        print("  agent <agent_id>")
        print("  daily [days]")
        print("  platform")
        print("  trends [days]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "record":
        if len(sys.argv) < 5:
            print("Usage: record <agent_id> <task_type> <duration> [success]")
            return
        success = sys.argv[4].lower() != "false" if len(sys.argv) > 4 else True
        result = analytics.record_task_completion(sys.argv[2], sys.argv[3], int(sys.argv[4]), success)
        print(json.dumps(result, indent=2))
    
    elif cmd == "agent":
        if len(sys.argv) < 3:
            print("Usage: agent <agent_id>")
            return
        stats = analytics.get_agent_stats(sys.argv[2])
        print(json.dumps(stats, indent=2))
    
    elif cmd == "daily":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        stats = analytics.get_daily_stats(days)
        print(json.dumps(stats, indent=2))
    
    elif cmd == "platform":
        stats = analytics.get_platform_stats()
        print(json.dumps(stats, indent=2))
    
    elif cmd == "trends":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        trends = analytics.get_trends(days)
        print(json.dumps(trends, indent=2))


if __name__ == "__main__":
    main()