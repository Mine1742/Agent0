# Output Formatter

The `OutputFormatter` module provides human-readable formatting for agent and tool outputs, converting JSON responses into clean, easy-to-read text.

## Features

- **Agent Results**: Format complete agent execution results with status, results, steps, and suggestions
- **Tool Output**: Format individual tool execution outputs
- **Tools List**: Format available tools with descriptions
- **Task History**: Format task execution history
- **Email List**: Format email results with from, subject, and preview
- **Calendar Events**: Format calendar event results
- **Nested Data**: Intelligent formatting of complex nested data structures

## Usage

### Quick Start

```python
from utils import print_result, OutputFormatter

# Format and print an agent result
result = {
    "ok": True,
    "goal": "Count unread emails",
    "result": {"count": 7},
    "steps_executed": 1,
}
print_result(result)
```

### Formatting Agent Results

```python
from utils import OutputFormatter

result = {
    "ok": True,
    "goal": "Get email and calendar summary",
    "result": {
        "emails": {"unread": 5},
        "calendar": {"events_today": 3},
    },
    "steps_executed": 2,
    "suggested_tools": ["send_email", "create_event"],
}

formatted = OutputFormatter.format_agent_result(result)
print(formatted)
```

Output:
```
TASK: Get email and calendar summary
------------------------------------------------------------
Status: [SUCCESS]

RESULT:
  emails: {
    unread: 5
  }
  calendar: {
    events_today: 3
  }

Steps executed: 2

Suggested tools:
  * send_email
  * create_event
```

### Formatting Tool Output

```python
from utils import OutputFormatter

output = {
    "ok": True,
    "result": {
        "emails": 5,
        "from": "alice@example.com"
    },
    "message": "Query executed successfully"
}

formatted = OutputFormatter.format_tool_output("QueryGmail", output)
print(formatted)
```

### Formatting Tools List

```python
from utils import print_tools_list

tools = {
    "query_gmail": "Query Gmail with filters",
    "send_email": "Send an email",
    "query_events": "Query calendar events",
}

print_tools_list(tools)
```

Output:
```
Available Tools:
----------------------------------------
* query_events
  Query calendar events
* query_gmail
  Query Gmail with filters
* send_email
  Send an email
```

### Formatting Task History

```python
from utils import OutputFormatter

history = [
    {"ok": True, "goal": "Check emails", "steps_executed": 1},
    {"ok": False, "goal": "Send email", "error": "Invalid address"},
]

formatted = OutputFormatter.format_task_history(history)
print(formatted)
```

### Formatting Email Lists

```python
from utils import OutputFormatter

emails = [
    {
        "from": "alice@example.com",
        "subject": "Project update",
        "snippet": "Here's the status on the project...",
    },
    {
        "from": "bob@example.com",
        "subject": "Meeting tomorrow",
        "snippet": "Let's sync about the initiative...",
    }
]

formatted = OutputFormatter.format_email_list(emails)
print(formatted)
```

### Formatting Calendar Events

```python
from utils import OutputFormatter

events = [
    {
        "summary": "Team standup",
        "start": "2024-01-15 10:00 AM",
        "end": "2024-01-15 10:30 AM",
    },
    {
        "summary": "Project review",
        "start": "2024-01-15 2:00 PM",
        "end": "2024-01-15 3:30 PM",
    }
]

formatted = OutputFormatter.format_calendar_events(events)
print(formatted)
```

## Output Examples

### Successful Result

```
TASK: Count unread emails
------------------------------------------------------------
Status: [SUCCESS]

RESULT:
  count: 7

Steps executed: 1

Task ID: #0
```

### Failed Result

```
TASK: Send email to invalid.user@
------------------------------------------------------------
Status: [FAILED]

Error: Invalid email address: invalid.user@

Task ID: #1
```

### Complex Nested Result

```
TASK: Get comprehensive summary
------------------------------------------------------------
Status: [SUCCESS]

RESULT:
  email_summary: {
    total_unread: 12
    by_sender: {
      alice@example.com: 5
      bob@example.com: 7
    }
  }
  calendar_summary: {
    events_today: 3
    busy_hours: 9:00 AM - 12:00 PM, 2:00 PM - 5:00 PM
  }

Steps executed: 4

Suggested tools:
  * send_email
  * create_event
```

## Functions

### `print_result(result: Dict[str, Any]) -> None`

Print an agent result in human-readable format to stdout.

**Parameters:**
- `result`: Dictionary containing agent execution result

**Example:**
```python
print_result({"ok": True, "goal": "Check email", "result": {"count": 5}})
```

### `print_tool_output(tool_name: str, output: Dict[str, Any]) -> None`

Print a tool output in human-readable format to stdout.

**Parameters:**
- `tool_name`: Name of the tool (e.g., "QueryGmail")
- `output`: Tool output dictionary

**Example:**
```python
print_tool_output("QueryGmail", {"ok": True, "result": {"count": 5}})
```

### `print_tools_list(tools: Dict[str, str]) -> None`

Print available tools in human-readable format to stdout.

**Parameters:**
- `tools`: Dictionary mapping tool names to descriptions

**Example:**
```python
tools = {"query_gmail": "Query Gmail", "send_email": "Send email"}
print_tools_list(tools)
```

## Class Methods

### `OutputFormatter.format_agent_result(result: Dict[str, Any]) -> str`

Format agent execution results. Returns formatted string.

### `OutputFormatter.format_tool_output(tool_name: str, output: Dict[str, Any]) -> str`

Format individual tool execution output. Returns formatted string.

### `OutputFormatter.format_tools_list(tools: Dict[str, str]) -> str`

Format available tools list. Returns formatted string.

### `OutputFormatter.format_task_history(history: List[Dict[str, Any]]) -> str`

Format task execution history. Returns formatted string.

### `OutputFormatter.format_email_list(emails: List[Dict[str, Any]]) -> str`

Format list of emails. Returns formatted string.

### `OutputFormatter.format_calendar_events(events: List[Dict[str, Any]]) -> str`

Format list of calendar events. Returns formatted string.

## Demo

To see the formatter in action, run:

```bash
python examples/formatter_demo.py
```

This demonstrates:
- Agent result formatting
- Tool output formatting
- Tools list formatting
- Failed result formatting
- Complex nested result formatting

## Design

The formatter uses several principles for readability:

1. **Clear Headers**: Each section has a clear label (e.g., "TASK:", "RESULT:", "SUGGESTED TOOLS:")
2. **Consistent Layout**: All outputs follow the same structure for easy scanning
3. **Intelligent Indentation**: Nested data is indented to show hierarchy
4. **Smart Quoting**: Strings are only quoted when necessary (long or multiline)
5. **Status Indicators**: Results use [SUCCESS] or [FAILED] for clarity
6. **ASCII-Safe**: Uses only ASCII characters (no emojis) for universal compatibility

## Integration

The formatter is automatically integrated into `main.py`. To use it in your own code:

```python
from utils import print_result, OutputFormatter

# Using convenience functions
print_result(result)

# Using the class directly
formatted = OutputFormatter.format_agent_result(result)
print(formatted)
```
