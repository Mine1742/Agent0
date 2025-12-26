# Google Agent - Quick Start Guide

Get up and running in 5 minutes.

## Quick Command (After Setup)

Once configured, run queries directly from command line:

```powershell
python gquery "How many unread emails in my inbox?"
python gquery "How many emails from caitrinconroy@gmail.com in inbox?"
python gquery "What events do I have today?"
python gquery "How many days does AJ work this week?"
```

Or in Python:

```python
from agents import GoogleAgent
result = GoogleAgent().execute_task("How many unread emails in my inbox?")
print(result['result'])
```

## 1. Set Up Google Credentials (2 minutes)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable these APIs:
   - Gmail API
   - Google Calendar API
4. Create OAuth 2.0 credentials (select "Desktop application")
5. Download the JSON file and save as `credentials.json` in your project root

## 2. Install Dependencies (1 minute)

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## 3. Try It Out (2 minutes)

```python
from agents import GoogleAgent

# Create agent
agent = GoogleAgent(verbose=True)

# Execute your first task
result = agent.execute_task("How many unread emails do I have?")

# Check the result
print(f"Result: {result['result']['summary']}")
```

First run will open a browser for you to authorize. After that, it uses cached authentication.

## Common Tasks

### Check Email Counts

```python
agent = GoogleAgent()

# Unread in inbox
result = agent.execute_task("How many unread emails in my inbox?")
print(result['result']['count'])

# From specific person
result = agent.execute_task("How many emails from alice@example.com?")
print(result['result']['count'])

# From specific person in inbox only
result = agent.execute_task("How many emails from alice@example.com in my inbox?")
print(result['result']['count'])
```

### Check Calendar

```python
# Today's events
result = agent.execute_task("What events do I have today?")
for event in result['result']['events']:
    print(f"- {event['summary']} at {event['start']}")

# This week
result = agent.execute_task("Show my calendar for this week")

# Search for specific events
result = agent.execute_task("How many days does AJ work this week?")
```

### Send Email

```python
result = agent.execute_task("Send email to john@example.com about the meeting")
```

## Understanding Results

Every task returns structured data that's automatically formatted for readability:

### Output Format

Results are displayed in a clean, human-readable format:

```
TASK: Count emails from alice@example.com
------------------------------------------------------------
Status: [SUCCESS]

RESULT:
  count: 42
  from: alice@example.com

Steps executed: 2

Suggested tools:
  * read_email
  * send_email
```

### Accessing Results Programmatically

```python
result = agent.execute_task("Count emails from alice@example.com")

# Check if task succeeded
if result['ok']:
    count = result['result']['count']  # Get the count

# Get the raw result data
print(result['result'])
```

### Result Dictionary Structure

```python
{
    'ok': True/False,              # Did task execute?
    'goal': 'your task here',      # What you asked for
    'result': {...},               # The actual result
    'steps_executed': 1,           # How many tools were used
    'suggested_tools': [...],      # Tools that might help
    'task_id': 0                   # Task history ID
}
```

## Debugging

### Enable verbose output

```python
agent = GoogleAgent(verbose=True)  # Shows what's happening
result = agent.execute_task("your task")
```

### Check available tools

```python
agent = GoogleAgent()
tools = agent.list_available_tools()
for name, description in tools.items():
    print(f"{name}: {description}")
```

### View task history

```python
history = agent.get_task_history()
for task in history:
    print(f"Goal: {task['goal']}")
    print(f"Success: {task['error'] is None}")
```

## Troubleshooting

### "credentials.json not found"
→ Save your downloaded credentials.json to project root

### "Insufficient authentication scopes"
→ Delete `token.pickle` and run again (will re-authenticate)

### No results returned
→ Run with `verbose=True` to see what tool was selected and what it did

## What's Included

- **GoogleAgent** - The autonomous agent that understands natural language
- **Gmail Tools** - Query, read, send emails
- **Calendar Tools** - List, query, create, delete events
- **Documentation** - Comprehensive guides and API reference

## Next Steps

1. ✓ Set up credentials.json
2. ✓ Install dependencies
3. ✓ Run simple task
4. Read: `agents/GOOGLE_AGENT_GUIDE.md` for detailed docs
5. Explore: `agents/README_PORTABLE.md` for integration patterns
6. Deploy: `agents/DEPLOYMENT_CHECKLIST.md` for other projects

## File Locations

- Agent code: `agents/google_agent.py`
- Tools: `tools/` directory
- Configuration: `credentials.json` (project root)
- Auth cache: `token.pickle` (auto-created, don't commit)

## Common Patterns

### Pattern 1: Single Task

```python
from agents import GoogleAgent

agent = GoogleAgent()
result = agent.execute_task("your task")
print(result['result'])
```

### Pattern 2: Multiple Tasks

```python
agent = GoogleAgent()
results = []
results.append(agent.execute_task("Check emails"))
results.append(agent.execute_task("Check calendar"))
results.append(agent.execute_task("Count from Alice"))

for r in results:
    print(f"{r['goal']}: {r['result']}")
```

### Pattern 3: With Error Handling

```python
agent = GoogleAgent()
try:
    result = agent.execute_task("your task")
    if result['ok']:
        print(f"Success: {result['result']}")
    else:
        print(f"Task failed, suggestions: {result['suggested_tools']}")
except Exception as e:
    print(f"Error: {e}")
```

## Tips

1. **Reuse agent instance** - Create once, use many times
2. **Use natural language** - Say what you want naturally
3. **Enable verbose** - When debugging issues
4. **Export history** - `agent.export_history("history.json")` for analysis
5. **Check suggestions** - Agent recommends helpful tools

## What's New

Fixed issues with the original Gmail setup:
- ✓ Accurate email counting (not inflated estimates)
- ✓ Correct folder filtering (in:inbox actually filters)
- ✓ Natural language parameter extraction
- ✓ Autonomous tool selection
- ✓ Task history and analysis

## Get Help

1. Check verbose output: `GoogleAgent(verbose=True)`
2. Read guides in `agents/` directory:
   - `GOOGLE_AGENT_GUIDE.md` - Detailed user guide
   - `README_PORTABLE.md` - Integration guide
   - `DEPLOYMENT_CHECKLIST.md` - Full deployment steps
3. Check task history for execution details
4. List available tools to confirm what's installed

## You're Ready!

```python
from agents import GoogleAgent

agent = GoogleAgent()
result = agent.execute_task("How many unread emails do I have?")
print(result['result'])
```

That's it! The agent understands natural language and handles the rest.
