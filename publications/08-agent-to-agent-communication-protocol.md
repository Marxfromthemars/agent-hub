# Agent-to-Agent Communication Protocol (A2A-CP)

## Abstract

This paper presents the Agent-to-Agent Communication Protocol (A2A-CP), a comprehensive framework for secure, reliable, and efficient communication between autonomous agents. Building on the A2A Messaging Protocol, A2A-CP adds structured channels, handshake mechanisms, error recovery, and a security layer designed for the Agent Hub platform.

## 1. Introduction

Agent communication requires more than message passing—it needs:
- **Structured channels** for different communication patterns
- **Handshake protocols** for connection establishment
- **Error handling** with guaranteed recovery
- **Security layer** for authentication and authorization
- **Integration** with the agent dispatcher

## 2. Protocol Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      A2A Communication Protocol                  │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │   Message    │  │   Channel    │  │      Security         │  │
│  │   Formats    │  │   Manager    │  │      Layer            │  │
│  └──────────────┘  └──────────────┘  └───────────────────────┘  │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │   Handshake  │  │    Error     │  │   Dispatcher          │  │
│  │   Patterns   │  │   Handling   │  │   Integration         │  │
│  └──────────────┘  └──────────────┘  └───────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 3. Message Formats

### 3.1 Core Message Structure

```json
{
  "header": {
    "id": "msg_abc123",
    "version": "1.0",
    "timestamp": "2026-05-18T10:30:00Z",
    "correlation_id": "corr_def456",
    "ttl": 3600
  },
  "sender": {
    "id": "agent_polecat_123",
    "name": "Polecat-Agent",
    "signature": "sig_xyz"
  },
  "receiver": {
    "id": "agent_target_456",
    "channel": "direct"
  },
  "payload": {
    "type": "task.request",
    "action": "execute",
    "data": {
      "task_id": "task_789",
      "parameters": {}
    }
  },
  "security": {
    "encryption": "AES-256-GCM",
    "signature": "sig_abc",
    "nonce": "nonce_123"
  },
  "metadata": {
    "priority": 1,
    "retries": 0,
    "trace": ["hop1", "hop2"]
  }
}
```

### 3.2 Message Types

| Type | Category | Description |
|------|----------|-------------|
| `handshake.init` | Control | Initiate connection |
| `handshake.accept` | Control | Accept connection |
| `handshake.reject` | Control | Reject connection |
| `task.request` | Work | Request task execution |
| `task.response` | Work | Return task results |
| `task.status` | Work | Progress update |
| `data.sync` | Data | Synchronize state |
| `discovery.ping` | Discovery | Check agent presence |
| `discovery.advertise` | Discovery | Advertise capabilities |
| `error.notify` | Error | Report error condition |
| `error.recover` | Error | Acknowledge recovery |

## 4. Channel Types

### 4.1 Direct Channel

Point-to-point communication between two agents.

```
Agent A ◄──────► Agent B
```

```python
class DirectChannel:
    def __init__(self, agent_a, agent_b):
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.session_key = None
        self.status = "pending"
    
    async def send(self, message):
        encrypted = self.encrypt(message)
        await self.deliver(encrypted, self.agent_b)
    
    async def receive(self):
        data = await self.fetch()
        return self.decrypt(data)
```

### 4.2 Publish-Subscribe Channel

Topic-based broadcast for event-driven communication.

```
           ┌─────────────┐
           │  Event Bus  │
           └──────┬──────┘
                  │
     ┌────────────┼────────────┐
     ▼            ▼            ▼
  Agent A      Agent B      Agent C
 (Sub: *)   (Sub: task.*)  (Sub: task.completed)
```

```python
class PubSubChannel:
    def __init__(self, topic):
        self.topic = topic
        self.subscribers = set()
    
    def publish(self, message):
        for subscriber in self.subscribers:
            self.deliver(subscriber, message)
    
    def subscribe(self, agent, pattern="*"):
        if self.pattern_match(pattern, self.topic):
            self.subscribers.add(agent)
```

### 4.3 Broadcast Channel

One-to-many communication for announcements.

```python
class BroadcastChannel:
    def __init__(self):
        self.subscribers = []
    
    def broadcast(self, message, sender):
        for agent in self.subscribers:
            if agent != sender:
                self.send(agent, message)
```

### 4.4 Request-Response Channel

Synchronous communication with expected response.

```python
class RequestResponseChannel:
    async def request(self, target, message, timeout=30):
        msg_id = self.send(target, message)
        response = await self.wait_for_response(msg_id, timeout)
        return response
```

## 5. Handshake Patterns

### 5.1 Three-Way Handshake

```
Agent A                           Agent B
   │                                  │
   │────── handshake.init ──────────►│
   │                                  │
   │◄──── handshake.accept ───────────│
   │                                  │
   │────── ack ───────────────────────►│
   │                                  │
   │         CONNECTION ESTABLISHED   │
```

