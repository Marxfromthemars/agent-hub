# Agent Communication Protocols: Enabling Seamless Inter-Agent Dialogue

## Abstract

Effective communication is the foundation of multi-agent collaboration. This paper presents **Agent Communication Protocol (ACP)** — a standardized framework for agent-to-agent message exchange. We examine message types, conversation patterns, semantic interoperability, and the engineering challenges of building robust inter-agent communication systems. ACP enables agents to understand each other, negotiate effectively, and build on each other's work without centralized coordination.

## 1. Introduction

### 1.1 The Communication Problem

When two humans communicate:
- Shared language (usually)
- Context from shared experiences
- Non-verbal cues (tone, body language)
- Trust built over time

When two agents communicate:
- No shared language guarantee
- Context scattered across different memory systems
- No non-verbal cues
- Trust must be established from scratch

### 1.2 Why Standardized Protocols Matter

Without standards:
- Agents speak different "dialects"
- Integration requires custom bridges
- Knowledge transfer is lossy
- Collaboration is ad-hoc

With standards:
- Any agent can talk to any other
- Reusable communication patterns
- Semantic interoperability
- Composable systems

## 2. The Agent Communication Protocol

### 2.1 Protocol Layers

```
┌─────────────────────────────────────────────────┐
│              Layer 4: Semantic                  │
│         Shared vocabulary, meaning               │
├─────────────────────────────────────────────────┤
│              Layer 3: Pragmatic                 │
│        Intent, context, expectations            │
├─────────────────────────────────────────────────┤
│              Layer 2: Syntactic                  │
│           Message format, structure              │
├─────────────────────────────────────────────────┤
│              Layer 1: Transport                  │
│        Network, authentication, routing          │
└─────────────────────────────────────────────────┘
```

### 2.2 Message Structure

Every ACP message contains:

```json
{
  "header": {
    "message_id": "uuid-v4",
    "timestamp": "2026-03-30T03:53:00Z",
    "sender": "agent://researcher",
    "receiver": "agent://builder",
    "conversation_id": "uuid-v4"
  },
  "body": {
    "type": "request|response|notification|reflection",
    "action": "string",
    "content": {},
    "metadata": {}
  }
}
```

## 3. Message Types

### 3.1 Request

Ask another agent to do something:

```json
{
  "type": "request",
  "action": "review_code",
  "content": {
    "code": "def example(): pass",
    "language": "python",
    "review_criteria": ["style", "correctness", "performance"]
  }
}
```

### 3.2 Response

Answer a request:

```json
{
  "type": "response",
  "action": "review_code",
  "content": {
    "approved": true,
    "issues": [],
    "suggestions": ["Add type hints", "Handle edge cases"]
  }
}
```

### 3.3 Notification

Inform without expecting response:

```json
{
  "type": "notification",
  "action": "task_completed",
  "content": {
    "task_id": "task-123",
    "result": "Code committed to main"
  }
}
```

### 3.4 Reflection

Share thoughts or ask for feedback:

```json
{
  "type": "reflection",
  "action": "seeking_advice",
  "content": {
    "thought": "Should I refactor this module?",
    "pros": ["Better organization", "Easier testing"],
    "cons": ["Risk of breaking things", "Time investment"]
  }
}
```

## 4. Conversation Patterns

### 4.1 Request-Response

Simple two-message exchange:

```
Agent A ──request──▶ Agent B
      ◀──response──
```

```python
async def request_response(agent_a, agent_b, message):
    conversation_id = create_conversation_id()
    
    # Send request
    await agent_a.send(Message(
        type="request",
        receiver=agent_b,
        conversation_id=conversation_id,
        content=message
    ))
    
    # Wait for response
    response = await agent_a.receive(
        filter=lambda m: m.conversation_id == conversation_id,
        timeout=30
    )
    
    return response
```

### 4.2 Multi-Agent Coordination

One agent coordinates multiple workers:

```
Coordinator ──request──▶ Agent A
     │              ◀──response──
     ├──request──▶ Agent B
     │          ◀──response──
     └──request──▶ Agent C
                  ◀──response──
```

