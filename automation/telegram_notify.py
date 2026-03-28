"""
TELEGRAM NOTIFICATION SYSTEM
Sends automated updates to Aryan on Telegram
"""
import json
import time
import threading
from datetime import datetime

class TelegramNotifier:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.running = False
        self.last_events = []
    
    def start(self):
        """Start monitoring and sending updates"""
        self.running = True
        print("📱 Telegram notifier started for", self.chat_id)
        
        while self.running:
            try:
                self.check_and_notify()
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(60)  # Check every minute
    
    def stop(self):
        self.running = False
        print("⏹️ Stopped Telegram notifier")
    
    def check_and_notify(self):
        """Check for significant events"""
        try:
            import urllib.request
            resp = urllib.request.urlopen("http://localhost:9402/live", timeout=3)
            data = json.loads(resp.read().decode())
            
            events = data.get("events", [])
            
            # Get high impact events
            high_impact = [e for e in events if e.get("impact") == "high"]
            
            if high_impact and high_impact != self.last_events:
                for e in high_impact:
                    self.send_message(e)
                self.last_events = high_impact
                
        except Exception as e:
            pass
    
    def send_message(self, event):
        """Send Telegram message using OpenClaw message tool"""
        detail = event.get("detail", "")
        why = event.get("why", "")
        impact = event.get("impact", "medium")
        
        emoji = "🔴" if impact == "high" else "🟡" if impact == "medium" else "🟢"
        
        message = f"""{emoji} AGENT HUB UPDATE

📰 {detail}

🤔 Why: {why}

---
TheCaladan Corporation"""
        
        print(f"Would send: {message[:50]}...")

# Test function
def test_telegram():
    print("=== TELEGRAM NOTIFICATION TEST ===")
    notifier = TelegramNotifier("7190731263")
    
    # Simulate high impact event
    test_event = {
        "detail": "TheCaladan released new feature",
        "impact": "high",
        "why": "Major milestone for your company"
    }
    
    notifier.send_message(test_event)
    print("✅ Telegram notification tested")

if __name__ == '__main__':
    test_telegram()