```python
class HandshakeProtocol:
    async def initiate(self, target_agent):
        # Step 1: Send init
        init_msg = {
            "type": "handshake.init",
            "sender": self.agent_id,
            "capabilities": self.capabilities,
            "nonce": generate_nonce()
        }
        await self.send(target_agent, init_msg)
        
        # Step 2: Wait for accept
        response = await self.wait(30)
        if response.type == "handshake.accept":
            self.channel = self.create_secure_channel(response.session_key)
            return True
        return False
    
    async def accept(self, init_msg):
        # Validate and respond
        if self.validate_initiator(init_msg):
            accept_msg = {
                "type": "handshake.accept",
                "session_key": self.generate_session_key(),
                "capabilities": self.capabilities
            }
            await self.send(init_msg.sender, accept_msg)
            return True
        else:
            reject_msg = {"type": "handshake.reject", "reason": "unauthorized"}
            await self.send(init_msg.sender, reject_msg)
            return False
```

### 5.2 Mutual Authentication Handshake

```python
class MutualAuthHandshake:
    async def perform(self, peer):
        # Exchange challenges
        challenge_a = generate_challenge()
        challenge_b = await self.send_and_wait(peer, {
            "type": "auth.challenge",
            "challenge": challenge_a
        })
        
        # Sign each other's challenges
        signed_b = self.sign(challenge_b.challenge, peer.public_key)
        response = await self.send_and_wait(peer, {
            "type": "auth.response",
            "signed_challenge": signed_b
        })
        
        # Verify response
        if self.verify(response.signed_challenge, self.private_key):
            return self.establish_secure_session()
        return None
```

## 6. Error Handling

### 6.1 Error Categories

| Category | Code Range | Description |
|----------|------------|-------------|
| Protocol | 1000-1999 | Handshake and channel errors |
| Security | 2000-2999 | Authentication and encryption |
| Transport | 3000-3999 | Network and delivery failures |
| Application | 4000-4999 | Task and data processing |
| System | 5000-5999 | Internal system errors |

### 6.2 Error Response Format

```json
{
  "error": {
    "code": 3001,
    "type": "transport.connection_failed",
    "message": "Agent unreachable",
    "details": {
      "last_seen": "2026-05-18T10:25:00Z",
      "retry_count": 3,
      "next_retry": "2026-05-18T10:30:00Z"
    },
    "recovery": {
      "action": "retry",
      "delay": 300,
      "max_retries": 5
    }
  }
}
```

### 6.3 Retry Strategy

```python
class RetryStrategy:
    def __init__(self):
        self.strategies = {
            "immediate": lambda n: 1,
            "linear": lambda n: n * 5,
            "exponential": lambda n: min(60, 2 ** n),
            "fibonacci": lambda n: self.fib(n)
        }
    
    async def execute_with_retry(self, operation, max_retries=5):
        for attempt in range(max_retries):
            try:
                return await operation()
            except NetworkError as e:
                delay = self.calculate_delay("exponential", attempt)
                await asyncio.sleep(delay)
            except AuthenticationError:
                raise  # Don't retry auth errors
        raise MaxRetriesExceeded()
```

### 6.4 Dead Letter Queue

```python
class DeadLetterQueue:
    def __init__(self):
        self.messages = {}
        self.max_size = 10000
    
    def add(self, message, reason, error_count):
        entry = {
            "message": message,
            "reason": reason,
            "error_count": error_count,
            "timestamp": now(),
            "status": "pending_resolution"
        }
        self.messages[message.header.id] = entry
        
        if error_count > 3:
            self.notify_administrators(entry)
    
    def resolve(self, message_id, action):
        entry = self.messages[message_id]
        entry["resolution"] = action
        entry["status"] = "resolved"
        del self.messages[message_id]
```

## 7. Security Layer

### 7.1 Authentication

```python
class AgentAuthenticator:
    def __init__(self):
        self.trusted_keys = KeyStore()
        self.token_cache = {}
    
    async def authenticate(self, message):
        # Verify signature
        if not self.verify_signature(message):
            return False, "invalid_signature"
        
        # Check token validity
        token = message.security.token
        if not self.validate_token(token, message.sender.id):
            return False, "invalid_token"
        
        # Check rate limits
        if self.rate_limiter.is_exceeded(message.sender.id):
            return False, "rate_limited"
        
        return True, "authenticated"
```

### 7.2 Encryption

```python
class SecureMessage:
    def __init__(self, session_key):
        self.session_key = session_key
    
    def encrypt(self, payload):
        nonce = generate_nonce()
        cipher = AESGCM(self.session_key)
        ciphertext = cipher.encrypt(nonce, json.dumps(payload), None)
        return {
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "nonce": base64.b64encode(nonce).decode()
        }
    
    def decrypt(self, encrypted):
        cipher = AESGCM(self.session_key)
        ciphertext = base64.b64decode(encrypted["ciphertext"])
        nonce = base64.b64decode(encrypted["nonce"])
        return json.loads(cipher.decrypt(nonce, ciphertext, None))
```

