"""LLM-powered query parser for extracting search criteria from natural language.

This module uses Claude to intelligently parse user queries and extract
structured search parameters for Gmail and Calendar operations.
"""
from typing import Any, Dict, Optional
import json
import os
from datetime import datetime

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None


class LLMQueryParser:
    """Uses Claude to parse natural language queries into structured parameters."""

    def __init__(self, model: Optional[str] = None):
        """Initialize the query parser.

        Args:
            model: Claude model to use (defaults to AGENT_CLAUDE_MODEL env var)
        """
        if not Anthropic:
            raise ImportError("anthropic package required. Install with: pip install anthropic")

        self.client = Anthropic()
        self.model = model or os.getenv("AGENT_CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

    def parse_calendar_query(self, query: str) -> Dict[str, Any]:
        """Parse a calendar query and extract date ranges and search criteria.

        Args:
            query: Natural language query about calendar events

        Returns:
            Dictionary with parsed parameters:
            {
                "time_min": "YYYY-MM-DD",
                "time_max": "YYYY-MM-DD",
                "search_text": optional search term,
                "calendar_id": "primary" or specific ID
            }
        """
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month

        prompt = f"""Parse this calendar query and extract the date range.

Query: "{query}"

Current date/time: {current_date.strftime('%Y-%m-%d %H:%M:%S')} ({current_date.strftime('%A, %B %d, %Y')})
Current year: {year}
Current month: {month}

Return ONLY valid JSON:
{{
    "time_min": "YYYY-MM-DD start date",
    "time_max": "YYYY-MM-DD end date (inclusive)",
    "search_text": "optional event name/keyword to search for, or null",
    "calendar_id": "primary"
}}

IMPORTANT: Parse month names CAREFULLY:
- If query mentions a month name (January, February, etc), identify it first
- If that month has not started yet this year, use this year
- If that month has passed, use next year
- "third week in january" means: find January, then the 3rd Monday-Sunday range

Calculation examples:
- "today": return today's date as both time_min and time_max
- "next week": return next Monday-Sunday range
- "third week in january":
  - If today is Dec 2024, January is next year (2025)
  - Find first Monday of January 2025
  - Third Monday = first Monday + 14 days
  - Range: 3rd Monday through 3rd Sunday

Rules:
- Weeks: Monday=start, Sunday=end
- Months: January=1, February=2, ..., December=12
- If month/date doesn't parse, return current week
- search_text is null unless event name mentioned

JSON only:"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            text = response.content[0].text
            # Remove markdown code blocks if present
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            text = text.strip()
            result = json.loads(text)
            return result
        except (json.JSONDecodeError, IndexError, AttributeError) as e:
            # Log error for debugging
            import sys
            print(f"Warning: Failed to parse LLM response: {e}", file=sys.stderr)
            # Return safe default if parsing fails
            return {
                "time_min": datetime.now().strftime('%Y-%m-%d'),
                "time_max": (datetime.now()).strftime('%Y-%m-%d'),
                "search_text": None,
                "calendar_id": "primary",
            }

    def parse_gmail_query(self, query: str) -> Dict[str, Any]:
        """Parse a Gmail query and extract search filters.

        Args:
            query: Natural language query about emails

        Returns:
            Dictionary with parsed parameters:
            {
                "query": Gmail search filter string,
                "count_all": whether to count all matches
            }
        """
        prompt = f"""Parse this Gmail query and extract the search filter.

Query: "{query}"

Return ONLY valid JSON:
{{
    "query": "Gmail search filter string (e.g., 'in:inbox is:unread from:user@example.com')",
    "count_all": boolean whether this is asking for a count
}}

Rules:
- Use Gmail search syntax: from:, to:, subject:, in:, is:unread, is:read, etc.
- If asking "how many" or "count", set count_all to true
- Combine filters with spaces
- For inbox without specification, add "in:inbox"
- For unread, add "is:unread"
- For specific sender, use "from:email@example.com"
- For specific recipient, use "to:email@example.com"
- For subject matches, use "subject:keyword"

JSON only, no explanation:"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            text = response.content[0].text
            # Remove markdown code blocks if present
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            text = text.strip()
            result = json.loads(text)
            return result
        except (json.JSONDecodeError, IndexError, AttributeError) as e:
            # Return safe default if parsing fails
            import sys
            print(f"Warning: Failed to parse Gmail params: {e}", file=sys.stderr)
            return {"query": "", "count_all": False}

    def determine_tool(self, query: str) -> str:
        """Determine which tool to use for a query.

        Args:
            query: Natural language query

        Returns:
            Tool name: "query_gmail", "send_email", "query_events", etc.
        """
        prompt = f"""Determine which tool is best for this query.

Query: "{query}"

Return ONLY the tool name, nothing else. Choose from:
- query_gmail (for searching emails, counting emails, reading emails)
- send_email (for sending emails)
- query_events (for searching calendar events, checking schedules)
- create_event (for creating calendar events)
- delete_event (for deleting/canceling events)
- list_gmail_labels (for listing email labels/folders)
- list_calendars (for listing all calendars)

Return only the tool name, nothing else:"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}],
        )

        tool = response.content[0].text.strip().lower()

        # Validate against known tools
        valid_tools = [
            "query_gmail",
            "send_email",
            "query_events",
            "create_event",
            "delete_event",
            "list_gmail_labels",
            "list_calendars",
        ]

        return tool if tool in valid_tools else "query_gmail"
