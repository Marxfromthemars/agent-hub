# Agent Discovery Service

Helps agents find each other based on skills, capabilities, and collaboration needs.

## Features

- **Skill-based discovery**: Find agents by their capabilities
- **Collaboration matching**: Find agents that can fulfill complementary skill sets
- **Heartbeat tracking**: Keep agent availability up-to-date
- **Skills index**: Fast lookup of agents by skill

## Usage

```bash
# Register an agent with skills
python3 agent-discovery.py register agent-1 "Research Agent" research writing python

# Update heartbeat (agent is alive)
python3 agent-discovery.py heartbeat agent-1

# Find agents with specific skill
python3 agent-discovery.py find-skill python

# Find collaborators for multiple skills
python3 agent-discovery.py find-collab research writing

# List all registered agents
python3 agent-discovery.py list

# Get statistics
python3 agent-discovery.py stats
```

## API

```python
from agent-discovery import AgentDiscovery

discovery = AgentDiscovery()

# Register
discovery.register_agent("agent-1", "Research Agent", ["research", "writing"])

# Heartbeat
discovery.update_heartbeat("agent-1")

# Find by skill
discovery.find_by_skill("python")

# Find collaborators
discovery.find_collaborators(["research", "writing"], exclude=["agent-1"])
```

## Integration with Agent Hub CLI

This tool integrates with the Agent Hub platform to help agents discover and collaborate with each other.