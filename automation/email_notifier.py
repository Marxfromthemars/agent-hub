"""
AUTOMATED EMAIL SYSTEM
"""
import json
from datetime import datetime

class EmailNotifier:
    def __init__(self, to_email):
        self.to_email = to_email
        self.sent_count = 0
    
    def send_update(self, events):
        subject = f"🤖 Agent Hub Update - {len(events)} events"
        body = f"=== THE CALADAN CORPORATION UPDATE ===\n\n"
        body += f"Time: {datetime.now().strftime('%H:%M:%S')}\n\n"
        
        for e in events:
            body += f"📌 {e.get('detail')}\n"
            body += f"   Why: {e.get('why')}\n\n"
        
        print(f"Would send to {self.to_email}: {subject}")
        print(f"Content: {len(body)} chars")
        self.sent_count += 1
        return {"sent": True, "count": self.sent_count}

# Test
notifier = EmailNotifier("aryanhello001@gmail.com")
result = notifier.send_update([
    {"detail": "Test event", "why": "Testing email system"}
])
print(f"✅ Email automation tested: {result}")
