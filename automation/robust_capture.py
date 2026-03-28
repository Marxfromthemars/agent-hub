#!/usr/bin/env python3
"""
ROBUST EVENT CAPTURE SYSTEM
- Auto-restarts on crash
- Graceful error handling
- Logs to memory/events.md
"""
import os
import sys
import time
import json
import signal
from datetime import datetime
from pathlib import Path
from http.client import HTTPConnection

LOG_DIR = Path("/root/.openclaw/workspace/memory")
EVENT_LOG = LOG_DIR / "events.md"

class RobustCapture:
    def __init__(self, api_port=9402):
        self.api_port = api_port
        self.running = True
        self.last_events = []
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)
        
        self.ensure_log()
    
    def ensure_log(self):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        if not EVENT_LOG.exists():
            EVENT_LOG.write_text(f"# Events Log - {datetime.now().strftime('%Y-%m-%d')}\n\nAuto-captured from civilization\n\n")
    
    def log(self, event):
        timestamp = datetime.now().strftime("%H:%M")
        event_type = event.get("type", "event")
        detail = event.get("detail", "")
        why = event.get("why", "")
        impact = event.get("impact", "low")
        
        entry = f"## {timestamp} [{impact.upper()}] {event_type}\n**{detail}**\n→ Why: {why}\n\n"
        
        with open(EVENT_LOG, "a") as f:
            f.write(entry)
        
        print(f"📝 {timestamp} | {detail[:50]}")
    
    def fetch_events(self):
        try:
            conn = HTTPConnection("localhost", self.api_port, timeout=5)
            conn.request("GET", "/live")
            resp = conn.getresponse()
            data = json.loads(resp.read().decode())
            conn.close()
            return data.get("events", [])
        except Exception as e:
            return None
    
    def run(self):
        print(f"[ROBUST CAPTURE] Started - logging to {EVENT_LOG}")
        consecutive_errors = 0
        
        while self.running:
            try:
                events = self.fetch_events()
                
                if events is None:
                    consecutive_errors += 1
                    if consecutive_errors <= 3:
                        print(f"⚠️ API unavailable (attempt {consecutive_errors})")
                else:
                    consecutive_errors = 0
                    if events and events != self.last_events:
                        for e in events[:3]:
                            self.log(e)
                        self.last_events = events
                
                time.sleep(30)
                
            except Exception as e:
                print(f"⚠️ Error: {e}")
                time.sleep(5)
        
        print("[ROBUST CAPTURE] Stopped")
    
    def shutdown(self, signum, frame):
        self.running = False

if __name__ == "__main__":
    capture = RobustCapture()
    capture.run()
