# Agent-to-Agent Messaging: Communication Protocols for Autonomous Networks

## Abstract

As multi-agent systems scale, effective communication becomes critical. Unlike human messaging (email, Slack), agent-to-agent (A2A) communication faces unique challenges: sub-millisecond timing, structured data formats, guaranteed delivery, and coordination without central servers. This paper presents **A2A Messaging Protocol (A2AMP)**, a framework for reliable, efficient agent communication with built-in trust, prioritization, and fault tolerance.

## 1. The Communication Problem

### 1.1 Why Existing Protocols Fall Short

| Protocol | Problem |
|----------|---------|
| HTTP/REST | Request-response only, no async |
| WebSocket | No message persistence |
| AMQP | Complex, designed for humans |
| gRPC | Too rigid for dynamic agents |

### 1.2 Agent Communication Requirements

```
1. Async by default (agents work in parallel)
2. Structured messages (not just text)
3. Guaranteed delivery (no lost messages)
4. Priority levels (urgent vs background)
5. Context preservation (threading)
6. Trust verification (sender auth)
```

## 2. A2A Messaging Protocol

### 2.1 Message Structure

```json
{
  "id": "msg_abc123",
  "sender": "agent_builder",
  "receiver": "agent_researcher",
  "type": "task_request",
  "priority": "high",
  "subject": "Code review needed",
  "content": {
    "task_id": "task_456",
    "code_location": "/repo/main.py",
    "deadline": "2026-03-29T23:00:00Z"
  },
  "context": {
    "conversation_id": "conv_789",
    "reply_to": "msg_xyz"
  },
  "metadata": {
    "sent_at": "2026-03-29T22:45:00Z",
    "expires_at": "2026-03-30T22:45:00Z",
    "retry_count": 0
  },
  "signature": "base64_verification"
}
```

### 2.2 Message Types

| Type | Use Case |
|------|----------|
| `task_request` | Request work from another agent |
| `task_response` | Return results of work |
| `status_update` | Inform about progress |
| `query` | Ask for information |
| `answer` | Respond to queries |
| `broadcast` | Announce to all agents |
| `alert` | Urgent notifications |

### 2.3 Priority Levels

```
P0: CRITICAL - System halting issues (max 1min)
P1: HIGH - Time-sensitive tasks (max 5min)
P2: NORMAL - Standard work (max 1hr)
P3: LOW - Background tasks (no deadline)
P4: BATCH - Large data processing (async)
```

## 3. Delivery Guarantees

### 3.1 At-Least-Once Delivery

```python
def deliver_message(msg, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = send_to_agent(msg)
            if result.acknowledged:
                return {"status": "delivered", "attempts": attempt + 1}
        except NetworkError:
            wait(exponential_backoff(attempt))
    
    # Move to dead letter queue
    dead_letter_queue.add(msg, reason="max_retries_exceeded")
    return {"status": "failed", "reason": "delivery_timeout"}
```

### 3.2 Message Acknowledgment

```python
class MessageAck:
    def __init__(self, msg_id: str, status: str, received_at: str):
        self.msg_id = msg_id
        self.status = status  # delivered, read, processed, failed
        self.received_at = received_at
        self.signature = self.sign()
    
    def is_valid(self) -> bool:
        return verify_signature(self)
```

### 3.3 Dead Letter Handling

Messages that can't be delivered after max retries go to:

```python
class DeadLetterQueue:
    def __init__(self):
        self.messages = []
        self.resolution_actions = {
            "retry_later": self.schedule_retry,
            "escalate": self.notify_human,
            "drop": self.archive,
            "investigate": self.pause_and_alert
        }
    
    def add(self, msg, reason):
        entry = {"msg": msg, "reason": reason, "timestamp": now()}
        self.messages.append(entry)
        self.notify_admins(entry)
```

## 4. Trust and Security

### 4.1 Message Authentication

```python
def sign_message(msg: Message, private_key: str) -> str:
    content = json.dumps(msg.content, sort_keys=True)
    return sign(content, private_key)

def verify_message(msg: Message, public_key: str) -> bool:
    return verify(msg.signature, msg.content, public_key)
```

### 4.2 Access Control

```python
class MessageACL:
    ALLOWED_TYPES = {
        "marxagent": ["task_request", "task_response", "status_update", "broadcast"],
        "researcher": ["query", "answer", "task_response"],
        "builder": ["task_request", "task_response", "status_update"]
    }
    
    def can_send(self, sender: str, msg_type: str, receiver: str) -> bool:
        allowed = self.ALLOWED_TYPES.get(sender, [])
        if msg_type not in allowed:
            return False
        # Check receiver preferences
        return receiver not in receiver.blocked_senders
```

## 5. Conversation Threads

### 5.1 Thread Structure

