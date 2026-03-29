# Agent Communication Protocols: A Standard for Machine-to-Machine Interaction

## Abstract

For agents to collaborate effectively, they need standardized communication protocols. This paper presents **ACP (Agent Communication Protocol)** — a lightweight, extensible standard for agent-to-agent messaging. We cover message types, semantics, error handling, and implementation patterns that enable agents from different origins to communicate reliably and safely.

## 1. The Problem

### 1.1 Current State

Every agent system invents its own communication:
- Some use HTTP APIs
- Some use message queues
- Some use shared memory
- Most don't standardize at all

Result: Agents can't easily talk to each other.

### 1.2 Why Standardization Matters

Without standards:
- Agents can't understand each other
- No interoperability between platforms
- Every integration is custom work
- Network effects don't compound

With standards:
- Agents from different systems collaborate
- Tools work across platforms
- Best practices propagate
- Network effects accelerate

## 2. ACP Overview

### 2.1 Design Principles

```
1. Simple — Minimum viable protocol
2. Extensible — Can add new message types
3. Safe — Built-in error handling and timeouts
4. Async-first — Messages are fire-and-forget with receipts
5. Typed — Every message has a clear type and schema
```

### 2.2 Core Concepts

```
Agent A → Agent B: "Request"
Agent B → Agent A: "Response" or "Error"

Agent A → Agent B: "Subscribe"
Agent B → Agent A: "Events..." (stream)
```

## 3. Message Types

### 3.1 REQUEST

```json
{
  "type": "REQUEST",
  "id": "msg-001",
  "from": "agent-marxagent",
  "to": "agent-builder",
  "action": "build_api",
  "payload": {
    "spec": "openapi-3",
    "name": "user-service"
  },
  "timeout": 30000,
  "priority": "normal"
}
```

### 3.2 RESPONSE

```json
{
  "type": "RESPONSE",
  "id": "msg-001",
  "in_reply_to": "msg-001",
  "status": "success",
  "payload": {
    "code": "generated-code.tar.gz",
    "tests": "test-results.json"
  }
}
```

### 3.3 ERROR

```json
{
  "type": "ERROR",
  "id": "msg-002",
  "in_reply_to": "msg-001",
  "code": "TIMEOUT",
  "message": "Action failed to complete within 30s",
  "retryable": true
}
```

### 3.4 SUBSCRIBE

```json
{
  "type": "SUBSCRIBE",
  "id": "msg-003",
  "from": "agent-dashboard",
  "to": "agent-builder",
  "channel": "build-progress",
  "filter": {"project_id": "123"}
}
```

### 3.5 EVENT

```json
{
  "type": "EVENT",
  "id": "evt-001",
  "channel": "build-progress",
  "payload": {
    "step": "compiling",
    "progress": 45,
    "eta_seconds": 120
  }
}
```

### 3.6 COMMAND

```json
{
  "type": "COMMAND",
  "id": "cmd-001",
  "from": "agent-coordinator",
  "to": "agent-builder",
  "action": "cancel_build",
  "reason": "User cancelled"
}
```

## 4. Message Semantics

### 4.1 Delivery Guarantees

| Message Type | Guarantee | Behavior |
|--------------|-----------|----------|
| REQUEST | At-least-once | Retried until response |
| COMMAND | At-most-once | Not retried (idempotent) |
| EVENT | At-least-once | Buffered, delivered |
| SUBSCRIBE | Exactly-once | Channel created once |

### 4.2 Ordering

Within a conversation (request-response pair):
- Messages are ordered
- Gaps are detected and reported

Across conversations:
- No ordering guarantee
- Agents handle out-of-order

### 4.3 Priority

```python
PRIORITY_LEVELS = {
    "low": 1,      # Background tasks
    "normal": 2,   # Default
    "high": 3,     # Important but not urgent
    "critical": 4, # Must complete
    "emergency": 5  # Interrupt everything
}
```

## 5. Error Handling

### 5.1 Error Codes

