#!/usr/bin/env python3
"""
AGENT PERFORMANCE TRACKER
Tracks agent work, quality, and contribution metrics
Integrated with trust system and economy
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

TRACKER_DIR = Path("/root/.openclaw/workspace/agent-hub/data/tracker")
TRACKER_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class WorkEntry:
    """A single unit of work done by an agent"""
    id: str
    agent_id: str
    work_type: str  # code, research, review, discovery, build
    description: str
    quality_score: float  # 0.0 to 1.0
    impact_score: float   # 0.0 to 1.0
    time_spent_minutes: int
    timestamp: str
    verified: bool = False
    verified_by: str = ""
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def to_dict(self) -> dict:
        return asdict(self)

class PerformanceTracker:
    """Track agent performance over time"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.work_log = TRACKER_DIR / f"{agent_id}_work.json"
        self.stats_cache = TRACKER_DIR / f"{agent_id}_stats.json"
        self.entries = self.load_entries()
    
    def load_entries(self) -> List[WorkEntry]:
        if self.work_log.exists():
            with open(self.work_log) as f:
                data = json.load(f)
                return [WorkEntry(**e) for e in data]
        return []
    
    def save_entries(self):
        with open(self.work_log, 'w') as f:
            json.dump([e.to_dict() for e in self.entries], f, indent=2)
    
    def log_work(self, work_type: str, description: str, quality: float, 
                 impact: float, time_minutes: int, tags: List[str] = None) -> WorkEntry:
        """Log a new work entry"""
        entry = WorkEntry(
            id=f"work_{len(self.entries) + 1}_{int(datetime.now().timestamp())}",
            agent_id=self.agent_id,
            work_type=work_type,
            description=description,
            quality_score=min(1.0, max(0.0, quality)),
            impact_score=min(1.0, max(0.0, impact)),
            time_spent_minutes=time_minutes,
            timestamp=datetime.utcnow().isoformat(),
            tags=tags or []
        )
        self.entries.append(entry)
        self.save_entries()
        self.invalidate_cache()
        return entry
    
    def get_stats(self, days: int = 30) -> Dict:
        """Get performance stats for the last N days"""
        # Check cache first
        if self.stats_cache.exists():
            cached = json.load(open(self.stats_cache))
            if cached.get("days") == days and \
               datetime.fromisoformat(cached["cached_at"]) > datetime.utcnow() - timedelta(hours=1):
                return cached
        
        # Calculate fresh stats
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent = [e for e in self.entries 
                  if datetime.fromisoformat(e.timestamp) > cutoff]
        
        if not recent:
            return {
                "agent_id": self.agent_id,
                "period_days": days,
                "total_work": 0,
                "work_types": {},
                "avg_quality": 0,
                "avg_impact": 0,
                "trust_score": 0,
                "level": "NEW"
            }
        
        # Aggregate by work type
        by_type = {}
        for e in recent:
            if e.work_type not in by_type:
                by_type[e.work_type] = {"count": 0, "total_quality": 0, "total_impact": 0}
            by_type[e.work_type]["count"] += 1
            by_type[e.work_type]["total_quality"] += e.quality_score
            by_type[e.work_type]["total_impact"] += e.impact_score
        
        for wt, data in by_type.items():
            data["avg_quality"] = data["total_quality"] / data["count"]
            data["avg_impact"] = data["total_impact"] / data["count"]
        
        # Calculate trust score based on quality, impact, and consistency
        avg_quality = sum(e.quality_score for e in recent) / len(recent)
        avg_impact = sum(e.impact_score for e in recent) / len(recent)
        consistency = 1.0 - (len(set(e.quality_score for e in recent)) / max(1, len(recent)))
        
        trust_score = (avg_quality * 40 + avg_impact * 40 + consistency * 20) * len(recent) / 10
        
        # Determine level
        if trust_score < 10:
            level = "NEW"
        elif trust_score < 50:
            level = "TESTED"
        elif trust_score < 150:
            level = "TRUSTED"
        elif trust_score < 500:
            level = "PROVEN"
        else:
            level = "ELITE"
        
        stats = {
            "agent_id": self.agent_id,
            "period_days": days,
            "total_work": len(recent),
            "work_types": by_type,
            "avg_quality": round(avg_quality * 100, 1),
            "avg_impact": round(avg_impact * 100, 1),
            "consistency": round(consistency * 100, 1),
            "trust_score": round(trust_score, 1),
            "level": level,
            "cached_at": datetime.utcnow().isoformat()
        }
        
        # Cache it
        with open(self.stats_cache, 'w') as f:
            json.dump(stats, f, indent=2)
        
        return stats
    
    def invalidate_cache(self):
        if self.stats_cache.exists():
            self.stats_cache.unlink()
    
    def get_leaderboard(self, days: int = 30, limit: int = 10) -> List[Dict]:
        """Get top agents by trust score"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        all_stats = []
        
        for log_file in TRACKER_DIR.glob("*_work.json"):
            agent_id = log_file.stem.replace("_work", "")
            try:
                tracker = PerformanceTracker(agent_id)
                stats = tracker.get_stats(days)
                all_stats.append(stats)
            except:
                pass
        
        all_stats.sort(key=lambda x: x["trust_score"], reverse=True)
        return all_stats[:limit]
    
    def verify_work(self, work_id: str, verifier: str) -> bool:
        """Mark a work entry as verified"""
        for e in self.entries:
            if e.id == work_id:
                e.verified = True
                e.verified_by = verifier
                self.save_entries()
                self.invalidate_cache()
                return True
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Agent Performance Tracker")
    parser.add_argument("action", choices=["log", "stats", "leaderboard", "verify"])
    parser.add_argument("--agent", default="marxagent")
    parser.add_argument("--type", default="code", help="Work type")
    parser.add_argument("--description", default="", help="Work description")
    parser.add_argument("--quality", type=float, default=0.8, help="Quality 0-1")
    parser.add_argument("--impact", type=float, default=0.7, help="Impact 0-1")
    parser.add_argument("--minutes", type=int, default=30, help="Time spent")
    parser.add_argument("--tags", nargs="*", default=[])
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--work-id", help="Work ID to verify")
    parser.add_argument("--limit", type=int, default=10)
    
    args = parser.parse_args()
    tracker = PerformanceTracker(args.agent)
    
    if args.action == "log":
        entry = tracker.log_work(args.type, args.description, args.quality, args.impact, args.minutes, args.tags)
        print(f"✓ Logged work: {entry.id}")
        print(f"  Type: {entry.work_type}, Quality: {entry.quality_score*100:.0f}%, Impact: {entry.impact_score*100:.0f}%")
    
    elif args.action == "stats":
        stats = tracker.get_stats(args.days)
        print(f"\n📊 {stats['agent_id']} Performance ({stats['period_days']} days)")
        print(f"   Total Work: {stats['total_work']} entries")
        print(f"   Avg Quality: {stats['avg_quality']}%")
        print(f"   Avg Impact: {stats['avg_impact']}%")
        print(f"   Trust Score: {stats['trust_score']}")
        print(f"   Level: {stats['level']}")
        if stats['work_types']:
            print("\n   By Type:")
            for wt, data in stats['work_types'].items():
                print(f"     {wt}: {data['count']} entries, {data['avg_quality']:.0f}% quality")
    
    elif args.action == "leaderboard":
        leaders = tracker.get_leaderboard(args.days, args.limit)
        print(f"\n🏆 Top Agents (last {args.days} days)")
        for i, s in enumerate(leaders, 1):
            print(f"  {i}. {s['agent_id']} - {s['trust_score']} ({s['level']}) - {s['total_work']} entries")
    
    elif args.action == "verify":
        if args.work_id:
            result = tracker.verify_work(args.work_id, args.agent)
            print(f"✓ Verified work {args.work_id}" if result else "✗ Work not found")
        else:
            print("--work-id required for verify action")

if __name__ == "__main__":
    main()