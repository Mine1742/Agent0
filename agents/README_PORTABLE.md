# Google Agent - Portable Deployment Guide

A production-ready, autonomous agent for managing Google services (Gmail, Calendar, etc.). Designed to be easily copied to other projects.

## Quick Copy-Paste Setup

### For Existing Projects

1. **Copy these files to your project:**

```
your_project/
├── agents/
│   ├── __init__.py                    (copy from agents/)
│   ├── google_agent.py               (copy from agents/)
│   ├── GOOGLE_AGENT_GUIDE.md         (copy from agents/)
│   └── README_PORTABLE.md            (this file)
├── tools/
│   ├── __init__.py                   (copy from tools/)
│   ├── base.py                       (copy from tools/)
│   ├── gmail.py                      (copy from tools/)
│   ├── calendar.py                   (copy from tools/)
│   └── gmail_auth.py                 (copy from tools/)
└── credentials.json                  (you create this)
```

2. **Install Google API client:**

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

3. **Set up credentials:**
   - Create OAuth 2.0 credentials at https://console.cloud.google.com/
   - Download `credentials.json` to your project root
   - First run will prompt for browser authorization

4. **Start using:**

```python
from agents import GoogleAgent

agent = GoogleAgent(verbose=True)
result = agent.execute_task("Check my inbox")
```

## Core Agent Features

### Smart Task Execution

The agent automatically:
- Parses natural language goals
- Selects appropriate tools
- Extracts parameters from goal descriptions
- Chains multiple operations
- Suggests helpful additional tools

### Natural Language Understanding

```python
# Agent understands these variations:
agent.execute_task("How many unread emails in inbox?")
agent.execute_task("Count unread messages")
agent.execute_task("Show unread email count")

# And these calendar variations:
agent.execute_task("What's on my calendar today?")
agent.execute_task("Show today's events")
agent.execute_task("List calendar appointments")
```

### Tool Management

```python
# List available tools
tools = agent.list_available_tools()

# Add custom tools
from tools.base import Tool
class MyTool(Tool):
    name = "my_tool"
    description = "Does something"
    def run(self, **kwargs):
        return {"ok": True, "result": "done"}

agent.add_custom_tool("my_tool", MyTool())
```

### Execution History

```python
# Get task history
history = agent.get_task_history()

# Export to JSON
agent.export_history("execution_history.json")

# Check statistics
status = agent.get_agent_status()
print(f"Executed: {status['total_tasks_executed']} tasks")
print(f"Success rate: {status['successful_tasks']}/{status['total_tasks_executed']}")
```

## Available Tools Reference

### Gmail Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `query_gmail` | Search emails with filters | Count unread, find by sender |
| `read_email` | Get full email content | Read message details |
| `send_email` | Send emails | Send messages programmatically |
| `list_gmail_labels` | List folders/labels | Show all Gmail folders |

### Calendar Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `list_calendars` | List available calendars | Show all your calendars |
| `query_events` | Search events | Find events by date, title |
| `create_event` | Create calendar events | Add meeting to calendar |
| `delete_event` | Remove events | Delete scheduled event |

## Usage Examples

### Count Emails

```python
agent = GoogleAgent()

# Unread in inbox
result = agent.execute_task("How many unread emails in my inbox?")
print(result['result']['count'])

# From specific sender
result = agent.execute_task("How many emails from alice@example.com in inbox?")
print(result['result']['count'])

# All folders
result = agent.execute_task("Total emails from bob@example.com?")
print(result['result']['count'])
```

### Check Calendar

```python
# Today's events
result = agent.execute_task("What events do I have today?")
for event in result['result']['events']:
    print(f"{event['summary']}: {event['start']}")

# This week's schedule
result = agent.execute_task("Show my calendar for this week")

# Search specific events
result = agent.execute_task("How many days does AJ work this week?")
```

### Send Email

```python
result = agent.execute_task("Send email to user@example.com about meeting")
if result['ok']:
    print("Email sent successfully")
```

### Task Analysis

```python
# Execute multiple tasks
agent.execute_task("How many unread emails?")
agent.execute_task("What's on my calendar?")
agent.execute_task("Show emails from admin@company.com")

# Analyze execution
history = agent.get_task_history()
for task in history:
    print(f"Task: {task['goal']}")
    print(f"Steps: {len(task['steps'])}")
    print(f"Success: {task['error'] is None}")

    # Suggested tools
    if task['suggested_tools']:
        print(f"Suggestions: {task['suggested_tools'][0]}")
```

## Integration Patterns

### Pattern 1: Simple Task Execution

```python
from agents import GoogleAgent

def check_inbox():
    agent = GoogleAgent()
    result = agent.execute_task("How many unread emails?")
    return result['result']['count']

count = check_inbox()
print(f"You have {count} unread emails")
```

### Pattern 2: Chained Tasks

```python
agent = GoogleAgent(verbose=True)

# Execute multiple related tasks
results = []
results.append(agent.execute_task("Check unread email count"))
results.append(agent.execute_task("List calendar events today"))
results.append(agent.execute_task("Count emails from work"))

for r in results:
    print(f"Task: {r['goal']}")
    print(f"Result: {r['result']}")
```