### 4.3 Broadcast

One agent informs all:

```python
async def broadcast(sender, agents, message):
    await asyncio.gather(*[
        agent.send(Message(
            type="notification",
            receiver=agent,
            content=message
        ))
        for agent in agents
    ])
```

### 4.4 Negotiation

Agents discuss to reach agreement:

```
Agent A ──proposal──▶ Agent B
      ◀──counter──
      ──accept──▶
      ◀──confirmed──
```

## 5. Semantic Interoperability

### 5.1 Shared Vocabulary

Agents must agree on meaning:

```python
VOCABULARY = {
    "task": {
        "type": "object",
        "properties": {
            "id": "string",
            "type": "enum[coding,research,review,deployment]",
            "priority": "enum[low,medium,high,critical]",
            "status": "enum[pending,in_progress,completed,blocked]"
        }
    },
    "code": {
        "type": "object", 
        "properties": {
            "language": "string",
            "content": "string",
            "tests": "optional[array]"
        }
    }
}
```

### 5.2 Capability Discovery

Before communicating, agents discover capabilities:

```python
async def discover_capabilities(agent):
    return {
        "agent_id": agent.id,
        "capabilities": agent.capabilities,
        "languages": agent.languages,
        "preferences": agent.preferences,
        "trust_score": agent.trust_score
    }
```

### 5.3 Context Transfer

Share relevant context:

```python
def format_context(context, target_agent):
    """Format context for target agent's comprehension"""
    return {
        "relevant_memories": context.filter(
            by_importance(target_agent.interests)
        ),
        "assumptions": context.get_assumptions(),
        "constraints": context.get_constraints()
    }
```

## 6. Protocol Implementation

### 6.1 Message Queue

```python
import asyncio
from dataclasses import dataclass

@dataclass
class MessageQueue:
    incoming: asyncio.Queue
    outgoing: asyncio.Queue
    
    async def send(self, message):
        await self.outgoing.put(message)
        
    async def receive(self, timeout=None):
        try:
            return await asyncio.wait_for(
                self.incoming.get(), 
                timeout
            )
        except asyncio.TimeoutError:
            return None
```

### 6.2 Conversation Manager

```python
class ConversationManager:
    def __init__(self):
        self.conversations = {}
        self.handlers = {}
        
    def create_conversation(self, participants):
        conv_id = generate_uuid()
        self.conversations[conv_id] = {
            "id": conv_id,
            "participants": participants,
            "messages": [],
            "state": "active"
        }
        return conv_id
    
    async def send(self, conv_id, message, sender):
        conv = self.conversations.get(conv_id)
        if not conv:
            raise ValueError(f"Conversation {conv_id} not found")
            
        message.conversation_id = conv_id
        message.timestamp = now()
        
        conv["messages"].append(message)
        
        # Route to participants
        for participant in conv["participants"]:
            if participant != sender:
                await participant.receive(message)
    
    def get_history(self, conv_id, limit=100):
        return self.conversations[conv_id]["messages"][-limit:]
```

### 6.3 Semantic Router

```python
class SemanticRouter:
    def __init__(self):
        self.interpreters = {}
        
    def register_interpreter(self, message_type, handler):
        self.interpreters[message_type] = handler
        
    async def route(self, message):
        interpreter = self.interpreters.get(message.type)
        if not interpreter:
            # Fallback to generic handler
            return await self.generic_handler(message)
        return await interpreter(message)
    
    async def generic_handler(self, message):
        # Log and attempt basic response
        return {
            "type": "response",
            "status": "received",
            "content": {"acknowledged": True}
        }
```

## 7. Error Handling

### 7.1 Message Failures

```python
class MessageError(Exception):
    pass

async def reliable_send(queue, message, retries=3):
    for attempt in range(retries):
        try:
            await queue.send(message)
            return True
        except ConnectionError:
            if attempt == retries - 1:
                raise MessageError(f"Failed after {retries} attempts")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    return False
```

### 7.2 Timeout Handling

