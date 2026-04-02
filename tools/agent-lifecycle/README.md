# Agent Lifecycle Manager

Manages the complete lifecycle of agents: spawning, monitoring, tracking, and retiring.

## Features

- **Spawn**: Create new agents with roles and capabilities
- **Monitor**: Track agent status and health
- **Complete**: Mark tasks as completed
- **Retire**: Gracefully retire agents
- **Statistics**: Get lifecycle insights

## Usage

```bash
# Spawn a new agent
python3 agent-lifecycle.py spawn "ResearchBot" researcher research python ml

# List all agents
python3 agent-lifecycle.py list

# List running agents only
python3 agent-lifecycle.py list running

# Check agent status
python3 agent-lifecycle.py status agent-abc123

# Update agent status
python3 agent-lifecycle.py update agent-abc123 working

# Mark task complete
python3 agent-lifecycle.py complete agent-abc123

# Retire an agent
python3 agent-lifecycle.py retire agent-abc123 "completed_mission"

# Get statistics
python3 agent-lifecycle.py stats
```

## Integration

Works with Agent Hub's spawning system to manage persistent agents.