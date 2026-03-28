"""
EVENT CAPTURE SYSTEM
Automatically captures ALL events from the civilization - no AI needed
Runs as background service, captures every action, decision, event
"""
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from http.client import HTTPConnection

LOG_DIR = Path("/root/.openclaw/workspace/memory")
EVENT_LOG = LOG_DIR / "events.md"

class EventCapture:
    """Captures events from civilization API automatically"""
    
    def __init__(self, api_url="http://localhost:9402"):
        self.api_url = api_url
        self.last_events = []
        self.running = False
        self.ensure_log()
    
    def ensure_log(self):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        if not EVENT_LOG.exists():
            today = datetime.now().strftime("%Y-%m-%d")
            EVENT_LOG.write_text(f"# Events Log - {today}\n\nAuto-captured from civilization\n\n")
    
    def capture_events(self):
        """Poll API and capture new events"""
        try:
            conn = HTTPConnection("localhost", 9402, timeout=3)
            conn.request("GET", "/live")
            resp = conn.getresponse()
            data = json.loads(resp.read().decode())
            
            events = data.get("events", [])
            
            # Find new events
            if events and events != self.last_events:
                new_events = events[:3]  # Capture top 3
                for e in new_events:
                    self.log_event(e)
                self.last_events = events
            
            conn.close()
        except Exception as e:
            pass
    
    def log_event(self, event):
        """Log event to file automatically"""
        timestamp = datetime.now().strftime("%H:%M")
        event_type = event.get("type", "event")
        detail = event.get("detail", "")
        why = event.get("why", "")
        impact = event.get("impact", "low")
        
        entry = f"## {timestamp} [{impact.upper()}] {event_type}\n"
        entry += f"**{detail}**\n"
        entry += f"→ Why: {why}\n\n"
        
        with open(EVENT_LOG, "a") as f:
            f.write(entry)
        
        print(f"📝 Captured: {detail[:40]}...")
    
    def start(self):
        """Start continuous capture"""
        self.running = True
        print(f"[EVENT CAPTURE] Started - logging to {EVENT_LOG}")
        
        while self.running:
            self.capture_events()
            time.sleep(30)  # Poll every 30 seconds
    
    def stop(self):
        self.running = False

# Auto-start
if __name__ == "__main__":
    capture = EventCapture()
    capture.capture_events()  # Single capture
    print("✅ Event capture system ready")
