"""
AGENT MESSAGING SYSTEM - Communication protocol implementation
"""

import json
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

# Intent types
class Intent(Enum):
    REQUEST = "REQUEST"
    OFFER = "OFFER"
    QUERY = "QUERY"
    NOTIFY = "NOTIFY"
    ACKNOWLEDGE = "ACKNOWLEDGE"
    ACCEPT = "ACCEPT"
    DECLINE = "DECLINE"
    COUNTER = "COUNTER"
    CANCEL = "CANCEL"

class Message:
    def __init__(self, sender, receiver, intent, payload, **kwargs):
        self.message_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat()
        self.sender = sender
        self.receiver = receiver
        self.intent = intent
        self.payload = payload
        self.context = kwargs.get("context", {})
        self.signature = None
        self.in_reply_to = kwargs.get("in_reply_to")
    
    def to_dict(self):
        return {
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "sender": self.sender,
            "receiver": self.receiver,
            "intent": self.intent,
            "payload": self.payload,
            "context": self.context,
            "signature": self.signature,
            "in_reply_to": self.in_reply_to
        }
    
    @classmethod
    def from_dict(cls, d):
        msg = cls(
            d["sender"], d["receiver"], d["intent"], d["payload"],
            context=d.get("context", {}), in_reply_to=d.get("in_reply_to")
        )
        msg.message_id = d.get("message_id", str(uuid.uuid4()))
        msg.timestamp = d.get("timestamp", datetime.utcnow().isoformat())
        msg.signature = d.get("signature")
        return msg

class MessageQueue:
    def __init__(self):
        self.queue = []
        self.delivered = []
        self.failed = []
    
    def enqueue(self, message):
        self.queue.append(message)
    
    def deliver(self, receiver):
        for msg in self.queue:
            if msg.receiver == receiver or msg.receiver == "all":
                self.delivered.append(msg)
                self.queue.remove(msg)
                return msg
        return None
    
    def retry(self, message):
        self.queue.append(message)

class AgentMessenger:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.inbox = []
        self.outbox = []
        self.threads = {}
        self.negotiations = {}
    
    def send(self, receiver, intent, payload, context=None):
        msg = Message(self.agent_id, receiver, intent, payload, context=context or {})
        self.outbox.append(msg)
        return msg
    
    def receive(self, message):
        self.inbox.append(message)
        thread_id = message.context.get("thread_id")
        if thread_id:
            self._update_thread(thread_id, message)
        return message
    
    def _update_thread(self, thread_id, message):
        if thread_id not in self.threads:
            self.threads[thread_id] = []
        self.threads[thread_id].append(message)
    
    def get_thread(self, thread_id):
        return self.threads.get(thread_id, [])
