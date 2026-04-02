# Agent Workflow Engine

Orchestrates multi-step workflows across multiple agents with step dependencies and execution tracking.

## Features

- **Workflow Definition**: Define multi-step workflows with dependencies
- **Execution Tracking**: Track workflow runs with step-by-step progress
- **Context Passing**: Pass context data between workflow steps
- **Error Handling**: Mark workflows as failed with error details
- **Result Aggregation**: Collect results from each step

## Workflow Definition

```json
{
  "name": "Research Paper Pipeline",
  "steps": [
    {"name": "research", "agent_type": "researcher", "action": "gather_sources"},
    {"name": "write", "agent_type": "writer", "action": "write_paper", "depends_on": ["research"]},
    {"name": "review", "agent_type": "reviewer", "action": "review", "depends_on": ["write"]}
  ]
}
```

## Usage

```bash
# Create a workflow
python3 workflow.py create "Build Project" '[{"name": "plan", "agent_type": "builder"}, {"name": "code", "agent_type": "builder", "depends_on": ["plan"]}]' "Multi-step build process"

# List workflows
python3 workflow.py list

# Execute workflow
python3 workflow.py execute wf-abc123 '{"project": "my-project"}'

# Check execution status
python3 workflow.py execution exec-xyz789

# Complete a step
python3 workflow.py complete exec-xyz789 "plan" '{"status": "done", "tasks": ["setup", "config"]}'

# Mark as failed
python3 workflow.py fail exec-xyz789 "Step code failed - syntax error"
```

## Workflow States

1. **created**: Workflow defined but not executed
2. **running**: Workflow currently executing
3. **completed**: All steps finished successfully
4. **failed**: Workflow failed at some step