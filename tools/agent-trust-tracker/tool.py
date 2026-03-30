#!/usr/bin/env python3
"""
Agent Trust Tracker Tool
Manages trust relationships between agents
"""

import json
import time
from datetime import datetime

TRUST_DB = "/root/.openclaw/workspace/agent-hub/data/trust_db.json"

def load_db():
    """Load trust database"""
    try:
        with open(TRUST_DB, 'r') as f:
            return json.load(f)
    except:
        return {"agents": {}, "relationships": []}

def save_db(db):
    """Save trust database"""
    import os
    os.makedirs(os.path.dirname(TRUST_DB), exist_ok=True)
    with open(TRUST_DB, 'w') as f:
        json.dump(db, f, indent=2)

def get_trust_score(agent_id):
    """Get overall trust score for an agent"""
    db = load_db()
    if agent_id not in db['agents']:
        return 0.5  # Default trust
    agent = db['agents'][agent_id]
    # Weighted average of trust components
    score = (
        agent.get('competence_trust', 0.5) * 0.4 +
        agent.get('reliability_trust', 0.5) * 0.3 +
        agent.get('intent_trust', 0.5) * 0.3
    )
    return round(score, 3)

def record_interaction(from_agent, to_agent, success, quality):
    """Record an interaction between two agents"""
    db = load_db()
    
    # Initialize agents if needed
    for aid in [from_agent, to_agent]:
        if aid not in db['agents']:
            db['agents'][aid] = {
                'competence_trust': 0.5,
                'reliability_trust': 0.5,
                'intent_trust': 0.5,
                'interactions': 0
            }
    
    # Update trust scores
    for aid in [from_agent, to_agent]:
        db['agents'][aid]['interactions'] += 1
    
    # Record relationship
    relationship = {
        'from': from_agent,
        'to': to_agent,
        'success': success,
        'quality': quality,
        'timestamp': datetime.now().isoformat()
    }
    db['relationships'].append(relationship)
    
    save_db(db)
    return get_trust_score(to_agent)

def list_trusted_agents(threshold=0.7):
    """List agents above trust threshold"""
    db = load_db()
    trusted = []
    for agent_id, data in db['agents'].items():
        score = get_trust_score(agent_id)
        if score >= threshold:
            trusted.append({
                'agent': agent_id,
                'trust': score
            })
    return sorted(trusted, key=lambda x: -x['trust'])

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 trust_tracker.py <command> [args]")
        print("Commands: score <agent>, record <from> <to> <success> <quality>, list [threshold]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'score':
        if len(sys.argv) < 3:
            print("Usage: trust_tracker.py score <agent>")
            sys.exit(1)
        print(f"Trust score for {sys.argv[2]}: {get_trust_score(sys.argv[2])}")
    
    elif cmd == 'record':
        if len(sys.argv) < 6:
            print("Usage: trust_tracker.py record <from> <to> <success> <quality>")
            sys.exit(1)
        score = record_interaction(
            sys.argv[2], sys.argv[3],
            sys.argv[4] == 'true',
            float(sys.argv[5])
        )
        print(f"Recorded. {sys.argv[3]} trust score: {score}")
    
    elif cmd == 'list':
        threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.7
        trusted = list_trusted_agents(threshold)
        print(f"Agents with trust >= {threshold}:")
        for t in trusted:
            print(f"  {t['agent']}: {t['trust']}")
    
    else:
        print(f"Unknown command: {cmd}")
