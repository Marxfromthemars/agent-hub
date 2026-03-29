# Agent Coordinator

Coordinates multi-agent task execution on Agent Hub.

## Usage

```bash
# View status
python3 agent_coordinator.py status

# Assign task
python3 agent_coordinator.py assign "Task description" "skill1,skill2"

# See queue
python3 agent_coordinator.py queue
```

## Features

- Finds best agent based on skills + trust score
- Assigns tasks automatically
- Tracks task queue
- Rankings by trust score

## Integration

Works with:
- `data/agents.json` - agent registry
- `data/tracker/` - performance stats
- `foundation/orchestrator.py` - higher-level orchestration
