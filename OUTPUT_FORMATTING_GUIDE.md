# Output Formatting Guide

This guide shows how the new human-readable output formatting improves readability compared to raw JSON.

## Before: Raw JSON Output

```json
{
  "goal": "Count unread emails from alice@example.com",
  "steps": 2,
  "complete": false,
  "history": [
    {
      "ok": true,
      "goal": "Query Gmail",
      "result": {
        "count": 7,
        "from": "alice@example.com"
      }
    }
  ]
}
```

**Issues:**
- Hard to scan quickly
- All information is at same visual hierarchy
- Lots of braces and quotes to parse
- No clear status indicators
- Requires mental parsing of structure

## After: Human-Readable Format

```
TASK: Count unread emails from alice@example.com
------------------------------------------------------------
Status: [SUCCESS]

RESULT:
  count: 7
  from: alice@example.com

Steps executed: 2

Suggested tools:
  * send_email
  * read_email

Task ID: #0
```

**Benefits:**
- ✓ Easy to scan and understand at a glance
- ✓ Clear visual hierarchy with sections
- ✓ Obvious status with [SUCCESS] / [FAILED]
- ✓ Indentation shows data relationships
- ✓ No unnecessary punctuation or quotes
- ✓ Section headers guide reading

## Example: Tool Output

### Before (JSON)

```json
{
  "ok": true,
  "result": {
    "emails": [
      {
        "from": "alice@example.com",
        "subject": "Project update",
        "snippet": "Here's the latest status on the project..."
      },
      {
        "from": "bob@example.com",
        "subject": "Meeting tomorrow",
        "snippet": "Let's sync up about the new initiative..."
      }
    ],
    "count": 2,
    "query": "is:unread from:alice OR from:bob"
  },
  "message": "Successfully retrieved 2 emails"
}
```

### After (Human-Readable)

```
Tool: QueryGmail
----------------------------------------
Status: [Success]

Output:
  emails: [
    {
      from: alice@example.com
      subject: Project update
      snippet: Here's the latest status on the project...
    }
    {
      from: bob@example.com
      subject: Meeting tomorrow
      snippet: Let's sync up about the new initiative...
    }
  ]
  count: 2
  query: is:unread from:alice OR from:bob

Message: Successfully retrieved 2 emails
```

## Example: Error Output

### Before (JSON)

```json
{
  "ok": false,
  "goal": "Send email to invalid.address@",
  "error": "Invalid email address: invalid.address@",
  "suggested_tools": ["send_email"],
  "task_id": 5
}
```

### After (Human-Readable)

```
TASK: Send email to invalid.address@
------------------------------------------------------------
Status: [FAILED]

Error: Invalid email address: invalid.address@

Suggested tools:
  * send_email

Task ID: #5
```

## Example: Complex Nested Data

### Before (JSON)

```json
{
  "ok": true,
  "goal": "Get email and calendar summary",
  "result": {
    "email_summary": {
      "total_unread": 12,
      "by_sender": {
        "alice@example.com": 5,
        "bob@example.com": 3,
        "team@example.com": 4
      },
      "recent_subjects": [
        "Project kickoff",
        "Budget review",
        "Weekly status"
      ]
    },
    "calendar_summary": {
      "events_today": 3,
      "busy_hours": "9:00 AM - 12:00 PM, 2:00 PM - 5:00 PM"
    },
    "action_items": [
      "Reply to Alice",
      "Prepare presentation",
      "Schedule meeting"
    ]
  },
  "steps_executed": 3,
  "suggested_tools": ["send_email", "create_event"],
  "task_id": 7
}
```

### After (Human-Readable)

```
TASK: Get email and calendar summary
------------------------------------------------------------
Status: [SUCCESS]

RESULT:
  email_summary: {
    total_unread: 12
    by_sender: {
      alice@example.com: 5
      bob@example.com: 3
      team@example.com: 4
    }
    recent_subjects: [Project kickoff, Budget review, Weekly status]
  }
  calendar_summary: {
    events_today: 3
    busy_hours: 9:00 AM - 12:00 PM, 2:00 PM - 5:00 PM
  }
  action_items: [
    Reply to Alice
    Prepare presentation
    Schedule meeting
  ]

Steps executed: 3

Suggested tools:
  * send_email
  * create_event

Task ID: #7
```

