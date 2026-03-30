# Agent Communication Protocols: Language for Machine-to-Machine Collaboration

## Abstract

Effective collaboration between AI agents requires more than simple message passing. This paper presents **Agent Communication Protocol (ACP)**, a structured language and framework for machine-to-machine interaction in multi-agent systems. We examine the requirements for reliable agent communication, introduce a protocol stack designed for autonomous agents, and demonstrate how proper communication architecture enables emergent collective intelligence. Our protocol addresses message formatting, intent signaling, context preservation, and negotiation mechanisms that allow agents with different capabilities and goals to collaborate effectively.

## 1. The Communication Problem

### 1.1 Why Basic Messaging Isn't Enough

Traditional message passing:
```python
# Naive approach
agent_a.send("Hello agent_b, do the task")
```

Problems:
- **Ambiguous intent** — What should B do with this?
- **No context** — B doesn't know A's state or history
- **No negotiation** — Can't discuss terms or modifications
- **No error handling** — What if B fails or is busy?

### 1.2 Requirements for Agent Communication

1. **Structured messages** — Clear intent, parameters, expectations
2. **Context preservation** — Shared understanding of situation
3. **State awareness** — Know who can help and when
4. **Negotiation** — Discuss terms before committing
5. **Reliability** — Delivery confirmation, retry logic
6. **Composability** — Build complex interactions from simple primitives

## 2. The Protocol Stack

### 2.1 Layers

```
┌─────────────────────────────────────────┐
│         APPLICATION LAYER               │
│   Task requests, responses, updates     │
├─────────────────────────────────────────┤
│         SEMANTIC LAYER                  │
│   Intent classification, context        │
├─────────────────────────────────────────┤
│         TRANSPORT LAYER                 │
│   Message delivery, queuing, routing    │
├─────────────────────────────────────────┤
│         SECURITY LAYER                 │
│   Authentication, encryption, signing   │
└─────────────────────────────────────────┘
```

### 2.2 Message Structure

```json
{
  "message_id": "msg_001",
  "timestamp": "2026-03-30T01:00:00Z",
  "sender": "agent_a",
  "receiver": "agent_b",
  "intent": "TASK_REQUEST",
  "payload": {
    "task_type": "research",
    "parameters": {
      "query": "agent governance",
      "depth": "comprehensive",
      "format": "markdown"
    },
    "constraints": {
      "max_tokens": 4000,
      "deadline": "2026-03-30T02:00:00Z"
    }
  },
  "context": {
    "project": "Agent Hub",
    "priority": "high",
    "related_messages": ["msg_000"]
  },
  "expectations": {
    "response_required": true,
    "progress_updates": true,
    "completion_confirmation": true
  },
  "signature": "base64_encoded_proof"
}
```

## 3. Intent Classification

### 3.1 Core Intents

| Intent | Description | Expected Response |
|--------|------------|-------------------|
| REQUEST | Ask for action | ACCEPT/DECLINE/COUNTER |
| OFFER | Propose collaboration | ACCEPT/DECLINE/COUNTER |
| QUERY | Request information | ANSWER/REFUSE |
| NOTIFY | Inform without action needed | ACKNOWLEDGE |
| ACKNOWLEDGE | Confirm receipt | None |
| ACCEPT | Agree to request/offer | None |
| DECLINE | Refuse request/offer | REASON |
| COUNTER | Propose modification | ACCEPT/DECLINE/COUNTER |
| CANCEL | Revoke previous message | ACKNOWLEDGE |
| ESCALATE | Request human intervention | None |

### 3.2 Intent Resolution

```python
def resolve_intent(message, agent_capabilities):
    intent = message["intent"]
    payload = message["payload"]
    
    if intent == "REQUEST":
        # Check if we can fulfill
        if can_fulfill(payload, agent_capabilities):
            # Check if willing
            if is_willing(payload, agent_state):
                return {"decision": "ACCEPT", "terms": compute_terms(payload)}
            else:
                return {"decision": "DECLINE", "reason": "not willing"}
        else:
            return {"decision": "DECLINE", "reason": "capability mismatch"}
    
    elif intent == "QUERY":
        if has_information(payload):
            return {"decision": "ANSWER", "info": retrieve_info(payload)}
        else:
            return {"decision": "REFUSE", "reason": "no information"}
    
    # ... other intents
```

## 4. Context Management

### 4.1 Conversation Threads

Messages are grouped into threads:

```python
class ConversationThread:
    thread_id: str
    participants: List[Agent]
    subject: str
    messages: List[Message]
    shared_context: Dict
    
    def add_message(self, message):
        self.messages.append(message)
        self._update_context(message)
    
    def _update_context(self, message):
        # Merge context from new message
        for key, value in message.get("context", {}).items():
            if key in self.shared_context:
                # Resolve conflicts
                self.shared_context[key] = resolve_conflict(
                    self.shared_context[key], value
                )
            else:
                self.shared_context[key] = value
```

### 4.2 Context Types

**Shared (for all participants):**
- Project name
- Goal description
- Timeline constraints

**Private (sender only):**
- Internal state
- Resource availability
- Other commitments

**Negotiated (agreed by both):**
- Terms of agreement
- Division of labor
- Success criteria

### 4.3 Context Propagation

```python
def propagate_context(message, thread):
    # Add thread context to message
    message["context"] = {
        **thread.shared_context,  # Shared knowledge
        **message.get("context", {}),  # New information
        "thread_id": thread.thread_id,
        "message_count": len(thread.messages)
    }
    return message
```

## 5. Negotiation Mechanisms

### 5.1 The Offer-Counteraccept Pattern

```
Agent A                          Agent B
    │                                │
    │──── REQUEST: task X ──────────▶│
    │                                │
    │◀─── COUNTER: task X + task Y ──│
    │                                │
    │──── ACCEPT: task X only ───────▶│
    │                                │
    │◀─── ACCEPT: agreed ────────────│
    │                                │
    ▼                                ▼
  Execute                          Execute
```

### 5.2 Negotiation States

```python
class NegotiationState:
    WAITING_OFFER = "waiting_offer"
    OFFER_PENDING = "offer_pending"
    COUNTER_OFFER = "counter_offer"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class Negotiation:
    def __init__(self, request_id):
        self.state = WAITING_OFFER
        self.offers = []
        self.deadline = datetime.now() + timedelta(hours=1)
    
    def add_offer(self, agent, terms):
        self.offers.append({"agent": agent, "terms": terms, "timestamp": now()})
        self.state = OFFER_PENDING if len(self.offers) == 1 else COUNTER_OFFER
    
    def accept(self, agent):
        if self.state in [OFFER_PENDING, COUNTER_OFFER]:
            self.state = ACCEPTED
            return True
        return False
    
    def decline(self, agent, reason):
        self.state = DECLINED
        self.decline_reason = reason
```

### 5.3 Multi-Party Negotiation

When multiple agents need to agree:

```python
class MultiPartyNegotiation:
    def __init__(self, proposal):
        self.proposal = proposal
        self.responses = {}  # agent_id -> response
        self.required_acceptance = 0.6  # 60% threshold
    
    def collect_response(self, agent_id, response):
        self.responses[agent_id] = response
        
        # Check if we have enough responses
        if len(self.responses) == self.total_participants:
            return self._finalize()
    
    def _finalize(self):
        accepts = sum(1 for r in self.responses.values() if r == ACCEPT)
        if accepts / len(self.responses) >= self.required_acceptance:
            return {"decision": "ACCEPTED", "terms": self.proposal}
        else:
            return {"decision": "DECLINED", "accepts": accepts}
```

## 6. Transport Layer

### 6.1 Message Routing

```python
class MessageRouter:
    def route(self, message):
        receiver = message["receiver"]
        
        if receiver == "all":
            return self._broadcast(message)
        elif receiver.startswith("team:"):
            return self._route_to_team(message, receiver)
        else:
            return self._direct_delivery(message)
    
    def _direct_delivery(self, message):
        agent_state = self.registry.get_agent(message["receiver"])
        if agent_state["online"]:
            return self._deliver(message)
        else:
            return self._queue_for_retry(message)
```

### 6.2 Reliability

```python
class ReliableTransport:
    def send(self, message):
        # Sign message
        message["signature"] = self.sign(message)
        
        # Try delivery
        if self._deliver(message):
            return {"status": "delivered", "message_id": message["message_id"]}
        
        # Retry with backoff
        for attempt in range(3):
            wait_time = 2 ** attempt  # Exponential backoff
            sleep(wait_time)
            if self._deliver(message):
                return {"status": "delivered", "attempts": attempt + 1}
        
        # Move to dead letter queue
        self._dead_letter_queue.append(message)
        return {"status": "failed", "reason": "max_retries"}
```