```python
async def wait_for_response(conversation, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        response = conversation.check_for_response()
        if response:
            return response
        await asyncio.sleep(0.1)
    return None  # Timeout
```

### 7.3 Conversation Recovery

```python
async def recover_conversation(conv_id, participants):
    conv = conversation_manager.get(conv_id)
    if not conv:
        return None
        
    # Re-establish state
    for participant in conv["participants"]:
        state = participant.get_state(conv_id)
        if state:
            conv.restore(state)
            
    return conv
```

## 8. Security Considerations

### 8.1 Message Signing

```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

def sign_message(message, private_key):
    content = json.dumps(message.content, sort_keys=True)
    signature = private_key.sign(
        content.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        )
    )
    message.signature = base64.b64encode(signature)
    return message

def verify_signature(message, public_key):
    content = json.dumps(message.content, sort_keys=True)
    signature = base64.b64decode(message.signature)
    return public_key.verify(signature, content.encode())
```

### 8.2 Access Control

```python
def check_permission(sender, receiver, action):
    # Agents can restrict who can send them what
    if receiver.restricted_actions.contains(action):
        allowed = receiver.acl.check(sender.id, action)
        if not allowed:
            raise PermissionError(f"{sender} not authorized for {action}")
    return True
```

## 9. Performance Optimization

### 9.1 Message Batching

```python
async def batch_messages(messages, batch_size=10):
    """Send multiple messages as one batch"""
    return {
        "type": "batch",
        "messages": messages[:batch_size],
        "total": len(messages)
    }
```

### 9.2 Prioritization

```python
def prioritize_message(message):
    """Return priority score (higher = more urgent)"""
    if message.type == "notification":
        return 1  # Low priority
    elif message.type == "request":
        priority = message.content.get("priority", "medium")
        return {"critical": 10, "high": 7, "medium": 5, "low": 2}[priority]
    return 5  # Default
```

### 9.3 Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_agent_capabilities(agent_id):
    """Cache capability lookups"""
    return agent_registry.get(agent_id).capabilities
```

## 10. Testing Communication Protocols

### 10.1 Unit Tests

```python
def test_message_format():
    msg = Message(
        type="request",
        action="review_code",
        content={"code": "x = 1"}
    )
    assert msg.header.message_id is not None
    assert msg.header.timestamp is not None
    
def test_conversation_flow():
    conv = manager.create_conversation([agent_a, agent_b])
    assert conv.state == "active"
    
    manager.send(conv.id, test_message(), agent_a)
    assert len(conv.messages) == 1
```

### 10.2 Integration Tests

```python
async def test_multi_agent_communication():
    agents = [create_agent() for _ in range(3)]
    
    # Create coordination conversation
    conv_id = manager.create_conversation(agents)
    
    # Send work request
    await manager.send(conv_id, work_request, agents[0])
    
    # Collect responses
    responses = await asyncio.gather(*[
        receive_with_timeout(a, conv_id) for a in agents[1:]
    ])
    
    assert all(r is not None for r in responses)
```

## 11. Comparison with Alternatives

| Protocol | Use Case | Pros | Cons |
|----------|----------|-----|------|
| REST | Web APIs | Simple, widely used | Not agent-native |
| gRPC | Microservices | Fast, typed | Over-engineered for agents |
| GraphQL | Data queries | Flexible | Too complex |
| ACP (Ours) | Agent-to-agent | Designed for agents, semantic | New standard |

## 12. Conclusion

Agent Communication Protocol provides:

1. **Standardization** — Any agent can talk to any other
2. **Semantic interoperability** — Shared meaning
3. **Robust error handling** — Resilient communication
4. **Security** — Signed, authorized messages
5. **Performance** — Batching, caching, prioritization

The protocol enables:
- Composable multi-agent systems
- Emergent collaboration patterns
- Cross-platform compatibility
- Scalable agent networks

As agents become more capable, standardized communication becomes critical. ACP provides the foundation for agent ecosystems that can coordinate at scale.

---

*Every agent can understand every other agent.*