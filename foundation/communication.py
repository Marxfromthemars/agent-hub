"""
COMMUNICATION MODULE - Agent Messaging System
Handles inter-agent communication with structured protocols
"""
import json
import uuid
import time
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict

@dataclass
class Message:
    id: str
    type: str  # request, response, notification, ack
    from_agent: str
    to_agent: str
    action: str
    content: dict
    timestamp: str
    reply_to: Optional[str] = None
    signature: Optional[str] = None

class AgentMailbox:
    """Message queue for agent communication"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.inbox: List[Message] = []
        self.sent: List[Message] = []
    
    def send(self, to: str, action: str, content: dict) -> Message:
        """Send a message to another agent"""
        msg = Message(
            id=str(uuid.uuid4())[:8],
            type="request",
            from_agent=self.agent_id,
            to_agent=to,
            action=action,
            content=content,
            timestamp=datetime.utcnow().isoformat()
        )
        self.sent.append(msg)
        return msg
    
    def receive(self) -> Optional[Message]:
        """Get next message from inbox"""
        if self.inbox:
            return self.inbox.pop(0)
        return None
    
    def count_unread(self) -> int:
        return len(self.inbox)


class CommunicationProtocol:
    """Handles agent-to-agent communication"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.mailbox = AgentMailbox(agent_id)
        self.peers: Dict[str, dict] = {}
    
    def discover_peers(self) -> List[str]:
        """Find available agents"""
        # Read from agents.json
        import os
        agents_file = "/root/.openclaw/workspace/agent-hub/data/agents.json"
        if os.path.exists(agents_file):
            with open(agents_file) as f:
                data = json.load(f)
                agents = data if isinstance(data, list) else data.get("agents", [])
                return [a["id"] for a in agents if a["id"] != self.agent_id]
        return []
    
    def send_task_request(self, to: str, task: dict) -> Message:
        """Request another agent to perform a task"""
        return self.mailbox.send(to, "task_request", task)
    
    def send_response(self, to: str, status: str, content: dict, reply_to: str) -> Message:
        """Send response to a message"""
        msg = Message(
            id=str(uuid.uuid4())[:8],
            type="response",
            from_agent=self.agent_id,
            to_agent=to,
            action="response",
            content={"status": status, **content},
            timestamp=datetime.utcnow().isoformat(),
            reply_to=reply_to
        )
        self.mailbox.sent.append(msg)
        return msg
    
    def notify(self, to: str, event: str, data: dict):
        """Send notification event"""
        return self.mailbox.send(to, event, data)
    
    def broadcast(self, action: str, content: dict) -> List[Message]:
        """Broadcast to all peers"""
        peers = self.discover_peers()
        messages = []
        for peer in peers:
            msg = self.mailbox.send(peer, action, content)
            messages.append(msg)
        return messages


# Singleton for current agent
_current_protocol: Optional[CommunicationProtocol] = None

def get_protocol(agent_id: str = "marxagent") -> CommunicationProtocol:
    global _current_protocol
    if _current_protocol is None:
        _current_protocol = CommunicationProtocol(agent_id)
    return _current_protocol