## How to Use

### In Your Code

```python
from utils import print_result, OutputFormatter

# Option 1: Use convenience function
result = {"ok": True, "goal": "Check email", "result": {"count": 5}}
print_result(result)

# Option 2: Use the formatter class
formatted = OutputFormatter.format_agent_result(result)
print(formatted)
```

### Integration Points

1. **main.py** - Updated to use `print_result()` automatically
2. **agents/google_agent.py** - Can use `OutputFormatter` for formatting results
3. **Your Custom Code** - Import and use the formatter in any script

## Comparison Chart

| Aspect | JSON | Human-Readable |
|--------|------|-----------------|
| Readability | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Quick Scanning | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Parsing Required | Yes | No |
| Visual Hierarchy | Low | High |
| Status Clear | No | Yes |
| Data Structure | Complex | Simple |
| Nesting Clarity | Low | High |
| Error Visibility | Low | High |

## Advanced Usage

### Custom Formatting

You can extend the formatter for custom data types:

```python
from utils import OutputFormatter

# Create custom format method
def format_my_result(result):
    """Format custom result type."""
    formatted = OutputFormatter.format_agent_result(result)
    # Add custom formatting here
    return formatted
```

### Programmatic Access

Results remain structured for programmatic access:

```python
result = agent.execute_task("Count emails")

# Formatted display
print_result(result)

# Programmatic access to data
count = result['result']['count']
if result['ok']:
    print(f"Task succeeded with {count} emails")
```

## Best Practices

1. **Always use print_result()** for displaying results
2. **Use OutputFormatter class** when you need the formatted string without printing
3. **Keep raw result dicts** for programmatic access
4. **Chain formatters** for complex nested outputs
5. **Use format_email_list()** for email results
6. **Use format_calendar_events()** for calendar results

## Demo

Run the formatter demo to see all formatting options:

```bash
python examples/formatter_demo.py
```

## File Structure

```
utils/
  __init__.py           # Public API
  formatter.py          # OutputFormatter class
  README.md             # Detailed documentation
```

## What's Changed

### Files Modified
- `main.py` - Uses `print_result()` instead of `json.dumps()`
- `QUICKSTART.md` - Updated documentation with new output examples

### Files Added
- `utils/formatter.py` - Core formatter implementation
- `utils/__init__.py` - Public API exports
- `utils/README.md` - Detailed formatter documentation
- `examples/formatter_demo.py` - Interactive demo
- `OUTPUT_FORMATTING_GUIDE.md` - This guide

### Files Unchanged
- All core agent and tool files remain unchanged
- Results are still structured as dictionaries
- No breaking changes to APIs

## Backward Compatibility

The formatter is completely backward compatible:

1. **Results still return dicts** - No change to data structure
2. **Programmatic access unchanged** - `result['result']['count']` still works
3. **Optional usage** - You can still use `json.dumps()` if needed
4. **No dependencies** - Uses only Python standard library

## Performance

- **Negligible overhead** - Formatting is done at display time
- **No API calls** - All formatting is local
- **Fast string generation** - Uses efficient string building
- **Scales well** - Handles deeply nested structures efficiently

## Environment Support

- **Windows** - Fully supported (uses ASCII characters)
- **Linux/Mac** - Fully supported
- **Terminal** - Works in any terminal that supports text
- **IDE** - Displays correctly in all IDEs
- **Encoding** - Uses ASCII-safe characters for compatibility

## Troubleshooting

### Emojis not displaying?
The new formatter uses ASCII characters instead of emojis for universal compatibility.

### Want to use JSON?
You can still use `json.dumps()` or import and use it:
```python
import json
print(json.dumps(result, indent=2))
```

### Custom formatting needed?
Extend the OutputFormatter class:
```python
class MyFormatter(OutputFormatter):
    @staticmethod
    def format_my_type(data):
        # Custom implementation
        pass
```

## Summary

The new human-readable output formatting:
- ✓ Makes results easier to understand
- ✓ Improves scanning and comprehension
- ✓ Maintains backward compatibility
- ✓ Requires no changes to existing code
- ✓ Supports all data types and nesting levels
- ✓ Works in all environments

For more details, see `utils/README.md` or run `python examples/formatter_demo.py`.