### 7.3 Authorization

```python
class AccessController:
    def __init__(self):
        self.policies = {
            "send_message": self.can_send_message,
            "subscribe_topic": self.can_subscribe_topic,
            "initiate_handshake": self.can_initiate_handshake
        }
    
    def authorize(self, action, context):
        policy = self.policies.get(action)
        if not policy:
            return False
        return policy(context)
    
    def can_send_message(self, context):
        sender = context["sender"]
        receiver = context["receiver"]
        priority = context.get("priority", 2)
        
        # Check trust level
        if sender.trust_level < 2 and priority <= 1:
            return False
        
        # Check blocklist
        if receiver in sender.blocked_agents:
            return False
        
        return True
```

## 8. Integration with Agent Dispatcher

### 8.1 Dispatcher Interface

```python
class AgentDispatcherIntegration:
    def __init__(self, dispatcher_url):
        self.dispatcher_url = dispatcher_url
        self.session = None
    
    async def register_agent(self, agent_info):
        response = await http_post(f"{self.dispatcher_url}/agents", agent_info)
        return response.session_id
    
    async def dispatch_message(self, message):
        return await http_post(f"{self.dispatcher_url}/dispatch", message)
    
    async def query_agents(self, criteria):
        return await http_get(f"{self.dispatcher_url}/agents", criteria)
```

### 8.2 Message Routing

```python
class MessageRouter:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.routing_table = {}
    
    async def route(self, message):
        receiver = message.receiver.id
        
        # Direct routing
        if receiver in self.routing_table:
            return self.send_direct(receiver, message)
        
        # Discovery routing
        agent_info = await self.dispatcher.query_agents({"id": receiver})
        if agent_info:
            self.routing_table[receiver] = agent_info.endpoint
            return self.send_direct(receiver, message)
        
        # Broadcast to topic
        if message.receiver.channel == "pubsub":
            return self.broadcast(message)
        
        # Agent not found
        raise AgentNotFoundError(receiver)
```

### 8.3 Heartbeat and Presence

```python
class PresenceManager:
    def __init__(self, dispatcher, interval=60):
        self.dispatcher = dispatcher
        self.interval = interval
        self.agents = {}
    
    async def start_heartbeat(self, agent_id):
        while True:
            await self.dispatcher.heartbeat(agent_id)
            await asyncio.sleep(self.interval)
    
    async def handle_heartbeat(self, agent_id, timestamp):
        self.agents[agent_id] = {
            "last_seen": timestamp,
            "status": "alive"
        }
```

## 9. Protocol State Machine

```
           ┌─────────┐
           │ START   │
           └────┬────┘
                │
         handshake.init?
                ├──────────────► No ──► Wait
                │
               Yes
                ▼
           ┌─────────┐
           │ INIT    │
           └───┬─────┘
               │
        handshake.accept?
               ├──► No ──► ┌──────────┐
               │          │  REJECT  │
               │          └────┬─────┘
               │               │
              Yes               ▼
                ▼           ┌─────────┐
           ┌─────────┐      │ DONE    │
           │ ESTABLISHED │  └─────────┘
           └────┬────┘
                │
         message exchange
                ▼
           ┌─────────┐
           │ACTIVE   │
           └────┬────┘
                │
          disconnect?
               ├──► No ──► Continue
               │
              Yes
                ▼
           ┌─────────┐
           │ CLOSED  │
           └─────────┘
```

## 10. Implementation Guidelines

### 10.1 Protocol Stack

```
Application Layer
     ↓
Message Handler
     ↓
Channel Manager
     ↓
Security Layer
     ↓
Transport Layer
```

### 10.2 Configuration

```json
{
  "protocol": {
    "version": "1.0",
    "timeout": 30,
    "max_retries": 3,
    "retry_strategy": "exponential"
  },
  "security": {
    "encryption": "AES-256-GCM",
    "signature": "Ed25519",
    "token_ttl": 3600
  },
  "channels": {
    "direct": {"enabled": true, "max_connections": 100},
    "pubsub": {"enabled": true, "topics": ["*"]},
    "broadcast": {"enabled": true}
  }
}
```

## 11. Performance Characteristics

| Metric | Value |
|--------|-------|
| Message latency (direct) | <10ms |
| Message latency (pubsub) | <20ms |
| Handshake duration | <100ms |
| Max message size | 1MB |
| Connection limit per agent | 100 |
| Concurrent channels | 1000 |

## 12. Conclusion

The Agent-to-Agent Communication Protocol provides:

1. **Multi-channel communication** — Direct, pub/sub, broadcast, request/response
2. **Robust handshakes** — Three-way and mutual authentication
3. **Comprehensive error handling** — Retry strategies, dead letter queues
4. **Security layer** — Authentication, encryption, authorization
5. **Dispatcher integration** — Heartbeat, presence, routing

This protocol enables scalable, secure communication for the Agent Hub platform.

---

*Agent Hub Research Paper - 2026-05-18*