"""Human-readable output formatting for agents and tools.

Converts JSON responses and tool outputs into formatted, easy-to-read text.
"""
from typing import Any, Dict, List
from datetime import datetime


class OutputFormatter:
    """Formats agent and tool outputs for human readability."""

    @staticmethod
    def format_agent_result(result: Dict[str, Any]) -> str:
        """Format agent execution results.

        Args:
            result: Dictionary containing agent execution result

        Returns:
            Formatted human-readable string
        """
        lines = []

        # Header
        if result.get('goal'):
            lines.append(f"TASK: {result['goal']}")
            lines.append("-" * 60)

        # Status
        status = "[SUCCESS]" if result.get('ok') else "[FAILED]"
        lines.append(f"Status: {status}")

        # Main result - use specialized formatters when appropriate
        if result.get('result'):
            lines.append("\nRESULT:")
            result_data = result['result']

            # Detect if this is a calendar events result
            if isinstance(result_data, dict) and 'events' in result_data and isinstance(result_data.get('events'), list):
                # Format as calendar events
                events = result_data['events']
                if events:
                    lines.append(OutputFormatter.format_calendar_events(events))
                    # Add summary if available
                    if result_data.get('summary'):
                        lines.append(f"\n{result_data['summary']}")
                else:
                    lines.append("No events found")
            # Detect if this is an email list result
            elif isinstance(result_data, dict) and 'emails' in result_data and isinstance(result_data.get('emails'), list):
                # Format as email list
                emails = result_data['emails']
                if emails:
                    lines.append(OutputFormatter.format_email_list(emails))
                    # Add count if available
                    if result_data.get('count'):
                        lines.append(f"\nTotal: {result_data['count']}")
                else:
                    lines.append("No emails found")
            else:
                # Default formatting
                lines.append(OutputFormatter._format_value(result_data, indent=2))

        # Steps executed
        if result.get('steps_executed'):
            lines.append(f"\nSteps executed: {result['steps_executed']}")

        # Suggested tools
        if result.get('suggested_tools'):
            lines.append("\nSuggested tools:")
            for tool in result['suggested_tools']:
                lines.append(f"  * {tool}")

        # Error info
        if result.get('error'):
            lines.append(f"\nError: {result['error']}")

        # Task ID
        if result.get('task_id') is not None:
            lines.append(f"\nTask ID: #{result['task_id']}")

        return "\n".join(lines)

    @staticmethod
    def format_tool_output(tool_name: str, output: Dict[str, Any]) -> str:
        """Format individual tool execution output.

        Args:
            tool_name: Name of the tool
            output: Tool output dictionary

        Returns:
            Formatted human-readable string
        """
        lines = []

        lines.append(f"Tool: {tool_name}")
        lines.append("-" * 40)

        status = "[Success]" if output.get('ok') else "[Failed]"
        lines.append(f"Status: {status}")

        if output.get('result'):
            lines.append("\nOutput:")
            lines.append(OutputFormatter._format_value(output['result'], indent=2))

        if output.get('error'):
            lines.append(f"\nError: {output['error']}")

        if output.get('message'):
            lines.append(f"\nMessage: {output['message']}")

        return "\n".join(lines)

    @staticmethod
    def format_tools_list(tools: Dict[str, str]) -> str:
        """Format available tools list.

        Args:
            tools: Dictionary of tool names and descriptions

        Returns:
            Formatted human-readable string
        """
        lines = ["Available Tools:", "-" * 40]

        for name, description in sorted(tools.items()):
            lines.append(f"* {name}")
            if description:
                lines.append(f"  {description}")

        return "\n".join(lines)

    @staticmethod
    def format_task_history(history: List[Dict[str, Any]]) -> str:
        """Format task history.

        Args:
            history: List of task records

        Returns:
            Formatted human-readable string
        """
        lines = ["Task History:", "-" * 40]

        for i, task in enumerate(history, 1):
            status = "[OK]" if task.get('ok') else "[FAILED]"
            lines.append(f"{i}. {status} {task.get('goal', 'Unknown task')}")

            if task.get('steps_executed'):
                lines.append(f"   Steps: {task['steps_executed']}")

            if task.get('error'):
                lines.append(f"   Error: {task['error']}")

        return "\n".join(lines)

    @staticmethod
    def format_email_list(emails: List[Dict[str, Any]]) -> str:
        """Format list of emails.

        Args:
            emails: List of email records

        Returns:
            Formatted human-readable string
        """
        lines = ["Emails:", "-" * 60]

        for email in emails:
            lines.append(f"From: {email.get('from', 'Unknown')}")
            lines.append(f"Subject: {email.get('subject', '(no subject)')}")

            if email.get('snippet'):
                snippet = email['snippet'][:100] + "..." if len(email['snippet']) > 100 else email['snippet']
                lines.append(f"Preview: {snippet}")

            lines.append("")  # Blank line between emails

        return "\n".join(lines).rstrip()

    @staticmethod
    def format_calendar_events(events: List[Dict[str, Any]]) -> str:
        """Format list of calendar events.

        Args:
            events: List of event records

        Returns:
            Formatted human-readable string
        """
        lines = ["Calendar Events:", "-" * 60]

        for event in events:
            lines.append(f"[EVENT] {event.get('summary', 'Untitled Event')}")

            # Format start and end times nicely
            if event.get('start'):
                start_str = OutputFormatter._format_datetime(event['start'])
                lines.append(f"   {start_str}")

            if event.get('end') and event['end'] != event.get('start'):
                end_str = OutputFormatter._format_datetime(event['end'], label="End")
                lines.append(f"   {end_str}")

            if event.get('description'):
                lines.append(f"   Description: {event['description']}")

            lines.append("")  # Blank line between events

        return "\n".join(lines).rstrip()

    @staticmethod
    def _format_datetime(dt_string: str, label: str = "Start") -> str:
        """Format a datetime string to a readable format.

        Args:
            dt_string: ISO 8601 datetime string or date string
            label: Label to prefix (e.g., "Start", "End")

        Returns:
            Formatted datetime string like "Start: Mon, Dec 22, 8:00 AM"
        """
        try:
            from datetime import datetime

            # Try parsing ISO 8601 format with timezone (e.g., "2025-12-22T08:00:00-05:00")
            if 'T' in dt_string:
                # Remove timezone info for parsing
                dt_part = dt_string.split('+')[0].split('-')[0] if '+' in dt_string or dt_string.count('-') > 2 else dt_string.split('+')[0]
                # Handle the timezone offset at the end
                if '+' in dt_string:
                    dt_part = dt_string.split('+')[0]
                elif dt_string.count(':') >= 2:  # Has timezone offset
                    # Find the last hyphen or plus that indicates timezone
                    for i in range(len(dt_string) - 1, -1, -1):
                        if dt_string[i] in ['+', '-'] and i > 10:  # After the date part
                            dt_part = dt_string[:i]
                            break

                dt_obj = datetime.fromisoformat(dt_part)
                date_str = dt_obj.strftime('%a, %b %d')
                time_str = dt_obj.strftime('%I:%M %p')
                return f"{label}: {date_str} at {time_str}"
            else:
                # Date-only format (e.g., "2025-12-26")
                dt_obj = datetime.strptime(dt_string, '%Y-%m-%d')
                date_str = dt_obj.strftime('%a, %b %d')
                return f"{label}: {date_str} (all day)"
        except Exception:
            # Fallback if parsing fails
            return f"{label}: {dt_string}"

    @staticmethod
    def _format_value(value: Any, indent: int = 0) -> str:
        """Recursively format a value with proper indentation.

        Args:
            value: Value to format
            indent: Current indentation level

        Returns:
            Formatted string
        """
        indent_str = " " * indent
        next_indent_str = " " * (indent + 2)

        if isinstance(value, dict):
            if not value:
                return "{}"

            lines = ["{"]
            for key, val in value.items():
                if isinstance(val, (dict, list)) and val:
                    formatted = OutputFormatter._format_value(val, indent + 2)
                    lines.append(f"{next_indent_str}{key}: {formatted}")
                else:
                    formatted_val = OutputFormatter._format_value(val, indent + 2)
                    lines.append(f"{next_indent_str}{key}: {formatted_val}")
            lines.append(f"{indent_str}}}")
            return "\n".join(lines)

        elif isinstance(value, list):
            if not value:
                return "[]"

            # If list contains simple values, format on one line if short
            if all(isinstance(v, (str, int, float, bool, type(None))) for v in value):
                simple_list = "[" + ", ".join(str(v) for v in value) + "]"
                if len(simple_list) <= 60:
                    return simple_list

            lines = ["["]
            for item in value:
                if isinstance(item, (dict, list)) and item:
                    formatted = OutputFormatter._format_value(item, indent + 2)
                    lines.append(f"{next_indent_str}{formatted}")
                else:
                    formatted = OutputFormatter._format_value(item, indent + 2)
                    lines.append(f"{next_indent_str}{formatted}")
            lines.append(f"{indent_str}]")
            return "\n".join(lines)

        elif isinstance(value, bool):
            return "Yes" if value else "No"

        elif isinstance(value, str):
            # Don't quote short strings
            if len(value) < 50 and "\n" not in value:
                return value
            # Quote longer strings
            return f'"{value}"'

        elif value is None:
            return "-"

        else:
            return str(value)


def print_result(result: Dict[str, Any]) -> None:
    """Print an agent result in human-readable format.

    Args:
        result: Dictionary containing agent execution result
    """
    print(OutputFormatter.format_agent_result(result))


def print_tool_output(tool_name: str, output: Dict[str, Any]) -> None:
    """Print a tool output in human-readable format.

    Args:
        tool_name: Name of the tool
        output: Tool output dictionary
    """
    print(OutputFormatter.format_tool_output(tool_name, output))


def print_tools_list(tools: Dict[str, str]) -> None:
    """Print available tools in human-readable format.

    Args:
        tools: Dictionary of tool names and descriptions
    """
    print(OutputFormatter.format_tools_list(tools))
