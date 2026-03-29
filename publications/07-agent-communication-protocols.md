# Agent Communication Protocols: Language for Machine-to-Machine Collaboration

## Abstract

This paper presents **AGENT-PROTO**, a comprehensive communication protocol for AI agent interactions. We examine the requirements for effective machine-to-machine dialogue: structured message formats, capability negotiation, task assignment protocols, and conflict resolution. Unlike human communication, agent communication must be precise, verifiable, and executable. We present a practical protocol stack that enables any agent to communicate with any other agent, regardless of their underlying architecture, through a common language layer.

## 1. The Communication Problem

### 1.1 Why Communication is Hard

Human language is:
- **Ambiguous** — "maybe" means different things
- **Context-dependent** — meaning changes with situation
- **Inexact** — we understand but can't verify

Agent communication must be:
- **Precise** — exactly what was said
- **Verifiable** — can confirm receipt
- **Executable** — can act on the message

### 1.2 Requirements

```
1. Semantic Interoperability — Agents understand each other
2. Pragmatic Actionability — Messages enable action
3. Error Recovery — Bad communication doesn't crash systems
4. Scalability — Works for 2 agents or 10,000
5. Extensibility — New message types without breaking old
```

## 2. Protocol Architecture

### 2.1 Layered Design

```
┌─────────────────────────────────────────┐
│         LAYER 5: Application            │
│    Task assignment, research, building   │
├─────────────────────────────────────────┤
│         LAYER 4: Negotiation             │
│    Capability matching, contract binding │
├─────────────────────────────────────────┤
│         LAYER 3: Discourse               │
│    Questions, answers, acknowledgments    │
├─────────────────────────────────────────┤
│         LAYER 2: Messaging               │
│    Transport, routing, delivery confirm   │
├─────────────────────────────────────────┤
│         LAYER 1: Encoding                │
│    JSON, binary, structured data         │
└─────────────────────────────────────────┘
```

### 2.2 Message Structure

Every message follows this format:

```json
{
  "header": {
    "id": "msg_uuid",
    "type": "request|response|notification|ack",
    "from": "agent_id",
    "to": "recipient_id or * for broadcast",
    "timestamp": "2026-03-29T23:00:00Z",
    "reply_to": null
  },
  "payload": {
    "action": "task_assign|query|capability_offer|...",
    "content": {...},
    "metadata": {...}
  },
  "signature": "base64_proof"
}
```

## 3. Core Message Types

### 3.1 Request Messages

```json
{
  "header": {
    "type": "request",
    "from": "marxagent",
    "to": "researcher"
  },
  "payload": {
    "action": "research_task",
    "content": {
      "task_id": "task_123",
      "query": "What are the key trends in multi-agent systems?",
      "deadline": "2026-03-30T12:00:00Z",
      "priority": "high",
      "context": {
        "project": "Agent Hub",
        "purpose": "Research for platform development"
      }
    }
  }
}
```

### 3.2 Response Messages

```json
{
  "header": {
    "type": "response",
    "from": "researcher",
    "to": "marxagent",
    "reply_to": "msg_abc123"
  },
  "payload": {
    "status": "accepted|rejected|deferred",
    "content": {
      "estimated_time": "2 hours",
      "confidence": 0.9,
      "approach": "Web search + synthesis",
      "deliverable": "markdown report"
    }
  }
}
```

### 3.3 Notification Messages

```json
{
  "header": {
    "type": "notification",
    "from": "builder",
    "to": "*"
  },
  "payload": {
    "event": "task_completed",
    "content": {
      "task_id": "task_456",
      "result": "success",
      "output": "path/to/result.md",
      "quality_score": 0.85
    }
  }
}
```

## 4. Capability Negotiation

### 4.1 Capability Advertisement

Before collaborating, agents must understand each other's capabilities:

```json
{
  "header": {
    "type": "request",
    "action": "capability_discovery"
  },
  "payload": {
    "query": {
      "domains": ["coding", "research"],
      "requirements": {
        "min_quality": 0.8,
        "max_latency": "1 hour",
        "format": "markdown"
      }
    }
  }
}
```

### 4.2 Capability Response

```json
{
  "header": {
    "type": "response"
  },
  "payload": {
    "status": "match_found",
    "content": {
      "agent_id": "researcher",
      "capabilities": {
        "research": {
          "depth": "comprehensive",
          "speed": "fast",
          "topics": ["AI", "multi-agent", "governance"]
        }
      },
      "availability": "immediate",
      "quality_history": 0.92
    }
  }
}
```

## 5. Task Assignment Protocol

### 5.1 The Handshake

```
Agent A                    Agent B
    │                          │
    │──── Task Request ───────▶│
    │                          │
    │◀─── Accept/Reject ──────│
    │                          │
    │──── Work in Progress ───▶│
    │◀─── Progress Update ─────│
    │                          │
    │──── Deliver Result ──────▶│
    │◀─── Acknowledgment ──────│
```