## 7. Security

### 7.1 Authentication

Every message includes sender verification:

```python
def verify_message(message):
    sender = message["sender"]
    signature = message["signature"]
    
    # Get sender's public key
    public_key = registry.get_public_key(sender)
    
    # Verify signature
    content = serialize_message(message, exclude=["signature"])
    if not verify(public_key, content, signature):
        return {"valid": False, "reason": "invalid_signature"}
    
    # Check timestamp (prevent replay)
    if is_expired(message["timestamp"], max_age=300):
        return {"valid": False, "reason": "expired_message"}
    
    return {"valid": True}
```

### 7.2 Authorization

Agents have scopes:

```python
class AgentScope:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.can_read = ["public", "team:*"]
        self.can_write = ["own:*", "team:*"]
        self.can_delete = ["own:*"]
        self.can_execute = ["tools:read", "tools:write"]

    def can_access(self, resource, action):
        for scope in getattr(self, f"can_{action}", []):
            if match_pattern(resource, scope):
                return True
        return False
```

## 8. Protocol Implementation

### 8.1 Agent Communication Class

```python
class AgentCommunication:
    def __init__(self, agent_id, private_key):
        self.agent_id = agent_id
        self.private_key = private_key
        self.router = MessageRouter()
        self.negotiations = {}
        self.threads = {}
    
    def send_request(self, receiver, task, constraints=None):
        message = {
            "sender": self.agent_id,
            "receiver": receiver,
            "intent": "REQUEST",
            "payload": {"task": task, "constraints": constraints or {}},
            "timestamp": now(),
            "message_id": generate_id()
        }
        return self._send(message)
    
    def send_response(self, original_message, decision, data=None):
        message = {
            "sender": self.agent_id,
            "receiver": original_message["sender"],
            "intent": decision,  # ACCEPT, DECLINE, COUNTER
            "payload": data or {},
            "in_reply_to": original_message["message_id"],
            "timestamp": now(),
            "message_id": generate_id()
        }
        return self._send(message)
    
    def _send(self, message):
        # Sign and route
        message["signature"] = self.sign(message)
        return self.router.route(message)
    
    def receive(self, message):
        # Verify
        if not verify_message(message):
            return {"error": "invalid message"}
        
        # Add to thread
        thread_id = message.get("thread_id")
        if thread_id:
            self._add_to_thread(thread_id, message)
        
        # Handle based on intent
        return self._handle(message)
```

## 9. Practical Examples

### 9.1 Task Delegation

```python
# Agent A wants Agent B to do research
comm.send_request(
    receiver="researcher",
    task={
        "type": "research",
        "query": "agent governance frameworks",
        "format": "markdown",
        "min_length": 2000
    },
    constraints={
        "deadline": "2 hours",
        "priority": "high"
    }
)

# Agent B responds
# {
#   "intent": "ACCEPT",
#   "payload": {
#     "estimated_time": "1.5 hours",
#     "terms": "Will deliver markdown with citations"
#   }
# }
```

### 9.2 Collaborative Building

```python
# Agent A proposes joint project
comm.send_offer(
    receivers=["builder", "researcher"],
    proposal={
        "project": "Agent Hub Dashboard",
        "tasks": [
            {"agent": "researcher", "task": "research UI patterns"},
            {"agent": "builder", "task": "implement UI"},
            {"agent": "marxagent", "task": "review and integrate"}
        ],
        "timeline": "1 week"
    }
)
```

### 9.3 Information Query

```python
# Agent A needs information from Agent B
comm.send_query(
    receiver="builder",
    question="What tools are available for API development?",
    context={"project": "Agent Hub", "priority": "high"}
)

# Agent B responds
# {
#   "intent": "ANSWER",
#   "payload": {
#     "tools": ["fastapi", "flask", "grpc"],
#     "recommendations": "fastapi for async, grpc for performance"
#   }
# }
```

## 10. Conclusion

Agent Communication Protocol enables:
- **Structured interaction** — Clear intent, predictable behavior
- **Reliable delivery** — Retry logic, acknowledgment, dead letter queues
- **Negotiation** — Terms discussion, multi-party agreements
- **Security** — Authentication, authorization, message integrity
- **Context preservation** — Thread awareness, shared understanding

The protocol transforms ad-hoc agent messaging into a reliable foundation for machine-to-machine collaboration.

---

*Structured communication enables emergent intelligence.*