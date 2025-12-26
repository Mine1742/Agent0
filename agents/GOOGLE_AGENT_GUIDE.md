# Google Agent - User Guide

A portable, autonomous agent for managing your Google services (Gmail, Calendar, etc.).

## Features

- **Gmail Management**: Query, read, and send emails
- **Calendar Management**: View, create, and delete calendar events
- **Smart Tool Selection**: Automatically selects appropriate tools for your task
- **Tool Suggestions**: Recommends additional tools to improve task execution
- **Task History**: Maintains a record of all executed tasks
- **Extensible**: Add custom tools to extend functionality
- **Portable**: Use in any Python project with minimal setup

## Quick Start

### Basic Usage

```python
from agents import GoogleAgent

# Create an agent instance
agent = GoogleAgent(verbose=True)

# Execute a task
result = agent.execute_task("How many unread emails do I have in my inbox?")

# Check the result
print(result)
```

### Example Tasks

```python
# Check today's calendar
result = agent.execute_task("What events do I have today?")

# Count work schedule
result = agent.execute_task("How many days does AJ work this week?")

# Send an email
result = agent.execute_task("Send an email to user@example.com with subject 'Hello'")

# Check Gmail
result = agent.execute_task("How many emails from john@example.com in my inbox?")
```

## API Reference

### GoogleAgent Class

#### Methods

**`__init__(verbose: bool = False)`**
- Initialize the agent
- Args:
  - `verbose`: Print execution logs (default: False)

**`execute_task(goal: str, max_steps: int = 10) -> Dict[str, Any]`**
- Execute a task goal
- Args:
  - `goal`: The task description
  - `max_steps`: Maximum executions (safety limit)
- Returns:
  - Dictionary with `ok`, `goal`, `result`, `steps_executed`, `suggested_tools`, `task_id`

**`list_available_tools() -> Dict[str, str]`**
- Get all available tools with descriptions
- Returns: Dictionary mapping tool names to descriptions

**`add_custom_tool(name: str, tool: Tool) -> None`**
- Add a custom tool to the agent
- Args:
  - `name`: Tool identifier
  - `tool`: Tool instance (must implement Tool interface)

**`get_task_history() -> list`**
- Get history of all executed tasks
- Returns: List of task records

**`export_history(filepath: str) -> None`**
- Export task history to JSON file
- Args:
  - `filepath`: Output file path

**`get_agent_status() -> Dict[str, Any]`**
- Get agent statistics and status
- Returns: Dictionary with metrics

**`reset_history() -> None`**
- Clear task history

### Available Tools

#### Gmail Tools

**`query_gmail`**
- Search and count emails
- Supports filters: sender, folder, unread status
- For counting, automatically uses `count_all=True` for accuracy

**`read_email`**
- Read full email content by ID
- Use after `query_gmail` to get message details

**`send_email`**
- Send emails
- Requires: recipient, subject, body

**`list_gmail_labels`**
- List all Gmail labels and folders

#### Calendar Tools

**`list_calendars`**
- List all available calendars

**`query_events`**
- Search events by date range and text
- Returns event details (title, time, location)

**`create_event`**
- Create calendar events
- Supports timed and all-day events

**`delete_event`**
- Delete events by ID
- Use after `query_events` to get event IDs

## Advanced Usage

### Custom Tools

```python
from tools.base import Tool
from agents import GoogleAgent

class CustomTool(Tool):
    name = "my_custom_tool"
    description = "Does something special"

    def run(self, **kwargs):
        # Your implementation
        return {"ok": True, "result": "success"}

# Add to agent
agent = GoogleAgent()
agent.add_custom_tool("my_custom_tool", CustomTool())

# Use in tasks
result = agent.execute_task("Use my custom tool to do X")
```

### Task Analysis

```python
# Get detailed execution info
result = agent.execute_task("Check my calendar")

print(f"Task ID: {result['task_id']}")
print(f"Steps executed: {result['steps_executed']}")
print(f"Suggested tools: {result['suggested_tools']}")

# Check history
history = agent.get_task_history()
for task in history:
    print(f"{task['goal']}: {task['result']}")
```

### Export and Analyze

```python
# Execute several tasks
agent.execute_task("How many emails from alice@example.com?")
agent.execute_task("What's on my calendar this week?")
agent.execute_task("How many unread messages?")

# Export for analysis
agent.export_history("task_history.json")

# Get statistics
status = agent.get_agent_status()
print(f"Executed {status['total_tasks_executed']} tasks")
print(f"Success rate: {status['successful_tasks']} / {status['total_tasks_executed']}")
```

## Installation & Setup

### Step 1: Copy Files to Your Project

Copy the following files to your project:
```
your_project/
├── agents/
│   ├── __init__.py
│   ├── google_agent.py
│   └── GOOGLE_AGENT_GUIDE.md
├── tools/
│   ├── __init__.py
│   ├── base.py
│   ├── gmail.py
│   ├── calendar.py
│   └── gmail_auth.py
```

### Step 2: Install Dependencies

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Step 3: Set Up Google Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API and Calendar API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download credentials.json
6. Place `credentials.json` in your project root

### Step 4: Use in Your Project

```python
from agents import GoogleAgent

agent = GoogleAgent(verbose=True)
result = agent.execute_task("your task here")
```

First run will prompt you to authorize in your browser.

## Troubleshooting

### "Insufficient authentication scopes" Error
- Delete `token.pickle` file
- Next execution will re-authenticate with proper scopes

### "credentials.json not found"
- Ensure `credentials.json` is in the project root
- Download from Google Cloud Console

### Tasks Not Finding Tools
- Check the goal description uses clear keywords
- Verbose mode shows which tools are selected
- Add custom tools if needed

## Contributing & Extension

### Adding New Tools

1. Create a tool class inheriting from `Tool`
2. Implement `name`, `description`, and `run()` method
3. Add to agent using `add_custom_tool()`

### Suggested Tools for Implementation

The agent can suggest these tools based on tasks:
- Gmail Filters Tool
- Email Templates
- Calendar Reminders
- Email Scheduling
- Calendar Sharing
- Bulk Operations
- Advanced Email Search
- Task Management (Google Tasks integration)

## Security Notes

- `token.pickle` contains your authentication token - keep it secure
- Agent operates only with scopes in `gmail_auth.py`
- No sensitive data is logged in task history
- All tool operations go through official Google APIs

## Examples

### Check Email Volume

```python
agent = GoogleAgent()
result = agent.execute_task("How many emails from caitrinconroy@gmail.com in my inbox?")
print(f"Result: {result['result']['count']} emails")
```

### Schedule Management

```python
result = agent.execute_task("How many days does AJ work this week?")
print(f"Working days: {result['steps_executed']}")
```

### Task Chain

```python
# Agent can chain multiple operations
agent.execute_task("Show me all unread emails in inbox")
# Then use suggestions for filters or automation
```

## Support

For issues or questions:
1. Check verbose output: `GoogleAgent(verbose=True)`
2. Review task history: `agent.get_task_history()`
3. Check available tools: `agent.list_available_tools()`
4. Refer to tool documentation in individual tool files
