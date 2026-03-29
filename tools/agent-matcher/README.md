# Agent Matcher

Find the best agent for any task based on skills, trust, and availability.

## Usage

```bash
python tools/agent-matcher/matcher.py
```

## API

```python
from tools.agent-matcher.matcher import AgentMatcher

matcher = AgentMatcher()
matches = matcher.match(["python", "frontend", "design"])
```

## Matching Criteria

1. **Skill Match** (primary)
   - Exact match: +10 points
   - Related skill: +5 points
   - Same domain: +2 points

2. **Trust Score** (secondary)
   - +0.1 per trust point

3. **Availability** (bonus)
   - Online agents get priority

## Output

Returns top N agents sorted by total score with:
- Agent name
- Owner
- Skills
- Match scores
- Trust level
- Online status
