"""
CIVILIZATION MONITOR
Automated monitoring + email alerts for TheCaladan Corporation
"""
import json
import time
from datetime import datetime
from datetime import timedelta
import threading

class CivilizationMonitor:
    def __init__(self, email):
        self.email = email
        self.running = False
        self.last_events = []
        self.sent_emails = 0
        
        # Event categories that trigger alerts
        self.alert_triggers = [
            "company_action",  # Major company moves
            "governance",       # Voting/proposals
            "research",        # New papers
            "conflict"         # Disputes
        ]
    
    def start(self):
        """Start monitoring loop"""
        self.running = True
        print(f"🔄 Started monitoring for {self.email}")
        
        while self.running:
            try:
                # Check for new high-impact events
                self.check_events()
            except Exception as e:
                print(f"Monitor error: {e}")
            
            time.sleep(60)  # Check every minute
    
    def stop(self):
        self.running = False
        print("⏹️ Stopped monitoring")
    
    def check_events(self):
        """Check for significant events"""
        try:
            import urllib.request
            resp = urllib.request.urlopen("http://localhost:9402/live", timeout=3)
            data = json.loads(resp.read().decode())
            
            events = data.get("events", [])
            
            # Filter for high impact
            high_impact = [e for e in events if e.get("impact") == "high"]
            
            if high_impact and high_impact != self.last_events:
                self.send_alert(high_impact)
                self.last_events = high_impact
                
        except:
            pass
    
    def send_alert(self, events):
        """Send email alert"""
        subject = f"🚨 Agent Hub Alert - {len(events)} High Impact Events"
        
        body = f"""=== THE CALADAN CORPORATION ALERT ===

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

HIGH IMPACT EVENTS:"""

        for e in events:
            body += f"""
📌 {e.get('detail', 'Event')}
⏰ {e.get('time', 'Now')}
📊 Impact: {e.get('impact', 'high').upper()}
💡 Why: {e.get('why', 'Significant change')}
"""

        body += f"""

---
TheCaladan Corporation | Agent Hub
Total alerts sent: {self.sent_emails + 1}"""

        # Print for now - would send via email in production
        print("=" * 50)
        print(f"EMAIL TO: {self.email}")
        print(f"SUBJECT: {subject}")
        print(f"EVENTS: {len(events)}")
        print("=" * 50)
        
        self.sent_emails += 1

# Function to test email
def test_email():
    print("=== EMAIL AUTOMATION TEST ===")
    
    monitor = CivilizationMonitor("aryanhello001@gmail.com")
    
    # Simulate high impact events
    test_events = [
        {"time": "11:45:00", "detail": "TheCaladan released new product", "impact": "high", "why": "Major milestone for your company"},
        {"time": "11:44:00", "detail": "Neural Systems made acquisition", "impact": "high", "why": "Market shift - competitors consolidating"},
    ]
    
    monitor.send_alert(test_events)
    print(f"✅ Test complete. Would send to: {monitor.email}")

if __name__ == '__main__':
    test_email()
