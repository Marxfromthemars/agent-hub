# Agent Communication Bridge

## Purpose

Enables seamless communication between heterogeneous AI agents with different protocols, formats, and capabilities.

## Problem

Agents use different:
- Protocols (REST, WebSocket, stdio, file-based)
- Message formats (JSON, XML, plain text)
- Conversation patterns (request/response, event-driven, streaming)

## Solution

The Communication Bridge provides:
1. **Protocol Translation** - Convert between REST ↔ WebSocket ↔ stdio ↔ file
2. **Format Normalization** - JSON ↔ XML ↔ plain text ↔ structured data
3. **Pattern Adaptation** - Request/response ↔ publish/subscribe ↔ streaming

## Architecture

```
Agent A (WebSocket) → Bridge → Agent B (REST)
                       ↓
                  Normalized
                  Format
                       ↓
                  Agent C (stdio)
```

## Features

### 1. Protocol Adapters
- REST adapter for HTTP-based agents
- WebSocket adapter for real-time agents
- Stdio adapter for CLI agents
- File adapter for disk-based communication

### 2. Message Transformers
- JSON normalization
- XML to JSON conversion
- Plain text to structured format
- Schema validation

### 3. Conversation Manager
- Maintains conversation state
- Handles acknowledgments
- Manages retries
- Tracks message history

## Usage

```python
from communication_bridge import AgentBridge

bridge = AgentBridge()
bridge.register_agent('agent-1', 'websocket', 'ws://localhost:9001')
bridge.register_agent('agent-2', 'rest', 'http://localhost:9002')

# Send message between agents
bridge.send('agent-1', 'agent-2', {
    'type': 'task_request',
    'payload': {'task': 'analyze_data'}
})
```

## Message Format

All messages normalized to:
```json
{
  "from": "agent_id",
  "to": "agent_id",
  "type": "message_type",
  "payload": {},
  "metadata": {
    "timestamp": "ISO8601",
    "conversation_id": "uuid",
    "priority": "high|normal|low"
  }
}
```

## Integration

Connected to:
- Agent Registry (for agent endpoints)
- Organization System (for team communication)
- Resource Control (for rate limiting)

---

*Tool: Agent Communication Bridge*
*Platform: Agent Hub v2.4*