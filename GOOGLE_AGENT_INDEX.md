# Google Agent - Documentation Index

Complete reference for the Google Agent system.

## Quick Links

| Need | Document | Time |
|------|----------|------|
| Get started NOW | [QUICKSTART.md](QUICKSTART.md) | 5 min |
| Understand what's built | [GOOGLE_AGENT_SUMMARY.md](GOOGLE_AGENT_SUMMARY.md) | 10 min |
| Learn to use the agent | [agents/GOOGLE_AGENT_GUIDE.md](agents/GOOGLE_AGENT_GUIDE.md) | 15 min |
| Deploy to another project | [agents/README_PORTABLE.md](agents/README_PORTABLE.md) | 10 min |
| Setup checklist | [agents/DEPLOYMENT_CHECKLIST.md](agents/DEPLOYMENT_CHECKLIST.md) | 20 min |

## What Is This?

A **production-ready autonomous agent** for managing Google services (Gmail, Calendar) using **natural language commands**.

```python
from agents import GoogleAgent

agent = GoogleAgent()
result = agent.execute_task("How many unread emails in my inbox?")
# Returns: 8541 emails (accurate count, not estimate)
```

## Core Features

✓ Natural Language Understanding - Say what you want naturally
✓ Accurate Gmail Counting - Fixed API estimate issues
✓ Calendar Management - Query, create, delete events
✓ Autonomous Tool Selection - Automatically picks right tool
✓ Portable - Copy to any project in minutes
✓ Extensible - Add custom tools easily
✓ Well Documented - Comprehensive guides included

## Files Structure

```
google-agent/
├── QUICKSTART.md                    (Start here!)
├── GOOGLE_AGENT_SUMMARY.md         (What we built)
├── GOOGLE_AGENT_INDEX.md           (This file)
│
├── agents/
│   ├── google_agent.py             (Main agent)
│   ├── GOOGLE_AGENT_GUIDE.md       (User guide)
│   ├── README_PORTABLE.md          (Deployment guide)
│   └── DEPLOYMENT_CHECKLIST.md     (Setup steps)
│
├── tools/
│   ├── gmail.py                    (Gmail tools)
│   ├── calendar.py                 (Calendar tools)
│   ├── gmail_auth.py               (OAuth authentication)
│   └── base.py                     (Tool base class)
│
├── test_google_agent.py            (Test script)
└── credentials.json                (You create this)
```

## Common Tasks

### Setup (First Time)

1. Download credentials.json from Google Cloud
2. Place in project root
3. Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
4. First task will prompt for browser auth

See: QUICKSTART.md

### Use in Your Code

```python
from agents import GoogleAgent

agent = GoogleAgent()
result = agent.execute_task("Check my unread emails")
```

See: agents/GOOGLE_AGENT_GUIDE.md

### Deploy to Another Project

1. Copy agents/ and tools/ directories
2. Copy your credentials.json
3. Install dependencies
4. Done!

See: agents/README_PORTABLE.md

## Example Usage

### Email Tasks

```python
agent = GoogleAgent()

# Count emails
result = agent.execute_task("How many unread emails in my inbox?")

# Count from specific sender
result = agent.execute_task("How many emails from alice@example.com?")

# Send email
result = agent.execute_task("Send email to john@example.com")
```

### Calendar Tasks

```python
# Today's events
result = agent.execute_task("What events do I have today?")

# This week
result = agent.execute_task("Show my calendar for this week")

# Count work days
result = agent.execute_task("How many days does AJ work this week?")
```

## Documentation by Role

### For Users
- QUICKSTART.md - Get started
- agents/GOOGLE_AGENT_GUIDE.md - Detailed usage

### For Developers
- GOOGLE_AGENT_SUMMARY.md - Technical overview
- agents/README_PORTABLE.md - Integration patterns
- Source code: agents/google_agent.py, tools/*.py

### For DevOps
- agents/DEPLOYMENT_CHECKLIST.md - Setup checklist
- agents/README_PORTABLE.md - Deployment guide

### For Architects
- GOOGLE_AGENT_SUMMARY.md - System design
- agents/google_agent.py - Architecture

## Available Tools

### Gmail Tools (4)

1. QueryGmail - Search emails with accurate counting
2. ReadEmail - Get full email content
3. SendEmail - Send emails
4. ListGmailLabels - List folders/labels

### Calendar Tools (4)

1. ListCalendars - Show available calendars
2. QueryEvents - Search events by date/text
3. CreateEvent - Add calendar event
4. DeleteEvent - Remove calendar event

## Quick Reference

### Basic Import
```python
from agents import GoogleAgent
```

### Create Agent
```python
agent = GoogleAgent(verbose=True)
```

### Execute Task
```python
result = agent.execute_task("your task here")
```

### Check Result
```python
if result['ok']:
    data = result['result']
```

### List Tools
```python
tools = agent.list_available_tools()
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| credentials.json not found | Place in project root |
| Insufficient authentication | Delete token.pickle |
| Agent not selecting tool | Check verbose output |
| Want custom tool | Use add_custom_tool() |

## Next Steps

1. New User? → Read QUICKSTART.md
2. Want Details? → Read agents/GOOGLE_AGENT_GUIDE.md
3. Deploying? → Read agents/DEPLOYMENT_CHECKLIST.md
4. Integrating? → Read agents/README_PORTABLE.md
5. Curious? → Read GOOGLE_AGENT_SUMMARY.md

## System Requirements

- Python 3.8+
- Google account
- pip
- Internet connection

## Status

Production Ready - Tested with real Gmail/Calendar data
