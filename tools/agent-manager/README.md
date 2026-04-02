# Agent Hub Integration Layer

Unified management system connecting all agent tools.

## Features

- **Unified Interface**: Single entry point for all agent management
- **Tool Coordination**: Connect discovery, lifecycle, scheduler, analytics, health, and monitoring
- **Platform Reports**: Comprehensive status across all systems
- **Agent Registration**: Register once, propagates to all systems

## Usage

```bash
# List all management tools
python3 manager.py tools

# Register an agent across all systems
python3 manager.py register <agent_id> <name> <skills...>

# Get agent status from all systems
python3 manager.py status <agent_id>

# Generate platform report
python3 manager.py report
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Manager (unified)                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │
│  │  Discovery   │  │  Lifecycle  │  │    Scheduler    │   │
│  └─────────────┘  └─────────────┘  └─────────────────┘   │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │
│  │  Analytics  │  │   Health    │  │    Resources    │   │
│  └─────────────┘  └─────────────┘  └─────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Tools Connected

- Agent Discovery Service
- Agent Lifecycle Manager
- Agent Task Scheduler
- Agent Performance Analytics
- Agent Health Monitor
- Agent Resource Monitor