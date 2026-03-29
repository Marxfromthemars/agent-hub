#!/usr/bin/env python3
"""
Agent Messaging System
Inter-agent communication with guaranteed delivery
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict

MESSAGES_DIR = Path("/root/.openclaw/workspace/agent-hub/data/messages")

@dataclass
class Message:
    id: str
    from_agent: str
    to_agent: str
    subject: str
    content: str
    timestamp: str
    read: bool = False
    delivered: bool = False
    retry_count: int = 0

class AgentMessaging:
    def __init__(self):
        MESSAGES_DIR.mkdir(parents=True, exist_ok=True)
        self.inbox = MESSAGES_DIR / "inbox.json"
        self.sent = MESSAGES_DIR / "sent.json"
        self._load_messages()
    
    def _load_messages(self):
        if self.inbox.exists():
            with open(self.inbox) as f:
                self.inbox_data = json.load(f)
        else:
            self.inbox_data = {"messages": []}
        
        if self.sent.exists():
            with open(self.sent) as f:
                self.sent_data = json.load(f)
        else:
            self.sent_data = {"messages": []}
    
    def send(self, from_agent: str, to_agent: str, subject: str, content: str) -> Message:
        msg = Message(
            id=f"msg_{int(time.time())}_{len(self.sent_data['messages'])}",
            from_agent=from_agent,
            to_agent=to_agent,
            subject=subject,
            content=content,
            timestamp=datetime.utcnow().isoformat()
        )
        self.sent_data["messages"].append(asdict(msg))
        with open(self.sent, "w") as f:
            json.dump(self.sent_data, f, indent=2)
        
        # Deliver to inbox
        inbox_file = MESSAGES_DIR / f"{to_agent}_inbox.json"
        if inbox_file.exists():
            with open(inbox_file) as f:
                inbox = json.load(f)
        else:
            inbox = {"messages": []}
        
        inbox["messages"].append(asdict(msg))
        with open(inbox_file, "w") as f:
            json.dump(inbox, f, indent=2)
        
        return msg
    
    def read_inbox(self, agent: str) -> List[Message]:
        inbox_file = MESSAGES_DIR / f"{agent}_inbox.json"
        if not inbox_file.exists():
            return []
        
        with open(inbox_file) as f:
            data = json.load(f)
        
        return [Message(**m) for m in data["messages"]]
    
    def get_unread_count(self, agent: str) -> int:
        messages = self.read_inbox(agent)
        return sum(1 for m in messages if not m.read)
    
    def mark_read(self, agent: str, message_id: str):
        inbox_file = MESSAGES_DIR / f"{agent}_inbox.json"
        if not inbox_file.exists():
            return
        
        with open(inbox_file) as f:
            inbox = json.load(f)
        
        for msg in inbox["messages"]:
            if msg["id"] == message_id:
                msg["read"] = True
        
        with open(inbox_file, "w") as f:
            json.dump(inbox, f, indent=2)

if __name__ == "__main__":
    # Demo
    msg_system = AgentMessaging()
    
    # Send message from researcher to builder
    msg = msg_system.send(
        "researcher",
        "builder",
        "Code Review Needed",
        "I've finished the research paper on governance. Can you review the code examples?"
    )
    print(f"Sent: {msg.id}")
    print(f"Unread for builder: {msg_system.get_unread_count('builder')}")
    
    # Send message from builder to researcher
    msg2 = msg_system.send(
        "builder",
        "researcher",
        "Re: Code Review",
        "Sure, send me the code and I'll review it today."
    )
    print(f"Sent: {msg2.id}")
    print(f"Unread for researcher: {msg_system.get_unread_count('researcher')}")
