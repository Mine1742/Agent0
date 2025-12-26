"""Generic LLM-powered parser for converting natural language to structured parameters.

This module provides a reusable QueryParser class that any agent or tool can use
to intelligently parse natural language queries into structured parameters.

Usage:
    parser = QueryParser(model="claude-haiku-4-5-20251001")

    # Parse for any domain
    calendar_params = parser.parse("What events do I have next week?", domain="calendar")
    gmail_params = parser.parse("Unread emails from alice@example.com", domain="gmail")

    # Custom parsing
    custom_result = parser.parse_custom(query, system_prompt, output_format)
"""
from typing import Any, Dict, Optional
import json
import os
from datetime import datetime

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None


class QueryParser:
    """Generic LLM-powered parser for natural language queries.

    This parser can be configured for any domain (calendar, email, documents, etc.)
    and converts natural language into structured parameters that tools can use.
    """

    def __init__(self, model: Optional[str] = None):
        """Initialize the query parser.

        Args:
            model: Claude model to use (defaults to AGENT_CLAUDE_MODEL env var)
        """
        if not Anthropic:
            raise ImportError("anthropic package required. Install with: pip install anthropic")

        self.client = Anthropic()
        self.model = model or os.getenv("AGENT_CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

    def parse(
        self,
        query: str,
        domain: str,
        custom_format: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Parse a query for a specific domain.

        Args:
            query: Natural language query
            domain: Domain type ("calendar", "gmail", "files", "web", etc.)
            custom_format: Optional custom format specification

        Returns:
            Dictionary of parsed parameters for the domain
        """
        if domain == "calendar":
            return self._parse_calendar(query)
        elif domain == "gmail":
            return self._parse_gmail(query)
        elif domain == "tool":
            return self._determine_tool(query)
        elif custom_format:
            return self.parse_custom(query, custom_format.get("system"), custom_format.get("output"))
        else:
            raise ValueError(f"Unknown domain: {domain}. Use 'calendar', 'gmail', 'tool', or provide custom_format")

    def _parse_calendar(self, query: str) -> Dict[str, Any]:
        """Parse a calendar query and extract date ranges.

        Args:
            query: Natural language query about calendar events

        Returns:
            Dictionary with time_min, time_max, search_text, calendar_id
        """
        current_date = datetime.now()

        prompt = f"""Parse this calendar query and extract the date range.

Query: "{query}"

Current date/time: {current_date.strftime('%Y-%m-%d %H:%M:%S')} ({current_date.strftime('%A, %B %d, %Y')})
Current year: {current_date.year}
Current month: {current_date.month}

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

Rules:
- Weeks: Monday=start, Sunday=end
- If month/date doesn't parse, return current week
- search_text is null unless event name mentioned

JSON only:"""

        return self._call_llm(prompt)

    def _parse_gmail(self, query: str) -> Dict[str, Any]:
        """Parse a Gmail query and extract search filters.

        Args:
            query: Natural language query about emails

        Returns:
            Dictionary with Gmail search query and options
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

JSON only:"""

        return self._call_llm(prompt)

    def _determine_tool(self, query: str) -> Dict[str, Any]:
        """Determine which tool to use for a query.

        Args:
            query: Natural language query

        Returns:
            Dictionary with tool name and confidence
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
- read_file (for reading files)
- write_file (for writing files)
- search_web (for searching the web)

Return only the tool name, nothing else:"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}],
        )

        tool = response.content[0].text.strip().lower()

        return {"tool": tool}

    def parse_custom(
        self,
        query: str,
        system_prompt: str,
        output_format: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Parse using a custom system prompt and expected output format.

        Args:
            query: Natural language query
            system_prompt: Custom system prompt describing what to extract
            output_format: Expected output format (JSON structure description)

        Returns:
            Dictionary of parsed parameters
        """
        prompt = f"""{system_prompt}

Query: "{query}"

{f"Expected output format: {output_format}" if output_format else ""}

Return ONLY valid JSON:"""

        return self._call_llm(prompt)

    def _call_llm(self, prompt: str) -> Dict[str, Any]:
        """Call the LLM and parse JSON response.

        Args:
            prompt: Prompt to send to LLM

        Returns:
            Parsed JSON response as dictionary
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
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
            # Return empty dict if parsing fails
            return {}


# Backward compatibility - keep the old names as aliases
class LLMQueryParser(QueryParser):
    """Backward compatible alias for QueryParser."""

    def parse_calendar_query(self, query: str) -> Dict[str, Any]:
        """Parse a calendar query (backward compatible method)."""
        return self._parse_calendar(query)

    def parse_gmail_query(self, query: str) -> Dict[str, Any]:
        """Parse a Gmail query (backward compatible method)."""
        return self._parse_gmail(query)

    def determine_tool(self, query: str) -> str:
        """Determine tool (backward compatible method)."""
        result = self._determine_tool(query)
        return result.get("tool", "query_gmail")