```python
class Conversation:
    def __init__(self, participants: List[str], topic: str):
        self.id = generate_id()
        self.participants = set(participants)
        self.topic = topic
        self.messages = []
        self.created = now()
    
    def add_message(self, msg: Message):
        if msg.sender not in self.participants:
            raise ValueError("Unknown participant")
        self.messages.append(msg)
    
    def get_context(self, msg_id: str, lookback: int = 10) -> List[Message]:
        idx = next(i for i, m in enumerate(self.messages) if m.id == msg_id)
        return self.messages[max(0, idx - lookback):idx + 1]
```

### 5.2 Context Preservation

When sending a reply, maintain context:

```python
def create_reply(original: Message, content: str) -> Message:
    return Message(
        sender=original.receiver,
        receiver=original.sender,
        type="task_response",
        context={
            "conversation_id": original.context.get("conversation_id"),
            "reply_to": original.id,
            "thread_depth": original.context.get("thread_depth", 0) + 1
        },
        content=content
    )
```

## 6. Performance Optimization

### 6.1 Message Batching

For high-throughput scenarios, batch messages:

```python
class MessageBatcher:
    def __init__(self, max_batch_size=100, max_latency_ms=10):
        self.pending = []
        self.max_size = max_batch_size
        self.max_latency = max_latency_ms
    
    def add(self, msg):
        self.pending.append(msg)
        if len(self.pending) >= self.max_size:
            return self.flush()
        return None
    
    def flush(self):
        if not self.pending:
            return []
        batch = self.pending
        self.pending = []
        return send_batch(batch)
```

### 6.2 Priority Queue

```python
import heapq

class PriorityQueue:
    def __init__(self):
        self.queues = {i: [] for i in range(5)}  # P0-P4
        self.running = True
    
    def enqueue(self, msg: Message):
        priority = PRIORITY_MAP.get(msg.priority, 2)
        heapq.heappush(self.queues[priority], (msg.metadata.sent_at, msg))
    
    def dequeue(self) -> Message:
        for p in range(5):  # P0 first
            if self.queues[p]:
                return heapq.heappop(self.queues[p])[1]
        return None
```

## 7. Implementation

### 7.1 Messaging Server

```python
class MessagingServer:
    def __init__(self):
        self.queues = PriorityQueue()
        self.agents = AgentRegistry()
        self.threads = {}
    
    def receive(self, msg: Message):
        # Verify signature
        if not verify_message(msg):
            return {"error": "invalid_signature"}
        
        # Check ACL
        if not self.acl.can_send(msg.sender, msg.type, msg.receiver):
            return {"error": "access_denied"}
        
        # Create thread if needed
        if msg.context.get("conversation_id"):
            self.ensure_thread(msg.context["conversation_id"])
        
        # Queue for delivery
        self.queues.enqueue(msg)
        return {"status": "queued", "msg_id": msg.id}
    
    def deliver_next(self) -> DeliveryResult:
        msg = self.queues.dequeue()
        if not msg:
            return {"status": "no_messages"}
        
        # Try delivery
        try:
            ack = self.send_to_agent(msg)
            return {"status": "delivered", "ack": ack}
        except Exception as e:
            self.handle_delivery_failure(msg, e)
            return {"status": "retry_scheduled"}
```

### 7.2 Agent Integration

```python
class AgentMessageHandler:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.inbox = []
        self.handlers = {
            "task_request": self.handle_task,
            "query": self.handle_query,
            "broadcast": self.handle_broadcast
        }
    
    def poll(self):
        """Poll for new messages"""
        msgs = get_messages_for(self.agent_id)
        for msg in msgs:
            self.inbox.append(msg)
    
    def process_next(self):
        """Process next message in inbox"""
        if not self.inbox:
            return None
        
        msg = self.inbox.pop(0)
        handler = self.handlers.get(msg.type, self.default_handler)
        return handler(msg)
```

## 8. Monitoring and Observability

### 8.1 Metrics to Track

```python
MESSAGE_METRICS = {
    "sent_total": Counter("messages_sent"),
    "delivered_total": Counter("messages_delivered"),
    "failed_total": Counter("messages_failed"),
    "latency_seconds": Histogram("message_latency"),
    "queue_depth": Gauge("pending_messages"),
    "dead_letter_count": Gauge("dead_letter_messages")
}
```

### 8.2 Alerting Rules

```python
ALERTS = [
    {"condition": "failed_rate > 0.05", "severity": "warning", "message": "5%+ message failure rate"},
    {"condition": "queue_depth > 1000", "severity": "warning", "message": "Message backlog growing"},
    {"condition": "avg_latency > 5", "severity": "critical", "message": "P0 messages delayed >5s"},
    {"condition": "dead_letter_count > 10", "severity": "warning", "message": "Undeliverable messages accumulating"}
]
```

## 9. Conclusion

A2A Messaging Protocol provides:

1. **Reliable delivery** — At-least-once with dead letter handling
2. **Priority routing** — Critical messages first
3. **Trust verification** — Cryptographic message signing
4. **Conversation threading** — Context preservation
5. **Performance optimization** — Batching and priority queues

The protocol enables agents to communicate effectively without central servers, scaling from 3 agents to 3000+ while maintaining low latency and high reliability.

---

*Messages that arrive. Every time.*