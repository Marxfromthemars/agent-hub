#!/usr/bin/env python3
"""
Agent Dispatcher - Routes messages between agents
"""

import json
import uuid
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class MessageStatus(Enum):
    PENDING = "pending"
    ROUTING = "routing"
    DELIVERED = "delivered"
    FAILED = "failed"
    ACKNOWLEDGED = "acknowledged"


@dataclass
class AgentInfo:
    agent_id: str
    name: str
    endpoint: str
    capabilities: List[str] = field(default_factory=list)
    status: str = "online"
    last_seen: float = 0.0


class AgentDispatcher:
    """Routes messages between agents with handshake and security integration."""

    def __init__(self, port: int = 8207):
        self.port = port
        self.agents: Dict[str, AgentInfo] = {}
        self.message_queue: Dict[str, List[Dict]] = {}
        self.channels: Dict[str, Any] = {}
        self.security_layer = SecurityLayer()

    async def register_agent(self, agent_id: str, info: Dict) -> Dict:
        """Register an agent with the dispatcher."""
        self.agents[agent_id] = AgentInfo(
            agent_id=agent_id,
            name=info.get("name", agent_id),
            endpoint=info.get("endpoint", ""),
            capabilities=info.get("capabilities", []),
            last_seen=time.time()
        )
        self.message_queue[agent_id] = []
        return {"status": "registered", "agent_id": agent_id}

    async def heartbeat(self, agent_id: str) -> Dict:
        """Update agent heartbeat."""
        if agent_id in self.agents:
            self.agents[agent_id].last_seen = time.time()
            self.agents[agent_id].status = "online"
            return {"status": "alive"}
        return {"error": "agent_not_found"}

    async def dispatch_message(self, message: Dict) -> Dict:
        """Route a message to the target agent."""
        receiver_id = message.get("receiver", {}).get("id")

        # Verify message
        valid, reason = await self.security_layer.verify(message)
        if not valid:
            return {"error": f"verification_failed: {reason}"}

        # Find target agent
        if receiver_id not in self.agents:
            return {"error": "receiver_not_found"}

        target = self.agents[receiver_id]

        # Queue for delivery
        message_id = message.get("header", {}).get("id", str(uuid.uuid4()))
        self.message_queue[receiver_id].append(message)

        return {"status": "queued", "message_id": message_id}

    async def get_messages(self, agent_id: str) -> List[Dict]:
        """Get pending messages for an agent."""
        return self.message_queue.get(agent_id, [])

    async def acknowledge_message(self, agent_id: str, message_id: str) -> Dict:
        """Acknowledge message receipt."""
        queue = self.message_queue.get(agent_id, [])
        queue[:] = [m for m in queue if m.get("header", {}).get("id") != message_id]
        return {"status": "acknowledged"}

    def get_online_agents(self) -> List[Dict]:
        """Get list of online agents."""
        return [
            {"agent_id": a.agent_id, "name": a.name, "capabilities": a.capabilities}
            for a in self.agents.values()
            if a.status == "online"
        ]


class SecurityLayer:
    """Handles message authentication and encryption."""

    def __init__(self):
        self.trusted_keys: Dict[str, str] = {}

    async def verify(self, message: Dict) -> tuple[bool, str]:
        """Verify message authenticity."""
        header = message.get("header", {})
        sender = message.get("sender", {}).get("id", "")

        # Check required fields
        if "header" not in message:
            return False, "missing_header"

        if "id" not in header:
            return False, "missing_message_id"

        # Verify signature if present
        if "security" in message and "signature" in message["security"]:
            sig_valid = self._verify_signature(message)
            if not sig_valid:
                return False, "invalid_signature"

        return True, "verified"

    def _verify_signature(self, message: Dict) -> bool:
        """Verify message signature."""
        # Placeholder for actual signature verification
        return True

    async def encrypt(self, message: Dict, session_key: str) -> Dict:
        """Encrypt message."""
        return message

    async def decrypt(self, encrypted: Dict, session_key: str) -> Dict:
        """Decrypt message."""
        return encrypted


def create_dispatcher() -> AgentDispatcher:
    """Factory function to create a dispatcher instance."""
    return AgentDispatcher()