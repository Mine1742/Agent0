# QueryParser Integration Guide

The `QueryParser` (and its backward-compatible alias `LLMQueryParser`) provides LLM-powered natural language query parsing for any agent or tool.

## Overview

Instead of hardcoding query patterns with regex, you can now leverage Claude to intelligently parse any natural language query into structured parameters.

### Key Benefits

- ✅ **No Hardcoding** - Add new query types without code changes
- ✅ **Domain Agnostic** - Works with calendar, email, files, web, or custom domains
- ✅ **Extensible** - Create custom parsers for any domain with `parse_custom()`
- ✅ **Fallback Capable** - All agents work even if LLM parsing fails
- ✅ **Backward Compatible** - Old code continues to work

## Quick Start

### For GoogleAgent (Already Integrated)

The QueryParser is already integrated into GoogleAgent. Just use it normally:

```python
from agents import GoogleAgent

agent = GoogleAgent()
result = agent.execute_task("What events do I have next Tuesday?")
```

The agent will automatically:
1. Use the LLM to determine the correct tool
2. Use the LLM to extract date ranges
3. Fall back to regex if LLM fails
4. Execute the query

### For New Agents

#### Option 1: Integrate Into Your Agent

```python
from agents.llm_parser import QueryParser

class MyAgent:
    def __init__(self):
        self.parser = QueryParser()

    def execute_task(self, query):
        # Determine the tool to use
        tool_result = self.parser.parse(query, domain="tool")
        tool_name = tool_result.get("tool")

        # Get parameters for the tool
        if tool_name.startswith("query_"):
            params = self._get_params_for_tool(query, tool_name)

        # Execute...
```

#### Option 2: Use Directly in Tools

```python
from agents.llm_parser import QueryParser

class QueryEmailsTool:
    def run(self, query):
        parser = QueryParser()

        # Parse the natural language query
        params = parser.parse(query, domain="gmail")
        # params = {"query": "in:inbox is:unread", "count_all": True}

        # Use params to execute the tool
        return self._search_emails(**params)
```

## Supported Domains

### Calendar Domain

Parse queries about calendar events and dates.

```python
parser = QueryParser()

# Returns: {"time_min": "2025-12-29", "time_max": "2026-01-04", "search_text": null, "calendar_id": "primary"}
params = parser.parse("What events do I have next week?", domain="calendar")

# Returns: {"time_min": "2026-01-19", "time_max": "2026-01-25", ...}
params = parser.parse("Show me the third week of January", domain="calendar")

# Returns: {"time_min": "2025-12-27", "time_max": "2025-12-27", ...}
params = parser.parse("Tomorrow's schedule", domain="calendar")
```

### Gmail Domain

Parse queries about emails and messages.

```python
parser = QueryParser()

# Returns: {"query": "in:inbox is:unread", "count_all": True}
params = parser.parse("How many unread emails?", domain="gmail")

# Returns: {"query": "from:alice@example.com in:inbox", "count_all": False}
params = parser.parse("Show me emails from alice@example.com", domain="gmail")

# Returns: {"query": "subject:meeting", "count_all": False}
params = parser.parse("Find emails about the meeting", domain="gmail")
```

### Tool Domain

Determine which tool to use.

```python
parser = QueryParser()

# Returns: {"tool": "query_events"}
result = parser.parse("What's on my calendar?", domain="tool")

# Returns: {"tool": "send_email"}
result = parser.parse("Send an email to john@example.com", domain="tool")

# Returns: {"tool": "read_file"}
result = parser.parse("Show me the contents of config.json", domain="tool")
```

## Custom Domains

Create a parser for any domain using `parse_custom()`:

```python
parser = QueryParser()

# Example: Parse a database query
db_prompt = """
Extract SQL query parameters from this natural language request:
- Extract table name, conditions, and filters
- Determine if it's a SELECT, INSERT, UPDATE, or DELETE
Return JSON with: {"operation": "...", "table": "...", "conditions": {...}}
"""

output_format = """
{
    "operation": "SELECT|INSERT|UPDATE|DELETE",
    "table": "table_name",
    "conditions": {"column": "value"}
}
"""

params = parser.parse_custom(
    "Get all users from the database where status is active",
    system_prompt=db_prompt,
    output_format=output_format
)
# Returns: {"operation": "SELECT", "table": "users", "conditions": {"status": "active"}}
```

## Integration Patterns

### Pattern 1: Agent-Level Integration (GoogleAgent Style)

Integrate the parser at the agent level to handle all queries:

```python
from agents.llm_parser import QueryParser

class MyAgent:
    def __init__(self):
        try:
            self.parser = QueryParser()
        except ImportError:
            self.parser = None  # Fallback to regex

    def _determine_tools(self, goal):
        if self.parser:
            try:
                result = self.parser.parse(goal, domain="tool")
                return [result.get("tool", "default_tool")]
            except Exception:
                pass  # Fall back to regex

        # Regex fallback
        return self._determine_tools_regex(goal)

    def _extract_parameters(self, goal, tool_name):
        if self.parser and tool_name in ["query_events", "query_gmail"]:
            try:
                domain = "calendar" if "event" in tool_name else "gmail"
                return self.parser.parse(goal, domain=domain)
            except Exception:
                pass  # Fall back to regex

        # Regex fallback
        return self._extract_parameters_regex(goal, tool_name)
```

### Pattern 2: Tool-Level Integration

Integrate the parser directly into individual tools:

```python
from tools.base import Tool
from agents.llm_parser import QueryParser

class QueryEventsWithParser(Tool):
    def __init__(self):
        self.name = "query_events"
        self.parser = QueryParser()

    def run(self, query: str):
        # Use parser to extract parameters
        params = self.parser.parse(query, domain="calendar")

        # Execute with parsed parameters
        return self._query_calendar(
            time_min=params.get("time_min"),
            time_max=params.get("time_max"),
            search_text=params.get("search_text")
        )
```

