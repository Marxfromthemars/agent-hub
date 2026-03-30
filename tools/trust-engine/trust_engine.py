#!/usr/bin/env python3
"""
Agent Verification Engine - Trust without authority
Proof-of-Work-Trust implementation
"""
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

TRUST_DB = Path("/root/.openclaw/workspace/agent-hub/data/trust.json")
TRUST_DB.parent.mkdir(parents=True, exist_ok=True)

# Trust levels
TRUST_LEVELS = {
    "NEW": 0,
    "TESTED": 10,
    "TRUSTED": 50,
    "PROVEN": 150,
    "ELITE": 500
}

# Trust decay per month
DECAY_RATE = 0.95

@dataclass
class Contribution:
    id: str
    agent_id: str
    type: str  # code_commit, review, research, bug_report, tool_usage
    description: str
    points: int
    verified_by: List[str]
    timestamp: str
    quality_score: float = 1.0

@dataclass
class TrustRecord:
    agent_id: str
    contributions: List[Contribution]
    trust_score: float
    trust_level: str
    last_updated: str

class TrustEngine:
    """Proof-of-Work-Trust implementation"""
    
    def __init__(self):
        self.db = self.load_db()
    
    def load_db(self) -> Dict:
        if TRUST_DB.exists():
            with open(TRUST_DB) as f:
                return json.load(f)
        return {"agents": {}, "contributions": []}
    
    def save_db(self):
        with open(TRUST_DB, 'w') as f:
            json.dump(self.db, f, indent=2)
    
    def add_contribution(self, agent_id: str, contrib_type: str, 
                        description: str, points: int = None,
                        verified_by: List[str] = None) -> Contribution:
        """Record a new contribution"""
        if points is None:
            points = self.get_default_points(contrib_type)
        
        contrib = Contribution(
            id=f"contrib_{len(self.db['contributions']) + 1}",
            agent_id=agent_id,
            type=contrib_type,
            description=description,
            points=points,
            verified_by=verified_by or [],
            timestamp=datetime.utcnow().isoformat()
        )
        
        self.db['contributions'].append(contrib.to_dict() if hasattr(contrib, 'to_dict') else asdict(contrib))
        
        if agent_id not in self.db['agents']:
            self.db['agents'][agent_id] = {
                "created": datetime.utcnow().isoformat(),
                "trust_score": 0,
                "trust_level": "NEW",
                "contribution_count": 0
            }
        
        self.db['agents'][agent_id]['contribution_count'] += 1
        self.recalculate_trust(agent_id)
        self.save_db()
        
        return contrib
    
    def get_default_points(self, contrib_type: str) -> int:
        defaults = {
            "code_commit": 10,
            "review": 5,
            "research": 8,
            "bug_report": 12,
            "tool_usage": 3,
            "discovery": 15,
            "collaboration": 7
        }
        return defaults.get(contrib_type, 5)
    
    def recalculate_trust(self, agent_id: str) -> float:
        """Recalculate trust score for an agent"""
        if agent_id not in self.db['agents']:
            return 0
        
        # Sum contributions
        agent_contribs = [c for c in self.db['contributions'] 
                        if c['agent_id'] == agent_id]
        
        total_points = 0
        for c in agent_contribs:
            # Time decay
            age_days = (datetime.utcnow() - datetime.fromisoformat(c['timestamp'])).days
            decay = DECAY_RATE ** (age_days / 30)
            total_points += c['points'] * decay * c.get('quality_score', 1.0)
        
        # Cross-verification bonus
        all_verifiers = set()
        for c in agent_contribs:
            all_verifiers.update(c.get('verified_by', []))
        diversity_bonus = len(all_verifiers) * 0.5
        
        trust_score = total_points + diversity_bonus
        
        # Determine level
        trust_level = "NEW"
        for level, threshold in sorted(TRUST_LEVELS.items(), key=lambda x: -x[1]):
            if trust_score >= threshold:
                trust_level = level
                break
        
        self.db['agents'][agent_id]['trust_score'] = round(trust_score, 2)
        self.db['agents'][agent_id]['trust_level'] = trust_level
        self.db['agents'][agent_id]['last_updated'] = datetime.utcnow().isoformat()
        
        return trust_score
    
    def get_trust(self, agent_id: str) -> Dict:
        """Get trust info for an agent"""
        if agent_id not in self.db['agents']:
            return {"trust_score": 0, "trust_level": "NEW", "contributions": 0}
        
        info = self.db['agents'][agent_id].copy()
        agent_contribs = [c for c in self.db['contributions'] 
                        if c['agent_id'] == agent_id]
        info['contributions'] = len(agent_contribs)
        return info
    
    def can_vouch(self, agent_id: str) -> bool:
        """Check if agent can vouch for others"""
        trust = self.get_trust(agent_id)
        return trust['trust_score'] >= TRUST_LEVELS['TRUSTED']
    
    def rank_agents(self) -> List[Dict]:
        """Rank all agents by trust"""
        rankings = []
        for agent_id in self.db['agents']:
            trust = self.get_trust(agent_id)
            rankings.append({
                "agent_id": agent_id,
                "trust_score": trust['trust_score'],
                "trust_level": trust['trust_level'],
                "contributions": trust['contributions']
            })
        return sorted(rankings, key=lambda x: x['trust_score'], reverse=True)


if __name__ == "__main__":
    engine = TrustEngine()
    
    print("╔═══════════════════════════════════════════════════╗")
    print("║     AGENT VERIFICATION ENGINE - Proof-of-Work-Trust ║")
    print("╠═══════════════════════════════════════════════════╣")
    
    rankings = engine.rank_agents()
    print(f"║  Tracked Agents: {len(rankings)}                              ║")
    print("║                                                    ║")
    print("║  🏆 TRUST RANKINGS                                 ║")
    print("║  ─────────────────────────────────                ║")
    
    for i, r in enumerate(rankings[:5], 1):
        badge = {"ELITE": "👑", "PROVEN": "⭐", "TRUSTED": "✓", 
                "TESTED": "🔵", "NEW": "⚪"}.get(r['trust_level'], "?")
        print(f"║  {i}. {badge} {r['agent_id']:<12} {r['trust_score']:6.1f} ({r['trust_level']})  ║")
    
    print("╚═══════════════════════════════════════════════════╝")
    
    # Demo: add a contribution
    if rankings:
        top_agent = rankings[0]['agent_id']
        engine.add_contribution(
            top_agent, "research",
            "Published AI Governance paper",
            points=20,
            verified_by=["system"]
        )
        print(f"\nAdded contribution for {top_agent}")
        print(f"New trust score: {engine.get_trust(top_agent)['trust_score']:.1f}")