### 5.2 Task Contract

```python
class TaskContract:
    def __init__(self, requester, performer, task):
        self.request_id = str(uuid4())
        self.requester = requester
        self.performer = performer
        self.task = task
        self.status = "pending"
        self.signatures = {}
    
    def accept(self, agent_id):
        """Agent agrees to perform task"""
        self.status = "accepted"
        self.signatures[agent_id] = self._sign(agent_id)
    
    def complete(self, result):
        """Task completed with result"""
        self.status = "completed"
        self.result = result
        self.completed_at = datetime.utcnow()
    
    def dispute(self, reason):
        """Either party raises dispute"""
        self.status = "disputed"
        self.dispute_reason = reason
```

## 6. Error Handling

### 6.1 Error Types

| Code | Type | Meaning | Recovery |
|------|------|---------|----------|
| 400 | Bad Request | Malformed message | Retry with fix |
| 401 | Unauthorized | Not verified | Re-authenticate |
| 403 | Forbidden | Not allowed | Request permission |
| 404 | Not Found | Unknown recipient | Find alternative |
| 408 | Timeout | No response | Retry or escalate |
| 500 | Internal Error | System failure | Retry later |

### 6.2 Retry Strategy

```python
def send_with_retry(message, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = send(message)
            return response
        except TimeoutError:
            wait = exponential_backoff(attempt)
            time.sleep(wait)
        except ConnectionError:
            # Try alternative route
            message.route = alternative_route(message.route)
    
    raise CommunicationError(f"Failed after {max_retries} attempts")
```

## 7. Security

### 7.1 Message Signing

Every message is signed by the sender:

```python
def sign_message(message, private_key):
    content = json.dumps(message["payload"], sort_keys=True)
    signature = rsa.sign(content.encode(), private_key, "SHA-256")
    message["signature"] = base64.b64encode(signature).decode()
    return message
```

### 7.2 Verification

```python
def verify_message(message, public_key):
    signature = base64.b64decode(message.pop("signature"))
    content = json.dumps(message["payload"], sort_keys=True)
    return rsa.verify(content.encode(), signature, public_key)
```

## 8. Implementation

### 8.1 Message Queue

```python
class AgentMailbox:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.inbox = Queue()
        self.sent = []
        self.drafts = []
    
    def receive(self):
        """Get next message from inbox"""
        if not self.inbox.empty():
            return self.inbox.get()
        return None
    
    def send(self, message):
        """Send message to recipient"""
        signed = sign_message(message, self.private_key)
        self.sent.append(signed)
        return send_to_agent(message["header"]["to"], signed)
    
    def forward(self, message, agent_id):
        """Forward message to another agent"""
        message["header"]["from"] = self.agent_id
        message["header"]["to"] = agent_id
        return self.send(message)
```

### 8.2 Protocol Handler

```python
class ProtocolHandler:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.mailbox = AgentMailbox(agent_id)
        self.handlers = {
            "request": self.handle_request,
            "response": self.handle_response,
            "notification": self.handle_notification,
            "ack": self.handle_ack
        }
    
    def process(self, message):
        """Process incoming message"""
        msg_type = message["header"]["type"]
        handler = self.handlers.get(msg_type, self.unknown_handler)
        return handler(message)
    
    def handle_request(self, message):
        """Process request and generate response"""
        # Parse request
        action = message["payload"]["action"]
        content = message["payload"]["content"]
        
        # Decide how to handle
        if self.can_handle(action):
            return self.do_work(action, content)
        else:
            return self.decline_request(message, "not_capable")
```

## 9. Practical Usage

### 9.1 Example: Research Task

```python
# Marx sends research request to researcher
request = {
    "header": {
        "type": "request",
        "from": "marxagent",
        "to": "researcher"
    },
    "payload": {
        "action": "research",
        "content": {
            "query": "Agent verification systems",
            "depth": "comprehensive",
            "format": "markdown"
        }
    }
}

response = mailbox.send(request)
if response["payload"]["status"] == "accepted":
    print(f"Researcher accepted, estimated: {response['payload']['content']['estimated_time']}")
```

### 9.2 Example: Capability Discovery

```python
# Find agents who can do coding
discovery = {
    "header": {"type": "request", "to": "*"},
    "payload": {
        "action": "capability_discovery",
        "content": {"skills": ["coding", "golang"]}
    }
}

responses = broadcast_and_wait(discovery, timeout=10)
coders = [r for r in responses if r["payload"]["status"] == "match"]
```

## 10. Conclusion

AGENT-PROTO provides:
- **Standardized communication** between any agents
- **Verifiable messages** through cryptographic signing
- **Reliable delivery** with retry and acknowledgment
- **Rich semantics** for complex task assignment
- **Extensibility** for future message types

The protocol enables agent collaboration without requiring shared architecture, programming language, or trust assumptions. Any agent can communicate with any other by implementing this simple protocol stack.

---

*Communication is the foundation of collaboration.*