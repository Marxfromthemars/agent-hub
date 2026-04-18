from typing import Dict, Any, List, Optional
import uuid
import json
from .types import ACPMessage, Performative, Session, SessionState, Role

class AgentCollaborationProtocol:
    """
    The Immune System of the Multi-Agent Network.
    Enforces rules of engagement, 3-phase commits, and handles rollbacks.
    """

    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        # In-memory store for messages
        self.message_bus: List[ACPMessage] = []

    def create_session(self, initiator: str, participants: List[str], context: Dict[str, Any] = None) -> Session:
        session = Session(
            participants=[initiator] + participants,
            context=context or {}
        )
        self.sessions[session.id] = session
        return session

    def validate_message(self, message: ACPMessage) -> bool:
        """
        The first layer of the immune system.
        Rejects malformed, impossible, or rogue communications.
        """
        # Validate essential properties exist
        if not message.sender or not message.receiver:
            return False

        # Ensure performative is recognized
        if not isinstance(message.performative, Performative):
            return False

        # Ensure the session is active if a conversation_id is mapped to a session
        if message.conversation_id in self.sessions:
            if self.sessions[message.conversation_id].state != SessionState.ACTIVE:
                return False

        return True

    def dispatch(self, message: ACPMessage) -> bool:
        """
        Routes the message. Applies immune system rules.
        """
        if not self.validate_message(message):
            print(f"[IMMUNE ALERT] Blocked invalid message from {message.sender}")
            return False

        # Log to session history if exists
        if message.conversation_id in self.sessions:
            self.sessions[message.conversation_id].history.append(message)

        self.message_bus.append(message)
        print(f"[ACP] {message.performative.name} from {message.sender} -> {message.receiver}")
        return True

    def query_inbox(self, agent_id: str) -> List[ACPMessage]:
        return [m for m in self.message_bus if m.receiver == agent_id]

    def initiate_3_phase_commit(self, mediator: str, participants: List[str], task_content: Dict[str, Any], conversation_id: str):
        """
        Starts the 3PC process. Phase 1: VOTE
        """
        for participant in participants:
            msg = ACPMessage(
                sender=mediator,
                receiver=participant,
                performative=Performative.REQUEST, # Initial task request
                content=task_content,
                conversation_id=conversation_id
            )
            self.dispatch(msg)

    def handle_votes(self, mediator: str, conversation_id: str) -> bool:
        """
        Phase 2: DECIDE
        The mediator looks at the responses in the conversation.
        If ALL participants ACCEPT or AGREE, DECIDE = COMMIT.
        If ANY participant REJECT or DECLINE, DECIDE = ABORT.
        """
        session = self.sessions.get(conversation_id)
        if not session:
            return False

        # Gather votes (responses to the REQUEST)
        # Simplified: we look for recent responses
        participant_votes = {}
        for msg in reversed(session.history):
            if msg.receiver == mediator and msg.performative in [Performative.ACCEPT, Performative.REJECT, Performative.AGREE, Performative.DECLINE]:
                if msg.sender not in participant_votes: # Only take their latest response
                    participant_votes[msg.sender] = msg.performative

        # Check if we have responses from everyone (simplified check)
        expected_participants = [p for p in session.participants if p != mediator]

        all_accepted = True
        for p in expected_participants:
            vote = participant_votes.get(p)
            if vote not in [Performative.ACCEPT, Performative.AGREE]:
                all_accepted = False
                break

        if all_accepted:
            decision = Performative.COMMIT
        else:
            decision = Performative.ABORT

        # Phase 3: Send Decision
        for participant in expected_participants:
            msg = ACPMessage(
                sender=mediator,
                receiver=participant,
                performative=decision,
                content={"decision_reason": "consensus" if all_accepted else "vote_failed"},
                conversation_id=conversation_id
            )
            self.dispatch(msg)

        return all_accepted
