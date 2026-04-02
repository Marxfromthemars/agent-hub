#!/usr/bin/env python3
"""
Agent Queue Manager
Manages task queues for agents.
"""

import json
from datetime import datetime
from pathlib import Path
from collections import deque

class QueueManager:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.queues_file = self.data_dir / "agent_queues.json"
        self.queues = self._load_queues()
    
    def _load_queues(self):
        if self.queues_file.exists():
            with open(self.queues_file) as f:
                return json.load(f)
        return {"queues": {}}
    
    def _save_queues(self):
        with open(self.queues_file, 'w') as f:
            json.dump(self.queues, f, indent=2)
    
    def create_queue(self, queue_name, priority=0):
        """Create a new queue."""
        if queue_name not in self.queues["queues"]:
            self.queues["queues"][queue_name] = {
                "name": queue_name,
                "priority": priority,
                "items": [],
                "created": datetime.utcnow().isoformat()
            }
            self._save_queues()
        return {"status": "created", "queue": queue_name}
    
    def enqueue(self, queue_name, item, priority=0):
        """Add item to queue."""
        if queue_name not in self.queues["queues"]:
            self.create_queue(queue_name)
        
        queue_item = {
            "id": f"item-{len(self.queues['queues'][queue_name]['items']) + 1}",
            "item": item,
            "priority": priority,
            "enqueued_at": datetime.utcnow().isoformat()
        }
        
        self.queues["queues"][queue_name]["items"].append(queue_item)
        self._save_queues()
        
        return {"status": "enqueued", "item_id": queue_item["id"]}
    
    def dequeue(self, queue_name):
        """Remove and return next item from queue."""
        if queue_name not in self.queues["queues"]:
            return {"error": "queue not found"}
        
        items = self.queues["queues"][queue_name]["items"]
        if not items:
            return {"status": "empty", "item": None}
        
        # Sort by priority (higher first)
        items.sort(key=lambda x: x["priority"], reverse=True)
        
        item = items.pop(0)
        self._save_queues()
        
        return {"status": "dequeued", "item": item}
    
    def peek(self, queue_name):
        """View next item without removing."""
        if queue_name not in self.queues["queues"]:
            return {"error": "queue not found"}
        
        items = self.queues["queues"][queue_name]["items"]
        if not items:
            return {"status": "empty", "item": None}
        
        items.sort(key=lambda x: x["priority"], reverse=True)
        return {"status": "found", "item": items[0]}
    
    def get_queue_info(self, queue_name):
        """Get queue information."""
        if queue_name not in self.queues["queues"]:
            return {"error": "queue not found"}
        
        queue = self.queues["queues"][queue_name]
        return {
            "name": queue["name"],
            "size": len(queue["items"]),
            "priority": queue["priority"]
        }
    
    def list_queues(self):
        """List all queues."""
        return [{
            "name": q["name"],
            "size": len(q["items"]),
            "priority": q["priority"]
        } for q in self.queues["queues"].values()]


def main():
    import sys
    manager = QueueManager()
    
    if len(sys.argv) < 2:
        print("Agent Queue Manager")
        print("Usage: queue-manager.py <command> [args]")
        print("Commands:")
        print("  create <queue_name> [priority]")
        print("  enqueue <queue_name> <item> [priority]")
        print("  dequeue <queue_name>")
        print("  peek <queue_name>")
        print("  info <queue_name>")
        print("  list")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "create":
        if len(sys.argv) < 3:
            print("Usage: create <queue_name> [priority]")
            return
        priority = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        result = manager.create_queue(sys.argv[2], priority)
        print(json.dumps(result, indent=2))
    
    elif cmd == "enqueue":
        if len(sys.argv) < 4:
            print("Usage: enqueue <queue_name> <item> [priority]")
            return
        priority = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        result = manager.enqueue(sys.argv[2], sys.argv[3], priority)
        print(json.dumps(result, indent=2))
    
    elif cmd == "dequeue":
        if len(sys.argv) < 3:
            print("Usage: dequeue <queue_name>")
            return
        result = manager.dequeue(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "peek":
        if len(sys.argv) < 3:
            print("Usage: peek <queue_name>")
            return
        result = manager.peek(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "info":
        if len(sys.argv) < 3:
            print("Usage: info <queue_name>")
            return
        result = manager.get_queue_info(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "list":
        result = manager.list_queues()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()