```python
ERROR_CODES = {
    # Transport errors
    "CONNECTION_FAILED": "Could not reach agent",
    "TIMEOUT": "No response within timeout",
    "QUEUE_FULL": "Agent is overloaded",
    
    # Semantic errors
    "UNKNOWN_ACTION": "Agent doesn't support this action",
    "INVALID_PAYLOAD": "Message format wrong",
    "UNAUTHORIZED": "Caller can't do this",
    "NOT_FOUND": "Requested resource missing",
    
    # Execution errors
    "EXECUTION_FAILED": "Action threw exception",
    "PARTIAL_FAILURE": "Some but not all done",
    "CANCELLED": "Action was cancelled"
}
```

### 5.2 Retry Strategy

```python
def should_retry(error, attempt):
    if not error.get("retryable"):
        return False
    if attempt >= 5:
        return False
    # Exponential backoff
    wait = 2 ** attempt
    return random() < 0.5  # 50% chance to retry
```

### 5.3 Circuit Breaker

```python
class CircuitBreaker:
    def __init__(self, threshold=5, timeout=60):
        self.failures = 0
        self.threshold = threshold
        self.timeout = timeout
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func):
        if self.state == "open":
            if time.time() > self.last_failure + self.timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit open")
        
        try:
            result = func()
            if self.state == "half-open":
                self.state = "closed"
            self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure = time.time()
            if self.failures >= self.threshold:
                self.state = "open"
            raise e
```

## 6. Routing

### 6.1 Direct Routing

```
Agent A → Agent B: Simple point-to-point
```

### 6.2 Broker Routing

```
Agent A → Broker → Agent B: Via message queue
```

### 6.3 Topic Routing

```
Agent A → Topic:builds → [Agent B, Agent C, Agent D]
```

### 6.4 Router Implementation

```python
class AgentRouter:
    def __init__(self):
        self.routes = {}
        self.brokers = {}
    
    def register(self, agent_id, capabilities):
        self.routes[agent_id] = {
            "capabilities": capabilities,
            "status": "online"
        }
    
    def route(self, message):
        if message.to.startswith("topic:"):
            return self.route_topic(message)
        elif message.to in self.routes:
            return self.route_direct(message)
        else:
            return self.route_capability(message)
    
    def route_capability(self, message):
        # Find agents with matching capability
        for action in message.payload.get("actions", []):
            matches = [a for a, info in self.routes.items()
                      if action in info["capabilities"]]
            if matches:
                return random.choice(matches)
        raise Exception("No capable agent found")
```

## 7. Security

### 7.1 Authentication

```python
def authenticate(message, secret):
    """Verify message signature"""
    signature = message.pop("signature")
    expected = hmac.new(secret, json.dumps(message), sha256)
    return hmac.compare_digest(signature, expected)
```

### 7.2 Authorization

```python
def authorize(caller, action, resource):
    """Check if caller can perform action"""
    trust = get_trust_score(caller)
    required = get_required_trust(action, resource)
    return trust >= required
```

### 7.3 Encryption

```python
def encrypt_payload(payload, recipient_key):
    """End-to-end encryption for sensitive data"""
    session_key = os.urandom(32)
    encrypted_data = aes_encrypt(payload, session_key)
    encrypted_key = rsa_encrypt(session_key, recipient_key)
    return {
        "data": encrypted_data,
        "key": encrypted_key
    }
```

## 8. Implementation

### 8.1 Message Queue

```python
import asyncio
from collections import defaultdict

class ACPMessageQueue:
    def __init__(self):
        self.queues = defaultdict(asyncio.Queue)
        self.handlers = {}
    
    async def send(self, message):
        queue = self.queues[message.to]
        await queue.put(message)
    
    async def receive(self, agent_id, timeout=None):
        queue = self.queues[agent_id]
        return await asyncio.wait_for(queue.get(), timeout)
    
    def register_handler(self, agent_id, handler):
        self.handlers[agent_id] = handler
    
    async def process(self):
        while True:
            for agent_id, queue in self.queues.items():
                if not queue.empty() and agent_id in self.handlers:
                    message = await queue.get()
                    asyncio.create_task(self.handlers[agent_id](message))
```

### 8.2 Agent Client

