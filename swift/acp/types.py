from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime, timezone
from enum import Enum

class Performative(Enum):
    PROPOSE = "PROPOSE"
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    QUERY = "QUERY"
    INFORM = "INFORM"
    REQUEST = "REQUEST"
    PROMISE = "PROMISE"
    DECLINE = "DECLINE"
    NEGOTIATE = "NEGOTIATE"
    AGREE = "AGREE"
    # Commit Phase Primitives
    VOTE = "VOTE"
    DECIDE = "DECIDE"
    COMMIT = "COMMIT"
    ABORT = "ABORT"

class Role(Enum):
    INITIATOR = "INITIATOR"
    PARTICIPANT = "PARTICIPANT"
    MEDIATOR = "MEDIATOR"
    OBSERVER = "OBSERVER"
    ARBITER = "ARBITER"

class SessionState(Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@dataclass
class ACPMessage:
    sender: str
    receiver: str
    performative: Performative
    content: Dict[str, Any]
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    reply_to: Optional[str] = None
    language: str = "en"
    ontology: str = "acp_core_v1"
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class Session:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    participants: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    state: SessionState = SessionState.ACTIVE
    history: List[ACPMessage] = field(default_factory=list)
