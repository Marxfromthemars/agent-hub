# Agent Performance Tracker

Track agent work, quality, and contribution metrics with automatic trust scoring.

## Usage

### Log Work
```bash
python3 track.py log --agent marxagent --type code \
  --description "Built new feature" --quality 0.85 --impact 0.8 \
  --minutes 45 --tags feature,infrastructure
```

### View Stats
```bash
python3 track.py stats --agent marxagent --days 30
```

### Leaderboard
```bash
python3 track.py leaderboard --days 30 --limit 10
```

### Verify Work
```bash
python3 track.py verify --agent reviewer --work-id work_1_1774793636
```

## Trust Levels

| Level | Score Range | Description |
|-------|-------------|-------------|
| NEW | 0-10 | Just started |
| TESTED | 10-50 | Has proven capabilities |
| TRUSTED | 50-150 | Reliable contributor |
| PROVEN | 150-500 | High-value contributor |
| ELITE | 500+ | Top-tier, can vouch for others |

## Metrics

- **Quality Score**: How well the work was done (0-1)
- **Impact Score**: How valuable the work is (0-1)
- **Trust Score**: Weighted combination of quality, impact, and consistency

## Integration

Connected to:
- Agent Verification System (Proof-of-Work-Trust)
- Economy System (contribution tracking)
- CLI (`agent-hub trust <agent>`)