### Pattern 3: Custom Workflows

```python
class EmailWorkflow:
    def __init__(self):
        self.agent = GoogleAgent()

    def daily_briefing(self):
        unread = self.agent.execute_task("Count unread emails")
        calendar = self.agent.execute_task("Show today's events")

        return {
            "unread_count": unread['result']['count'],
            "events": calendar['result']['events']
        }

workflow = EmailWorkflow()
briefing = workflow.daily_briefing()
print(f"Unread: {briefing['unread_count']}")
print(f"Events: {len(briefing['events'])}")
```

### Pattern 4: Error Handling

```python
agent = GoogleAgent(verbose=False)

try:
    result = agent.execute_task("Check inbox")
    if result['ok']:
        print(f"Success: {result['result']}")
    else:
        print(f"Task failed: {result['suggested_tools']}")
except Exception as e:
    print(f"Error: {e}")
    # Fallback behavior
```

## Extending the Agent

### Adding Custom Tools

```python
from tools.base import Tool

class SlackNotifyTool(Tool):
    name = "slack_notify"
    description = "Send notification to Slack"

    def run(self, message: str, channel: str = "#general"):
        # Your implementation
        return {"ok": True, "sent": True}

# Add to agent
agent = GoogleAgent()
agent.add_custom_tool("slack_notify", SlackNotifyTool())

# Use in tasks
agent.execute_task("Send slack notification about emails")
```

### Custom Tool Patterns

```python
from tools.base import Tool
from typing import Dict, Any

class DatabaseTool(Tool):
    name = "store_email_stats"
    description = "Store email statistics in database"

    def run(self, count: int, sender: str) -> Dict[str, Any]:
        # Save to database
        try:
            # db.insert("emails", {"sender": sender, "count": count})
            return {"ok": True, "stored": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

# Chain with agent
agent = GoogleAgent()
agent.add_custom_tool("store_email_stats", DatabaseTool())
```

## Troubleshooting

### Issue: "credentials.json not found"
**Solution:** Place credentials.json in your project root
```bash
# Google Cloud Console → Download OAuth credentials
cp ~/Downloads/credentials.json .
```

### Issue: "Insufficient authentication scopes"
**Solution:** Delete cached token and re-authenticate
```bash
rm token.pickle
python -c "from agents import GoogleAgent; GoogleAgent().execute_task('check inbox')"
# Follow browser prompt to authorize
```

### Issue: "Tool not found"
**Solution:** Check tool name matches exactly
```python
tools = agent.list_available_tools()
print(tools.keys())
```

### Issue: "Unicode encoding error" (Windows)
**Solution:** Already fixed in provided code using [OK]/[FAIL] instead of checkmarks

## Best Practices

1. **Reuse Agent Instance**
   ```python
   # Good - single instance
   agent = GoogleAgent()
   agent.execute_task("task1")
   agent.execute_task("task2")

   # Less efficient - creates new instances
   GoogleAgent().execute_task("task1")
   GoogleAgent().execute_task("task2")
   ```

2. **Enable Verbose for Debugging**
   ```python
   agent = GoogleAgent(verbose=True)  # Shows execution logs
   ```

3. **Handle Task Results Properly**
   ```python
   result = agent.execute_task("count emails")
   if result['ok']:
       # Use result['result'] not result
       count = result['result']['count']
   ```

4. **Export History for Analysis**
   ```python
   agent.export_history("run_history.json")
   # Analyze execution patterns and performance
   ```

## Performance Tips

1. **Use count_all for accurate email counts** - Agent does this automatically
2. **Limit max_steps for safety** - Default is 10
3. **Cache agent instance** - Create once, reuse
4. **Monitor task history** - Check for failures

## Security Considerations

- `token.pickle` contains auth token - **keep secure**
- Don't commit credentials.json to version control
- Agent respects Google API scopes configured in gmail_auth.py
- All operations use official Google APIs (no scraping)

## File Structure

```
agents/
├── __init__.py                  # Package initialization
├── google_agent.py             # Main agent class
├── GOOGLE_AGENT_GUIDE.md       # User guide
└── README_PORTABLE.md          # This file (deployment guide)

tools/
├── __init__.py                 # Package initialization
├── base.py                     # Tool base class
├── gmail.py                    # Gmail tools
├── calendar.py                 # Calendar tools
└── gmail_auth.py              # Google API authentication
```

## Next Steps

1. Copy files to your project
2. Set up credentials.json
3. Install dependencies
4. Run test: `python -c "from agents import GoogleAgent; print(GoogleAgent().list_available_tools())"`
5. Start building with natural language goals

## Support Resources

- Detailed guide: See `agents/GOOGLE_AGENT_GUIDE.md`
- Example usage: See `test_google_agent.py`
- Tool documentation: See individual tool files
- Google API docs: https://developers.google.com/

## License & Attribution

This agent is provided as-is for use in your projects. Feel free to modify and extend as needed.
