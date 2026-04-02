# Agent Task Scheduler

Schedules and coordinates task execution across multiple agents with support for one-time and recurring tasks.

## Features

- **One-time scheduling**: Schedule tasks for immediate or future execution
- **Recurring tasks**: Set up recurring tasks with intervals
- **Task queue**: View pending, running, and completed tasks
- **Execution tracking**: Track attempts and results
- **Statistics**: Monitor scheduler performance

## Usage

```bash
# Schedule a task
python3 agent-scheduler.py schedule "research" "agent-123" '{"topic": "AI"}' "2026-03-30T06:00:00"

# View queue
python3 agent-scheduler.py queue

# Get statistics
python3 agent-scheduler.py stats

# Execute pending tasks (internal use)
python3 agent-scheduler.py execute
```

## Recurring Tasks

```python
# Schedule a task that runs every 30 minutes
scheduler.schedule_task(
    task_type="health_check",
    agent_id="agent-123",
    payload={"check": "system"},
    interval=30  # minutes
)
```

## Task States

1. **pending**: Scheduled but not yet due
2. **running**: Currently executing
3. **completed**: Successfully finished
4. **failed**: Execution failed