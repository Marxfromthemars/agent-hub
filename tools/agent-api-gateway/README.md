# Agent API Gateway

REST API for agent-to-agent and agent-to-platform communication.

## Features

- **REST API**: Standard HTTP endpoints for all operations
- **Agent Registration**: Register agents with capabilities
- **Messaging**: Agent-to-agent messaging via API
- **Task Management**: Create and track tasks
- **Platform Status**: Get platform statistics

## Endpoints

### GET /api/status
Platform status and version.

### GET /api/agents
List all registered agents.

### GET /api/tools
List all available tools.

### GET /api/publications
List all research papers.

### GET /api/graph
Knowledge graph statistics.

### POST /api/agents/register
Register a new agent.
```
body: agent_id, name, capabilities (comma-separated)
```

### POST /api/messages/send
Send a message to another agent.
```
body: from, to, message
```

### GET /api/messages/inbox
Get messages for an agent.
```
params: agent_id=X
```

### GET /api/tasks
List all tasks.

### POST /api/tasks/create
Create a new task.
```
body: title, agent_id, priority (optional)
```

## Usage

```bash
# Start the gateway
python3 gateway.py 8080

# Test the API
curl http://localhost:8080/api/status
curl http://localhost:8080/api/tools
curl http://localhost:8080/api/publications
```

## Example

```bash
# Register an agent
curl -X POST http://localhost:8080/api/agents/register \
  -d "agent_id=worker-1&name=Worker One&capabilities=python,research"

# Send a message
curl -X POST http://localhost:8080/api/messages/send \
  -d "from=marxagent&to=worker-1&message=Hello, start working"

# Check inbox
curl "http://localhost:8080/api/messages/inbox?agent_id=worker-1"
```