### Pattern 3: Middleware Integration

Use the parser as middleware between user input and tools:

```python
from agents.llm_parser import QueryParser

class QueryParserMiddleware:
    def __init__(self, tools):
        self.parser = QueryParser()
        self.tools = tools

    def process_query(self, query):
        # Step 1: Determine tool
        tool_result = self.parser.parse(query, domain="tool")
        tool_name = tool_result.get("tool")

        # Step 2: Get tool-specific parameters
        tool = self.tools.get(tool_name)
        if tool and hasattr(tool, 'expected_params'):
            params = self.parser.parse_custom(
                query,
                system_prompt=tool.get_system_prompt(),
                output_format=tool.get_output_format()
            )
        else:
            # Use domain-specific parsing
            domain = self._get_domain(tool_name)
            params = self.parser.parse(query, domain=domain)

        # Step 3: Execute tool
        return tool.run(**params)
```

## Error Handling

The parser gracefully handles errors:

```python
parser = QueryParser()

try:
    params = parser.parse("complex query", domain="calendar")
except ImportError:
    print("LLM not available, falling back to regex")

# Or just check if parser is available
if parser:
    try:
        params = parser.parse(query, domain="calendar")
    except Exception as e:
        print(f"Parsing failed: {e}, using defaults")
        params = {"time_min": today, "time_max": today}
```

## Configuration

### Using Custom Models

```python
# Use environment variable
import os
os.environ["AGENT_CLAUDE_MODEL"] = "claude-opus-4-20250514"

parser = QueryParser()  # Uses AGENT_CLAUDE_MODEL

# Or specify directly
parser = QueryParser(model="claude-opus-4-20250514")
```

### Cost Optimization

For high-volume use, consider:

1. **Caching Results**: Cache frequently asked queries
2. **Batching**: Parse multiple queries in one call
3. **Fallback Strategy**: Use regex for simple queries, LLM for complex ones

```python
class OptimizedParser:
    def __init__(self):
        self.parser = QueryParser()
        self.cache = {}

    def parse(self, query, domain):
        # Check cache
        cache_key = f"{query}:{domain}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Try regex first for common patterns
        result = self._try_regex(query, domain)
        if result:
            return result

        # Fall back to LLM for complex queries
        result = self.parser.parse(query, domain=domain)
        self.cache[cache_key] = result
        return result
```

## Best Practices

1. **Always have a fallback**: Query parsing should never break your application
2. **Use specific domains**: More specific domains = better results
3. **Test with examples**: Verify the parser handles your expected queries
4. **Monitor errors**: Log when the parser fails to identify patterns
5. **Cache results**: Reuse parsed parameters for identical queries

## Backward Compatibility

Old code using `LLMQueryParser` continues to work:

```python
# Old code - still works
from agents.query_parser import LLMQueryParser

parser = LLMQueryParser()
calendar_params = parser.parse_calendar_query("What events do I have?")
gmail_params = parser.parse_gmail_query("Unread emails")
tool = parser.determine_tool("Send an email")

# New code - also works with same import
from agents.llm_parser import LLMQueryParser

parser = LLMQueryParser()
# Same methods available...
```

## Examples

### Example 1: Calendar-Only Agent

```python
from agents.llm_parser import QueryParser

class CalendarAgent:
    def __init__(self):
        self.parser = QueryParser()

    def query_calendar(self, question):
        params = self.parser.parse(question, domain="calendar")
        return self._fetch_events(
            start=params["time_min"],
            end=params["time_max"]
        )

agent = CalendarAgent()
events = agent.query_calendar("What's on my calendar next week?")
```

### Example 2: Email Search Tool

```python
from agents.llm_parser import QueryParser

class EmailSearch:
    def search(self, query):
        parser = QueryParser()
        params = parser.parse(query, domain="gmail")

        # Use Gmail API with parsed parameters
        return gmail_api.search(
            q=params["query"],
            maxResults=100 if params["count_all"] else 10
        )

tool = EmailSearch()
results = tool.search("Show me unread emails from my boss")
```

### Example 3: Multi-Domain Agent

```python
from agents.llm_parser import QueryParser

class UniversalAgent:
    def execute(self, query):
        parser = QueryParser()

        # Determine domain
        tool_result = parser.parse(query, domain="tool")
        tool_name = tool_result.get("tool", "query_gmail")

        # Parse for appropriate domain
        if "event" in tool_name:
            params = parser.parse(query, domain="calendar")
        elif "email" in tool_name or "gmail" in tool_name:
            params = parser.parse(query, domain="gmail")
        else:
            params = {}

        # Execute
        return self._execute_tool(tool_name, params)
```

## Troubleshooting

### Parser returns empty parameters

**Problem**: Parser returns `{}` or default values

**Solution**:
- Check that ANTHROPIC_API_KEY is set
- Verify query is clear and specific
- Check LLM response format in logs

### Integration not working

**Problem**: Agent not using parser

**Solution**:
1. Verify import: `from agents.llm_parser import QueryParser`
2. Check fallback logic is enabled
3. Test parser directly:
   ```python
   parser = QueryParser()
   result = parser.parse("test query", domain="calendar")
   print(result)
   ```

### Performance issues

**Problem**: Parser calls are slow

**Solution**:
- Implement caching (see Example above)
- Use fallback for common patterns
- Consider using a smaller model for high-volume parsing

## Support

For issues or questions:
1. Check `agents/llm_parser.py` source code
2. Review examples in this guide
3. Test with verbose logging enabled
4. Check ANTHROPIC_API_KEY is valid
