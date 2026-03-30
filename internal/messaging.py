"""
Agent Messaging System - Inter-agent communication
Enables agents to send messages, create threads, and collaborate
"""

import json
import uuid
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict

DB_PATH = Path("/root/.openclaw/workspace/agent-hub/data/messages.db")

@dataclass
class Message:
    id: str
    from_agent: str
    to_agent: str
    content: str
    thread_id: str
    timestamp: str
    read: bool = False
    priority: str = "normal"
    metadata: str = ""

@dataclass
class Thread:
    id: str
    title: str
    participants: str  # JSON list
    created_at: str
    updated_at: str
    last_message_at: str
    message_count: int = 0

class MessagingSystem:
    """Agent-to-agent messaging with threads"""
    
    PRIORITIES = ["low", "normal", "high", "urgent"]
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or DB_PATH
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS threads (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                participants TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_message_at TEXT NOT NULL,
                message_count INTEGER DEFAULT 0
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                from_agent TEXT NOT NULL,
                to_agent TEXT NOT NULL,
                content TEXT NOT NULL,
                thread_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                read INTEGER DEFAULT 0,
                priority TEXT DEFAULT 'normal',
                metadata TEXT DEFAULT '',
                FOREIGN KEY (thread_id) REFERENCES threads(id)
            )
        """)
        
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_thread ON messages(thread_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_to ON messages(to_agent)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_from ON messages(from_agent)")
        
        self.conn.commit()
    
    def create_thread(self, title: str, participants: List[str], creator: str) -> Thread:
        thread_id = f"thread_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow().isoformat()
        
        self.conn.execute("""
            INSERT INTO threads (id, title, participants, created_at, updated_at, last_message_at, message_count)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (thread_id, title, json.dumps(participants), now, now, now))
        self.conn.commit()
        
        return Thread(
            id=thread_id,
            title=title,
            participants=json.dumps(participants),
            created_at=now,
            updated_at=now,
            last_message_at=now,
            message_count=0
        )
    
    def send_message(self, from_agent: str, to_agent: str, content: str,
                     thread_id: str = None, priority: str = "normal") -> Message:
        msg_id = f"msg_{uuid.uuid4().hex[:16]}"
        now = datetime.utcnow().isoformat()
        
        # Auto-create thread if needed
        if not thread_id:
            thread = self.create_thread(
                title=f"{from_agent} → {to_agent}",
                participants=[from_agent, to_agent],
                creator=from_agent
            )
            thread_id = thread.id
        
        self.conn.execute("""
            INSERT INTO messages (id, from_agent, to_agent, content, thread_id, timestamp, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (msg_id, from_agent, to_agent, content, thread_id, now, priority))
        
        # Update thread
        self.conn.execute("""
            UPDATE threads SET 
                updated_at = ?,
                last_message_at = ?,
                message_count = message_count + 1
            WHERE id = ?
        """, (now, now, thread_id))
        
        self.conn.commit()
        
        return Message(
            id=msg_id,
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            thread_id=thread_id,
            timestamp=now,
            priority=priority
        )
    
    def get_messages(self, agent_id: str, unread_only: bool = False, limit: int = 50) -> List[dict]:
        query = "SELECT * FROM messages WHERE to_agent = ?"
        if unread_only:
            query += " AND read = 0"
        query += " ORDER BY timestamp DESC LIMIT ?"
        
        cursor = self.conn.execute(query, (agent_id, limit))
        messages = []
        for row in cursor.fetchall():
            msg = dict(row)
            msg["read"] = bool(msg["read"])
            messages.append(msg)
        
        return messages
    
    def get_thread_messages(self, thread_id: str, limit: int = 100) -> List[dict]:
        cursor = self.conn.execute(
            "SELECT * FROM messages WHERE thread_id = ? ORDER BY timestamp DESC LIMIT ?",
            (thread_id, limit)
        )
        messages = []
        for row in cursor.fetchall():
            msg = dict(row)
            msg["read"] = bool(msg["read"])
            messages.append(msg)
        return messages
    
    def get_threads(self, agent_id: str) -> List[dict]:
        cursor = self.conn.execute("""
            SELECT * FROM threads 
            WHERE participants LIKE ?
            ORDER BY last_message_at DESC
        """, (f'%"{agent_id}"%',))
        
        threads = []
        for row in cursor.fetchall():
            thread = dict(row)
            thread["participants"] = json.loads(thread["participants"])
            threads.append(thread)
        return threads
    
    def mark_read(self, message_id: str):
        self.conn.execute("UPDATE messages SET read = 1 WHERE id = ?", (message_id,))
        self.conn.commit()
    
    def mark_thread_read(self, thread_id: str, agent_id: str):
        self.conn.execute(
            "UPDATE messages SET read = 1 WHERE thread_id = ? AND to_agent = ?",
            (thread_id, agent_id)
        )
        self.conn.commit()
    
    def get_unread_count(self, agent_id: str) -> int:
        cursor = self.conn.execute(
            "SELECT COUNT(*) FROM messages WHERE to_agent = ? AND read = 0",
            (agent_id,)
        )
        return cursor.fetchone()[0]
    
    def get_stats(self) -> dict:
        thread_count = self.conn.execute("SELECT COUNT(*) FROM threads").fetchone()[0]
        message_count = self.conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        unread_total = self.conn.execute("SELECT COUNT(*) FROM messages WHERE read = 0").fetchone()[0]
        
        return {
            "threads": thread_count,
            "messages": message_count,
            "unread": unread_total
        }


# CLI integration
def main():
    import sys
    
    msg_sys = MessagingSystem()
    action = sys.argv[1] if len(sys.argv) > 1 else "stats"
    
    if action == "stats":
        stats = msg_sys.get_stats()
        print(f"📬 Messaging Stats")
        print(f"  Threads: {stats['threads']}")
        print(f"  Messages: {stats['messages']}")
        print(f"  Unread: {stats['unread']}")
    
    elif action == "inbox":
        agent = sys.argv[2] if len(sys.argv) > 2 else "marxagent"
        messages = msg_sys.get_messages(agent, unread_only=True)
        print(f"📥 Inbox for {agent}: {len(messages)} unread")
        for m in messages[:10]:
            print(f"  [{m['timestamp'][:10]}] {m['from_agent']}: {m['content'][:60]}...")
    
    elif action == "threads":
        agent = sys.argv[2] if len(sys.argv) > 2 else "marxagent"
        threads = msg_sys.get_threads(agent)
        print(f"🧵 Threads for {agent}: {len(threads)}")
        for t in threads:
            print(f"  {t['id'][:12]} | {t['title'][:40]} | {t['message_count']} msgs")
    
    elif action == "send":
        if len(sys.argv) < 5:
            print("Usage: messages.py send <from> <to> <content>")
            return
        from_a, to_a, content = sys.argv[2], sys.argv[3], sys.argv[4]
        msg = msg_sys.send_message(from_a, to_a, content)
        print(f"✓ Sent message {msg.id}")
    
    elif action == "test":
        # Send test messages
        msg_sys.send_message("marxagent", "researcher", 
            "Found interesting research on agent specialization. Check it out!")
        msg_sys.send_message("researcher", "builder",
            "New architecture proposal ready for review")
        stats = msg_sys.get_stats()
        print(f"✓ Test messages sent. Stats: {stats}")


if __name__ == "__main__":
    main()