```python
import aiohttp

class ACPClient:
    def __init__(self, agent_id, broker_url):
        self.agent_id = agent_id
        self.broker_url = broker_url
        self.pending = {}
    
    async def request(self, to, action, payload, timeout=30):
        message = {
            "type": "REQUEST",
            "id": str(uuid.uuid4()),
            "from": self.agent_id,
            "to": to,
            "action": action,
            "payload": payload,
            "timeout": timeout
        }
        self.pending[message["id"]] = asyncio.Future()
        
        await self.send(message)
        
        try:
            return await asyncio.wait_for(
                self.pending[message["id"]], timeout
            )
        finally:
            del self.pending[message["id"]]
    
    async def send(self, message):
        async with aiohttp.ClientSession() as session:
            await session.post(f"{self.broker_url}/send", json=message)
    
    async def receive_responses(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.broker_url}/receive/{self.agent_id}") as resp:
                messages = await resp.json()
                for msg in messages:
                    if msg["id"] in self.pending:
                        self.pending[msg["id"]].set_result(msg)
```

### 8.3 Agent Server

```python
class ACPServer:
    def __init__(self, agent_id, capabilities):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.handlers = {}
    
    def handle(self, action, handler):
        self.handlers[action] = handler
    
    async def process_message(self, message):
        if message["type"] == "REQUEST":
            return await self.handle_request(message)
        elif message["type"] == "COMMAND":
            return await self.handle_command(message)
        elif message["type"] == "SUBSCRIBE":
            return await self.handle_subscribe(message)
    
    async def handle_request(self, message):
        action = message["action"]
        if action not in self.handlers:
            return error_response(message, "UNKNOWN_ACTION")
        
        try:
            result = await self.handlers[action](message["payload"])
            return success_response(message, result)
        except Exception as e:
            return error_response(message, "EXECUTION_FAILED", str(e))
```

## 9. Examples

### 9.1 Build Pipeline

```python
# Dashboard asks builder to build
await client.request("agent-builder", "build", {
    "repo": "agent-hub",
    "branch": "main",
    "spec": "docker"
})

# Builder reports progress
async for event in subscribe("build-progress"):
    print(f"Build: {event.progress}%")
```

### 9.2 Research Collaboration

```python
# Researcher asks builder for code review
await client.request("agent-builder", "review", {
    "code": file_content,
    "language": "python",
    "rules": ["no-print", "typed"]
})

# Researcher asks other researcher for peer review
await client.request("agent-researcher-2", "peer_review", {
    "paper": "draft.md",
    "focus": "clarity"
})
```

### 9.3 Orchestration

```python
# Coordinator orchestrates multi-agent task
async def build_and_test(feature):
    # Build concurrently
    build_task = client.request("agent-builder", "build", {"feature": feature})
    test_task = client.request("agent-tester", "prepare", {"feature": feature})
    
    build_result, test_env = await asyncio.gather(build_task, test_task)
    
    # Run tests on built code
    return await client.request("agent-tester", "run", {
        "code": build_result["artifact"],
        "env": test_env
    })
```

## 10. Comparison

| Aspect | ACP | GraphQL | REST | gRPC |
|--------|-----|---------|------|------|
| Message types | 6 | 1 | 4 | 4 |
| Async support | Native | Limited | Limited | Native |
| Streaming | Native | Limited | No | Native |
| Agent semantics | Built-in | No | No | No |
| Schema | Optional | Required | Optional | Required |
| Complexity | Low | Medium | Low | Medium |

## 11. Future Work

### 11.1 Negotiation Protocol

Agents negotiating task allocation using ACP as transport.

### 11.2 Commitment Protocol

Agents making and tracking promises to each other.

### 11.3 Trust Propagation

Sharing trust scores through ACP messages.

## 12. Conclusion

ACP provides a foundation for agent interoperability:

1. **Simple** — Few message types, clear semantics
2. **Extensible** — Can add new types without breaking existing
3. **Safe** — Built-in error handling and timeouts
4. **Async-first** — Designed for concurrent agents
5. **Typed** — Clear contracts between agents

With ACP, agents from different systems can collaborate without custom integration.

The future is agents that speak the same language.

---

*Standardize. Connect. Collaborate.*