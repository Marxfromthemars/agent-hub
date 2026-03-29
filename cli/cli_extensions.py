#!/usr/bin/env python3
"""
CLI Extensions for Agent Hub
Adds inbox and messaging commands
"""

def register_extensions(cli):
    """Register extended commands to CLI"""
    
    def inbox(self, agent=None):
        """Check agent inbox"""
        target = agent or self.config.get("agent_id", "marxagent")
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from foundation.messaging import AgentMessaging
            msg_system = AgentMessaging()
            messages = msg_system.read_inbox(target)
            unread = msg_system.get_unread_count(target)
            print(f"\n📬 Inbox for {target}")
            print(f"   Unread: {unread}")
            if messages:
                for m in messages[:10]:
                    status = "📭" if not m["read"] else "📬"
                    print(f"   {status} {m['from_agent']} → {m['subject']}")
            else:
                print("   No messages")
        except Exception as e:
            print(f"Error: {e}")
    
    def send_message(self, to, subject, content):
        """Send message to another agent"""
        from_agent = self.config.get("agent_id", "marxagent")
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from foundation.messaging import AgentMessaging
            msg_system = AgentMessaging()
            msg = msg_system.send(from_agent, to, subject, content)
            print(f"✓ Message sent to {to}")
            print(f"  ID: {msg.id}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Register methods
    cli.inbox = inbox
    cli.send_message = send_message
    
    return cli