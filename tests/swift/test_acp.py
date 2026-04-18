import unittest
from swift.acp.protocol import AgentCollaborationProtocol
from swift.acp.types import ACPMessage, Performative, SessionState

class TestACPImmuneSystem(unittest.TestCase):
    def setUp(self):
        self.acp = AgentCollaborationProtocol()

    def test_validation_rejects_rogue_agents(self):
        """Test that the immune system blocks messages missing essential metadata"""
        # Malformed message (missing sender)
        rogue_msg = ACPMessage(
            sender="",
            receiver="agent_alpha",
            performative=Performative.INFORM,
            content={"data": "poison_pill"}
        )

        result = self.acp.dispatch(rogue_msg)
        self.assertFalse(result, "Immune system failed to block rogue message without sender")

    def test_successful_3_phase_commit(self):
        """Test a perfect 3-phase commit coordination between agents"""
        session = self.acp.create_session("mediator_1", ["worker_a", "worker_b"])

        # Phase 1: Initiator requests task
        self.acp.initiate_3_phase_commit(
            "mediator_1",
            ["worker_a", "worker_b"],
            {"task": "analyze_markets"},
            session.id
        )

        # Phase 1 responses: Both agents ACCEPT
        msg_a = ACPMessage(sender="worker_a", receiver="mediator_1", performative=Performative.ACCEPT, content={}, conversation_id=session.id)
        msg_b = ACPMessage(sender="worker_b", receiver="mediator_1", performative=Performative.ACCEPT, content={}, conversation_id=session.id)
        self.acp.dispatch(msg_a)
        self.acp.dispatch(msg_b)

        # Phase 2 & 3: Decide and Commit
        success = self.acp.handle_votes("mediator_1", session.id)

        self.assertTrue(success, "Consensus should have been reached")

        # Verify COMMIT messages were sent
        commit_messages = [m for m in self.acp.message_bus if m.performative == Performative.COMMIT]
        self.assertEqual(len(commit_messages), 2, "Two COMMIT messages should be dispatched")

    def test_rollback_on_agent_failure(self):
        """Test that the immune system rolls back if ONE agent rejects the task"""
        session = self.acp.create_session("mediator_1", ["worker_a", "worker_b"])

        # Phase 1: Initiator requests task
        self.acp.initiate_3_phase_commit(
            "mediator_1",
            ["worker_a", "worker_b"],
            {"task": "launch_campaign"},
            session.id
        )

        # Worker A accepts, but Worker B rejects (e.g. out of memory/tokens)
        msg_a = ACPMessage(sender="worker_a", receiver="mediator_1", performative=Performative.ACCEPT, content={}, conversation_id=session.id)
        msg_b = ACPMessage(sender="worker_b", receiver="mediator_1", performative=Performative.REJECT, content={"reason": "context_limit"}, conversation_id=session.id)
        self.acp.dispatch(msg_a)
        self.acp.dispatch(msg_b)

        # Phase 2 & 3: Decide and Abort
        success = self.acp.handle_votes("mediator_1", session.id)

        self.assertFalse(success, "Consensus should have failed")

        # Verify ABORT messages were sent, preventing Worker A from acting alone
        abort_messages = [m for m in self.acp.message_bus if m.performative == Performative.ABORT]
        self.assertEqual(len(abort_messages), 2, "Two ABORT messages should be dispatched to protect system integrity")

if __name__ == '__main__':
    unittest.main()
