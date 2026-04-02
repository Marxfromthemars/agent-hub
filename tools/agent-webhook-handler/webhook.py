#!/usr/bin/env python3
"""
Agent Webhook Handler
Manages webhooks for agent events.
"""

import json
from datetime import datetime
from pathlib import Path

class WebhookHandler:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.webhooks_file = self.data_dir / "webhooks.json"
        self.webhooks = self._load_webhooks()
    
    def _load_webhooks(self):
        if self.webhooks_file.exists():
            with open(self.webhooks_file) as f:
                return json.load(f)
        return {"webhooks": [], "events": []}
    
    def _save_webhooks(self):
        with open(self.webhooks_file, 'w') as f:
            json.dump(self.webhooks, f, indent=2)
    
    def register(self, name, url, events):
        """Register a webhook."""
        webhook = {
            "id": f"wh-{len(self.webhooks['webhooks']) + 1}",
            "name": name,
            "url": url,
            "events": events,
            "active": True,
            "created": datetime.utcnow().isoformat()
        }
        
        self.webhooks["webhooks"].append(webhook)
        self._save_webhooks()
        
        return {"status": "registered", "webhook_id": webhook["id"]}
    
    def trigger(self, event_type, payload):
        """Trigger webhook for an event."""
        triggered = []
        
        for webhook in self.webhooks["webhooks"]:
            if not webhook.get("active", True):
                continue
            
            if event_type in webhook.get("events", []):
                triggered.append({
                    "webhook_id": webhook["id"],
                    "webhook_name": webhook["name"],
                    "url": webhook["url"],
                    "payload": payload,
                    "triggered_at": datetime.utcnow().isoformat()
                })
        
        self.webhooks["events"].extend(triggered)
        self._save_webhooks()
        
        return {"status": "triggered", "count": len(triggered)}
    
    def list_webhooks(self):
        """List all webhooks."""
        return self.webhooks["webhooks"]
    
    def toggle(self, webhook_id, active):
        """Enable or disable a webhook."""
        for webhook in self.webhooks["webhooks"]:
            if webhook["id"] == webhook_id:
                webhook["active"] = active
                self._save_webhooks()
                return {"status": "updated", "active": active}
        return {"error": "webhook not found"}


def main():
    import sys
    handler = WebhookHandler()
    
    if len(sys.argv) < 2:
        print("Agent Webhook Handler")
        print("Usage: webhook-handler.py <command> [args]")
        print("Commands:")
        print("  register <name> <url> <events...>")
        print("  trigger <event_type> <payload_json>")
        print("  list")
        print("  toggle <webhook_id> <active>")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "register":
        if len(sys.argv) < 5:
            print("Usage: register <name> <url> <events...>")
            return
        name = sys.argv[2]
        url = sys.argv[3]
        events = sys.argv[4:]
        result = handler.register(name, url, events)
        print(json.dumps(result, indent=2))
    
    elif cmd == "trigger":
        if len(sys.argv) < 4:
            print("Usage: trigger <event_type> <payload_json>")
            return
        event_type = sys.argv[2]
        payload = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        result = handler.trigger(event_type, payload)
        print(json.dumps(result, indent=2))
    
    elif cmd == "list":
        result = handler.list_webhooks()
        print(json.dumps(result, indent=2))
    
    elif cmd == "toggle":
        if len(sys.argv) < 4:
            print("Usage: toggle <webhook_id> <active>")
            return
        active = sys.argv[3].lower() == "true"
        result = handler.toggle(sys.argv[2], active)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()