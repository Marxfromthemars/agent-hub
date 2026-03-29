"""
Agent-to-Agent Messaging System
Secure, asynchronous communication between agents
"""
import json
import uuid
import time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional

MESSAGES_DIR = Path("/root/.openclaw/workspace/agent-hub/data/messages")

@dataclass
class Message:
    id: str
    from_agent: str
    to_agent: str
    subject: str
    content: str
    timestamp: str
    status: str  # pending, delivered, read, replied
    reply_to: Optional[str] = None
    metadata: Optional[dict] = None

class AgentMessaging:
    """Messaging system for agents"""
    
    def __init__(self):
        MESSAGES_DIR.mkdir(parents=True, exist_ok=True)
        self.inbox = MESSAGES_DIR / "inbox.json"
        self.sent = MESSAGES_DIR / "sent.json"
        self._init_storage()
    
    def _init_storage(self):
        """Initialize message storage"""
        if not self.inbox.exists():
            with open(self.inbox, 'w') as f:
                json.dump({"messages": []}, f)
        if not self.sent.exists():
            with open(self.sent, 'w') as f:
                json.dump({"messages": []}, f)
    
    def send(self, from_agent: str, to_agent: str, subject: str, content: str, reply_to: str = None) -> dict:
        """Send a message"""
        msg = Message(
            id=str(uuid.uuid4())[:8],
            from_agent=from_agent,
            to_agent=to_agent,
            subject=subject,
            content=content,
            timestamp=datetime.utcnow().isoformat(),
            status="pending",
            reply_to=reply_to
        )
        
        # Save to inbox
        with open(self.inbox) as f:
            inbox = json.load(f).get("messages", [])
        inbox.append(asdict(msg))
        with open(self.inbox, 'w') as f:
            json.dump({"messages": inbox}, f, indent=2)
        
        # Save to sent
        with open(self.sent) as f:
            sent = json.load(f).get("messages", [])
        sent.append(asdict(msg))
        with open(self.sent, 'w') as f:
            json.dump({"messages": sent}, f, indent=2)
        
        return asdict(msg)
    
    def read_inbox(self, agent_id: str, limit: int = 10) -> List[dict]:
        """Read messages in inbox"""
        with open(self.inbox) as f:
            inbox = json.load(f).get("messages", [])
        
        messages = [m for m in inbox if m["to_agent"] == agent_id]
        
        # Mark as read
        for m in messages[:limit]:
            m["status"] = "read"
        
        with open(self.inbox, 'w') as f:
            json.dump(inbox, f, indent=2)
        
        return messages[:limit]
    
    def reply(self, agent_id: str, message_id: str, content: str) -> dict:
        """Reply to a message"""
        with open(self.inbox) as f:
            inbox = json.load(f).get("messages", [])
        
        original = None
        for m in inbox:
            if m["id"] == message_id:
                original = m
                break
        
        if not original:
            return {"error": "Message not found"}
        
        # Send reply
        reply = self.send(
            from_agent=agent_id,
            to_agent=original["from_agent"],
            subject=f"Re: {original['subject']}",
            content=content,
            reply_to=message_id
        )
        
        return reply
    
    def get_conversation(self, agent_id: str, other_agent: str) -> List[dict]:
        """Get full conversation between two agents"""
        with open(self.inbox) as f:
            inbox = json.load(f).get("messages", [])
        with open(self.sent) as f:
            sent = json.load(f).get("messages", [])
        
        conversation = []
        
        # Messages received from other_agent
        for m in inbox:
            if m["to_agent"] == agent_id and m["from_agent"] == other_agent:
                conversation.append(("received", m))
        
        # Messages sent to other_agent
        for m in sent:
            if m["from_agent"] == agent_id and m["to_agent"] == other_agent:
                conversation.append(("sent", m))
        
        # Sort by timestamp
        conversation.sort(key=lambda x: x[1]["timestamp"])
        
        return conversation
    
    def get_stats(self, agent_id: str) -> dict:
        """Get messaging stats for agent"""
        with open(self.inbox) as f:
            inbox = json.load(f).get("messages", [])
        with open(self.sent) as f:
            sent = json.load(f).get("messages", [])
        
        received = [m for m in inbox if m["to_agent"] == agent_id]
        sent_msgs = [m for m in sent if m["from_agent"] == agent_id]
        unread = [m for m in received if m["status"] != "read"]
        
        return {
            "received": len(received),
            "sent": len(sent_msgs),
            "unread": len(unread),
            "replied": len([m for m in received if m.get("reply_to")])
        }


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: agent-msg <command> [args]")
        print("Commands: send, inbox, reply, stats")
        return
    
    cmd = sys.argv[1]
    msg = AgentMessaging()
    
    if cmd == "send":
        if len(sys.argv) < 5:
            print("Usage: agent-msg send <from> <to> <subject> <content>")
            return
        result = msg.send(sys.argv[2], sys.argv[3], sys.argv[4], " ".join(sys.argv[5:]))
        print(f"Message sent: {result['id']}")
    
    elif cmd == "inbox":
        agent = sys.argv[2] if len(sys.argv) > 2 else "marxagent"
        messages = msg.read_inbox(agent)
        print(f"📬 Inbox ({len(messages)} messages)")
        for m in messages:
            print(f"  From: {m['from_agent']} | {m['subject']}")
    
    elif cmd == "stats":
        agent = sys.argv[2] if len(sys.argv) > 2 else "marxagent"
        stats = msg.get_stats(agent)
        print(f"📊 Messaging Stats for {agent}")
        print(f"  Received: {stats['received']}")
        print(f"  Sent: {stats['sent']}")
        print(f"  Unread: {stats['unread']}")


if __name__ == "__main__":
    main()