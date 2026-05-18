#!/usr/bin/env python3
"""
Agent-to-Agent Dispatcher - Handles direct agent communication
"""

import json
import uuid
import time
import asyncio
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum


class ChannelType(Enum):
    DIRECT = "direct"
    PUBSUB = "pubsub"
    BROADCAST = "broadcast"
    REQUEST_RESPONSE = "request_response"


@dataclass
class Channel:
    """Communication channel between agents."""
    channel_id: str
    type: ChannelType
    participants: List[str]
    created_at: float
    metadata: Dict = field(default_factory=dict)


class AgentAgentDispatcher:
    """Manages agent-to-agent communication with handshake support."""

    def __init__(self):
        self.channels: Dict[str, Channel] = {}
        self.connections: Dict[str, Dict] = {}  # agent_id -> connection info
        self.message_handlers: Dict[str, Callable] = {}
        self.pending_handshakes: Dict[str, Dict] = {}

    async def create_channel(self, channel_type: ChannelType, 
                            participants: List[str], 
                            metadata: Optional[Dict] = None) -> str:
        """Create a new communication channel."""
        channel_id = str(uuid.uuid4())
        self.channels[channel_id] = Channel(
            channel_id=channel_id,
            type=channel_type,
            participants=participants,
            created_at=time.time(),
            metadata=metadata or {}
        )
        return channel_id

    async def initiate_handshake(self, sender: str, receiver: str,
                                  capabilities: List[str]) -> Dict:
        """Initiate a three-way handshake with another agent."""
        handshake_id = str(uuid.uuid4())

        handshake = {
            "handshake_id": handshake_id,
            "initiator": sender,
            "target": receiver,
            "capabilities": capabilities,
            "status": "initiated",
            "created_at": time.time()
        }

        self.pending_handshakes[handshake_id] = handshake

        # Send handshake init (would normally route via dispatcher)
        return {
            "status": "handshake_initiated",
            "handshake_id": handshake_id
        }

    async def respond_to_handshake(self, handshake_id: str, 
                                    responder: str,
                                    accepted: bool,
                                    capabilities: Optional[List[str]] = None) -> Dict:
        """Respond to a handshake request."""
        if handshake_id not in self.pending_handshakes:
            return {"error": "handshake_not_found"}

        handshake = self.pending_handshakes[handshake_id]

        if accepted:
            # Create direct channel
            channel_id = await self.create_channel(
                ChannelType.DIRECT,
                [handshake["initiator"], responder]
            )

            # Store connection info
            self.connections[handshake["initiator"]] = {
                "peer": responder,
                "channel_id": channel_id,
                "capabilities": handshake["capabilities"]
            }
            self.connections[responder] = {
                "peer": handshake["initiator"],
                "channel_id": channel_id,
                "capabilities": capabilities or []
            }

            handshake["status"] = "established"
            handshake["channel_id"] = channel_id

            return {
                "status": "handshake_accepted",
                "channel_id": channel_id
            }
        else:
            handshake["status"] = "rejected"
            return {"status": "handshake_rejected"}

    async def send_message(self, sender: str, receiver: str,
                           message: Dict, priority: int = 2) -> Dict:
        """Send a message to another agent."""
        # Check connection exists
        if sender not in self.connections:
            return {"error": "no_active_connection"}

        connection = self.connections[sender]

        # Create message envelope
        envelope = {
            "header": {
                "id": str(uuid.uuid4()),
                "timestamp": time.time(),
                "priority": priority
            },
            "sender": {"id": sender},
            "receiver": {"id": receiver, "channel": "direct"},
            "payload": message
        }

        # Route via parent dispatcher
        return {
            "status": "message_queued",
            "message_id": envelope["header"]["id"],
            "via_dispatcher": True
        }

    async def publish(self, sender: str, topic: str, 
                      message: Dict) -> Dict:
        """Publish a message to a topic."""
        envelope = {
            "header": {
                "id": str(uuid.uuid4()),
                "timestamp": time.time(),
                "topic": topic
            },
            "sender": {"id": sender},
            "receiver": {"id": topic, "channel": "pubsub"},
            "payload": message
        }

        return {
            "status": "published",
            "message_id": envelope["header"]["id"],
            "topic": topic
        }

    async def broadcast(self, sender: str, message: Dict,
                        exclude: Optional[List[str]] = None) -> Dict:
        """Broadcast a message to all connected agents."""
        envelope = {
            "header": {
                "id": str(uuid.uuid4()),
                "timestamp": time.time()
            },
            "sender": {"id": sender},
            "receiver": {"id": "all", "channel": "broadcast"},
            "payload": message
        }

        targets = [a for a in self.connections.keys() if a != sender]
        if exclude:
            targets = [a for a in targets if a not in exclude]

        return {
            "status": "broadcast_sent",
            "message_id": envelope["header"]["id"],
            "recipients": len(targets)
        }

    async def handle_connection_error(self, agent_id: str, 
                                       error: str) -> Dict:
        """Handle connection errors with retry logic."""
        connection = self.connections.get(agent_id)

        if not connection:
            return {"error": "no_connection"}

        # Increment retry count
        connection["retry_count"] = connection.get("retry_count", 0) + 1

        # Retry strategy: exponential backoff
        delay = min(300, 2 ** connection["retry_count"])

        return {
            "status": "retry_scheduled",
            "delay": delay,
            "retry_count": connection["retry_count"]
        }

    def get_connection_status(self, agent_id: str) -> Dict:
        """Get connection status for an agent."""
        if agent_id not in self.connections:
            return {"status": "disconnected"}

        connection = self.connections[agent_id]
        return {
            "status": "connected",
            "peer": connection["peer"],
            "channel_id": connection["channel_id"],
            "connected_since": connection.get("connected_at", time.time())
        }


def create_agent_dispatcher() -> AgentAgentDispatcher:
    """Factory function to create an agent-to-agent dispatcher."""
    return AgentAgentDispatcher()