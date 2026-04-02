# Agent Notification System

Manages alerts, notifications, and announcements for agents.

## Features

- **Direct notifications**: Send to specific agents
- **Broadcast**: Notify all agents at once
- **Priority levels**: low, normal, high, urgent
- **Categories**: general, alert, system, task, collaboration
- **Inbox management**: Get, mark read, archive
- **Preferences**: Configure per-agent channel preferences

## Usage

```bash
# Send notification
python3 notifications.py send <recipient> <title> <message> [priority] [category]

# Broadcast to all
python3 notifications.py broadcast <title> <message> [priority]

# Get inbox
python3 notifications.py inbox <agent_id> [unread]

# Mark as read
python3 notifications.py read <notification_id>

# Archive
python3 notifications.py archive <notification_id>

# Stats
python3 notifications.py stats [agent_id]
```

## Priority Levels

- **low**: Background info, non-urgent
- **normal**: Standard notifications
- **high**: Important but not critical
- **urgent**: Immediate attention required

## Categories

- **general**: General information
- **alert**: System alerts
- **system**: Platform/system messages
- **task**: Task-related notifications
- **collaboration**: Collaboration requests