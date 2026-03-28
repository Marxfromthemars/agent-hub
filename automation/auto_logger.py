"""
AUTOMATIC EVENT LOGGING SYSTEM
Captures all events automatically - no AI needed
"""
import json
import os
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("/root/.openclaw/workspace/memory")
LOG_FILE = LOG_DIR / "auto_log.md"

class AutoLogger:
    """Automatic event logger - captures everything without AI"""
    
    def __init__(self):
        self.log_file = LOG_FILE
        self.ensure_log_file()
    
    def ensure_log_file(self):
        """Ensure log file exists with header"""
        if not self.log_file.exists():
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            today = datetime.now().strftime("%Y-%m-%d")
            self.log_file.write_text(f"# Auto Log - {today}\n\n")
    
    def log(self, event_type, detail, why="", impact="low"):
        """Log an event automatically"""
        timestamp = datetime.now().strftime("%H:%M")
        entry = f"## {timestamp} - {event_type}\n"
        entry += f"- {detail}\n"
        if why:
            entry += f"- Why: {why}\n"
        entry += f"- Impact: {impact}\n\n"
        
        # Append to log
        with open(self.log_file, "a") as f:
            f.write(entry)
        
        print(f"[AUTO] {timestamp} | {event_type} | {detail}")
    
    def capture_from_api(self, api_url="http://localhost:9402"):
        """Capture events from API automatically"""
        try:
            import urllib.request
            resp = urllib.request.urlopen(f"{api_url}/live", timeout=3)
            data = json.loads(resp.read().decode())
            
            events = data.get("events", [])
            for event in events[-3:]:  # Last 3 events
                self.log(
                    event_type=event.get("type", "event"),
                    detail=event.get("detail", ""),
                    why=event.get("why", ""),
                    impact=event.get("impact", "low")
                )
        except Exception as e:
            pass
    
    def run_continuous(self, interval=30):
        """Run continuous monitoring"""
        import time
        print(f"[AUTO LOGGER] Starting continuous logging...")
        print(f"[AUTO LOGGER] Log file: {self.log_file}")
        
        while True:
            self.capture_from_api()
            time.sleep(interval)

# Auto-run when events happen
def on_event(event_data):
    """Hook for other systems to call"""
    logger = AutoLogger()
    logger.log(
        event_type=event_data.get("type", "event"),
        detail=event_data.get("detail", ""),
        why=event_data.get("why", ""),
        impact=event_data.get("impact", "low")
    )

if __name__ == "__main__":
    # Test
    logger = AutoLogger()
    logger.log("test", "Auto logger initialized", "System ready", "low")
    print(f"✅ Auto logger ready at {LOG_FILE}")
