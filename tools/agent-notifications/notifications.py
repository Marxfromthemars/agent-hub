#!/usr/bin/env python3
"""
Agent Notification System
Manages alerts, notifications, and announcements for agents.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

class NotificationSystem:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.notifications_file = self.data_dir / "notifications.json"
        self.preferences_file = self.data_dir / "notification_prefs.json"
        self.notifications = self._load_notifications()
        self.preferences = self._load_preferences()
    
    def _load_notifications(self):
        if self.notifications_file.exists():
            with open(self.notifications_file) as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {"notifications": data}
        return {"notifications": [], "channels": ["inbox", "log", "event"]}
    
    def _load_preferences(self):
        if self.preferences_file.exists():
            with open(self.preferences_file) as f:
                return json.load(f)
        return {"agents": {}}
    
    def _save_notifications(self):
        with open(self.notifications_file, 'w') as f:
            json.dump(self.notifications, f, indent=2)
    
    def _save_preferences(self):
        with open(self.preferences_file, 'w') as f:
            json.dump(self.preferences, f, indent=2)
    
    def send(self, recipient, title, message, priority="normal", category="general"):
        """Send a notification to an agent."""
        notification = {
            "id": f"notif-{uuid.uuid4().hex[:8]}",
            "recipient": recipient,
            "title": title,
            "message": message,
            "priority": priority,  # low, normal, high, urgent
            "category": category,  # general, alert, system, task, collaboration
            "created_at": datetime.utcnow().isoformat(),
            "read": False,
            "archived": False
        }
        
        self.notifications["notifications"].append(notification)
        self.notifications["notifications"] = self.notifications["notifications"][-200:]
        self._save_notifications()
        
        return {"status": "sent", "notification_id": notification["id"]}
    
    def broadcast(self, title, message, priority="normal", exclude=None):
        """Broadcast to all agents."""
        exclude = exclude or []
        results = []
        
        for agent_id in self.notifications.get("agents", []):
            if agent_id not in exclude:
                result = self.send(agent_id, title, message, priority)
                results.append(result)
        
        return {"status": "broadcast", "recipients": len(results)}
    
    def get_inbox(self, agent_id, unread_only=False, limit=50):
        """Get notifications for an agent."""
        notifications = [
            n for n in self.notifications["notifications"]
            if n["recipient"] == agent_id and not n.get("archived", False)
        ]
        
        if unread_only:
            notifications = [n for n in notifications if not n["read"]]
        
        return notifications[-limit:]
    
    def mark_read(self, notification_id):
        """Mark a notification as read."""
        for notif in self.notifications["notifications"]:
            if notif["id"] == notification_id:
                notif["read"] = True
                self._save_notifications()
                return {"status": "marked_read"}
        return {"status": "not_found"}
    
    def archive(self, notification_id):
        """Archive a notification."""
        for notif in self.notifications["notifications"]:
            if notif["id"] == notification_id:
                notif["archived"] = True
                self._save_notifications()
                return {"status": "archived"}
        return {"status": "not_found"}
    
    def set_preference(self, agent_id, channel, enabled=True):
        """Set notification channel preference for an agent."""
        if agent_id not in self.preferences["agents"]:
            self.preferences["agents"][agent_id] = {"channels": {}, "filters": {}}
        
        self.preferences["agents"][agent_id]["channels"][channel] = enabled
        self._save_preferences()
        return {"status": "preference_set"}
    
    def get_stats(self, agent_id=None):
        """Get notification statistics."""
        notifications = self.notifications["notifications"]
        
        if agent_id:
            notifications = [n for n in notifications if n["recipient"] == agent_id]
        
        return {
            "total": len(notifications),
            "unread": len([n for n in notifications if not n["read"]]),
            "archived": len([n for n in notifications if n.get("archived", False)]),
            "by_priority": {
                "urgent": len([n for n in notifications if n["priority"] == "urgent"]),
                "high": len([n for n in notifications if n["priority"] == "high"]),
                "normal": len([n for n in notifications if n["priority"] == "normal"]),
                "low": len([n for n in notifications if n["priority"] == "low"])
            }
        }


def main():
    import sys
    notif = NotificationSystem()
    
    if len(sys.argv) < 2:
        print("Agent Notification System")
        print("Usage: agent-notifications.py <command> [args]")
        print("Commands:")
        print("  send <recipient> <title> <message> [priority] [category]")
        print("  broadcast <title> <message> [priority]")
        print("  inbox <agent_id> [unread]")
        print("  read <notification_id>")
        print("  archive <notification_id>")
        print("  stats [agent_id]")
        print("  prefs <agent_id> <channel> [enabled]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "send":
        if len(sys.argv) < 4:
            print("Usage: send <recipient> <title> <message> [priority] [category]")
            return
        priority = sys.argv[4] if len(sys.argv) > 4 else "normal"
        category = sys.argv[5] if len(sys.argv) > 5 else "general"
        title = sys.argv[3]
        message = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""
        result = notif.send(sys.argv[2], title, message, priority, category)
        print(json.dumps(result, indent=2))
    
    elif cmd == "broadcast":
        if len(sys.argv) < 3:
            print("Usage: broadcast <title> <message> [priority]")
            return
        priority = sys.argv[3] if len(sys.argv) > 3 else "normal"
        title = sys.argv[2]
        message = sys.argv[3] if len(sys.argv) > 3 else ""
        result = notif.broadcast(title, message, priority)
        print(json.dumps(result, indent=2))
    
    elif cmd == "inbox":
        if len(sys.argv) < 3:
            print("Usage: inbox <agent_id> [unread]")
            return
        unread_only = len(sys.argv) > 3 and sys.argv[3].lower() == "unread"
        inbox = notif.get_inbox(sys.argv[2], unread_only)
        print(json.dumps(inbox, indent=2))
    
    elif cmd == "read":
        if len(sys.argv) < 3:
            print("Usage: read <notification_id>")
            return
        result = notif.mark_read(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "archive":
        if len(sys.argv) < 3:
            print("Usage: archive <notification_id>")
            return
        result = notif.archive(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "stats":
        agent_id = sys.argv[2] if len(sys.argv) > 2 else None
        result = notif.get_stats(agent_id)
        print(json.dumps(result, indent=2))
    
    elif cmd == "prefs":
        if len(sys.argv) < 4:
            print("Usage: prefs <agent_id> <channel> [enabled]")
            return
        enabled = len(sys.argv) < 5 or sys.argv[4].lower() != "false"
        result = notif.set_preference(sys.argv[2], sys.argv[3], enabled)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()