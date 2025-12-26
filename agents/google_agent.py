"""Google Agent - An autonomous agent for managing Google services.

This agent can:
- Query and manage Gmail inbox
- Query and manage Google Calendar
- Perform other Google service operations
- Suggest additional tools as needed

The agent is designed to be portable and reusable across projects.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
import json
from datetime import datetime

from tools.base import Tool
from tools.gmail import QueryGmail, ReadEmail, SendEmail, ListGmailLabels
from tools.calendar import ListCalendars, QueryEvents, CreateEvent, DeleteEvent
from agents.llm_parser import LLMQueryParser


class GoogleAgentToolkit:
    """Toolkit containing all available Google tools for the agent."""

    def __init__(self):
        """Initialize the toolkit with all Google tools."""
        self.tools = {
            # Gmail tools
            "query_gmail": QueryGmail(),
            "read_email": ReadEmail(),
            "send_email": SendEmail(),
            "list_gmail_labels": ListGmailLabels(),
            # Calendar tools
            "list_calendars": ListCalendars(),
            "query_events": QueryEvents(),
            "create_event": CreateEvent(),
            "delete_event": DeleteEvent(),
        }

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)

    def list_tools(self) -> Dict[str, str]:
        """List all available tools with descriptions."""
        return {name: tool.description for name, tool in self.tools.items()}

    def execute(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool with the given arguments."""
        tool = self.get_tool(tool_name)
        if not tool:
            return {"ok": False, "error": f"Tool '{tool_name}' not found"}

        try:
            result = tool.run(**kwargs)
            return result
        except Exception as e:
            return {"ok": False, "error": f"Failed to execute {tool_name}: {e}"}


class GoogleAgent:
    """Autonomous agent for managing Google services.

    This agent can:
    - Query Gmail for emails
    - Read and send emails
    - Query and manage calendar events
    - Suggest additional tools when needed
    - Work autonomously with your Google account

    The agent maintains a task history and can be extended with new tools.
    """

    def __init__(self, verbose: bool = False):
        """Initialize the Google Agent.

        Args:
            verbose: If True, print detailed execution logs
        """
        self.toolkit = GoogleAgentToolkit()
        self.verbose = verbose
        self.task_history = []
        self.suggested_tools = []
        try:
            self.query_parser = LLMQueryParser()
        except ImportError:
            self.query_parser = None
            self._log("Warning: LLM query parser not available, falling back to regex parsing")

    def execute_task(self, goal: str, max_steps: int = 10) -> Dict[str, Any]:
        """Execute a task goal with the agent.

        The agent will:
        1. Analyze the goal
        2. Select appropriate tools
        3. Execute the task
        4. Return results and suggestions

        Args:
            goal: The task goal to accomplish
            max_steps: Maximum number of tool executions (safety limit)

        Returns:
            Dictionary with task results, execution history, and suggestions
        """
        self._log(f"Starting task: {goal}")

        task_record = {
            "goal": goal,
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "result": None,
            "error": None,
        }

        # Parse the goal to determine which tools are needed
        tools_needed = self._determine_tools(goal)
        self._log(f"Tools identified for task: {tools_needed}")

        execution_count = 0
        result = None

        try:
            for tool_name in tools_needed:
                if execution_count >= max_steps:
                    raise Exception(f"Max steps ({max_steps}) exceeded")

                # Parse parameters from goal
                params = self._extract_parameters(goal, tool_name)
                self._log(f"Executing {tool_name} with params: {params}")

                # Execute the tool
                step_result = self.toolkit.execute(tool_name, **params)
                execution_count += 1

                # Record the step
                task_record["steps"].append({
                    "tool": tool_name,
                    "params": params,
                    "result": step_result,
                })

                if step_result.get("ok"):
                    result = step_result
                    self._log(f"[OK] {tool_name} executed successfully")
                else:
                    self._log(f"[FAIL] {tool_name} failed: {step_result.get('error')}")

            task_record["result"] = result

        except Exception as e:
            self._log(f"Task execution error: {e}")
            task_record["error"] = str(e)

        # Suggest additional tools if needed
        self._suggest_tools(goal, result)
        task_record["suggested_tools"] = self.suggested_tools

        # Save to history
        self.task_history.append(task_record)

        return {
            "ok": task_record["error"] is None,
            "goal": goal,
            "result": result,
            "steps_executed": execution_count,
            "suggested_tools": self.suggested_tools,
            "task_id": len(self.task_history) - 1,
        }

    def _determine_tools(self, goal: str) -> list[str]:
        """Determine which tools are needed for the goal."""
        # Use LLM to determine tools if available
        if self.query_parser:
            try:
                tool = self.query_parser.determine_tool(goal)
                self._log(f"LLM determined tool: {tool}")
                return [tool]
            except Exception as e:
                self._log(f"LLM tool determination failed: {e}, falling back to regex")

        # Fallback to regex-based determination
        goal_lower = goal.lower()
        tools = []

        # Gmail-related goals
        if any(word in goal_lower for word in ["email", "gmail", "inbox", "send", "read", "message"]):
            if any(word in goal_lower for word in ["count", "how many", "total"]):
                tools.append("query_gmail")
            elif any(word in goal_lower for word in ["read", "show", "display"]):
                tools.append("query_gmail")
            elif any(word in goal_lower for word in ["send", "write"]):
                tools.append("send_email")
            elif any(word in goal_lower for word in ["label", "folder"]):
                tools.append("list_gmail_labels")
            else:
                tools.append("query_gmail")

        # Calendar-related goals
        if any(word in goal_lower for word in ["calendar", "event", "schedule", "meeting", "appointment"]):
            if any(word in goal_lower for word in ["create", "add"]):
                tools.append("create_event")
            elif any(word in goal_lower for word in ["delete", "remove", "cancel"]):
                tools.append("delete_event")
            elif any(word in goal_lower for word in ["list all", "list calendars"]):
                # Only list_calendars if explicitly asking for "list all calendars" or "list calendars"
                tools.append("list_calendars")
            else:
                # Default to query_events for showing events, searching, finding, etc.
                tools.append("query_events")

        return tools if tools else ["query_gmail"]  # Default to Gmail query

    def _extract_parameters(self, goal: str, tool_name: str) -> Dict[str, Any]:
        """Extract parameters from the goal for the tool."""
        params = {}

        # Use LLM to extract parameters if available
        if self.query_parser:
            try:
                if tool_name == "query_gmail":
                    llm_params = self.query_parser.parse_gmail_query(goal)
                    self._log(f"LLM extracted Gmail params: {llm_params}")
                    return llm_params
                elif tool_name == "query_events":
                    llm_params = self.query_parser.parse_calendar_query(goal)
                    self._log(f"LLM extracted Calendar params: {llm_params}")
                    return llm_params
            except Exception as e:
                self._log(f"LLM parameter extraction failed: {e}, falling back to regex")

        # Fallback to regex-based extraction
        # For Gmail queries
        if tool_name == "query_gmail":
            # Look for folder mentions
            if "inbox" in goal.lower():
                params["query"] = "in:inbox"
            elif "sent" in goal.lower():
                params["query"] = "in:sent"
            elif "draft" in goal.lower():
                params["query"] = "in:draft"
            else:
                params["query"] = ""

            # Look for sender mentions
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, goal)
            if emails:
                email = emails[0]
                params["query"] = f"from:{email}"
                if "inbox" in goal.lower():
                    params["query"] += " in:inbox"

            # Look for unread mentions
            if "unread" in goal.lower():
                if params.get("query"):
                    params["query"] += " is:unread"
                else:
                    params["query"] = "is:unread"
                if "inbox" in goal.lower():
                    params["query"] += " in:inbox"

            # For "how many" questions, use count_all
            if any(word in goal.lower() for word in ["how many", "count", "total"]):
                params["count_all"] = True

        # For Calendar queries
        elif tool_name == "query_events":
            # Default to primary calendar
            params["calendar_id"] = "primary"

            # Look for search text
            if "work" in goal.lower():
                params["search_text"] = "Work"

            # Look for date ranges
            from datetime import datetime, timedelta
            import re

            if "today" in goal.lower():
                today = datetime.now().strftime('%Y-%m-%d')
                tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                params["time_min"] = today
                params["time_max"] = tomorrow
            elif "week" in goal.lower():
                today = datetime.now()

                # Check for specific week numbers (e.g., "third week in january", "week 3")
                week_match = re.search(r'(first|second|third|fourth|fifth|1st|2nd|3rd|4th|5th)\s+week', goal.lower())
                month_match = re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar(?!ch)|apr|may|jun|jul|aug|sep|oct|nov|dec)\b', goal.lower())

                if month_match and week_match:
                    # Parse month
                    month_str = month_match.group(1)
                    month_map = {
                        'january': 1, 'jan': 1,
                        'february': 2, 'feb': 2,
                        'march': 3, 'mar': 3,
                        'april': 4, 'apr': 4,
                        'may': 5,
                        'june': 6, 'jun': 6,
                        'july': 7, 'jul': 7,
                        'august': 8, 'aug': 8,
                        'september': 9, 'sep': 9,
                        'october': 10, 'oct': 10,
                        'november': 11, 'nov': 11,
                        'december': 12, 'dec': 12,
                    }
                    month_num = month_map.get(month_str.lower(), today.month)

                    # Parse week number
                    week_str = week_match.group(1)
                    week_map = {
                        'first': 1, '1st': 1, '1': 1,
                        'second': 2, '2nd': 2, '2': 2,
                        'third': 3, '3rd': 3, '3': 3,
                        'fourth': 4, '4th': 4, '4': 4,
                        'fifth': 5, '5th': 5, '5': 5,
                    }
                    week_num = week_map.get(week_str.lower(), 1)

                    # Calculate the date range for that week
                    # First, get the first day of the month
                    year = today.year if month_num >= today.month else today.year + 1
                    first_of_month = datetime(year, month_num, 1)

                    # Find the first Monday of the month
                    days_until_monday = (7 - first_of_month.weekday()) % 7
                    if days_until_monday == 0 and first_of_month.weekday() != 0:
                        days_until_monday = 7
                    first_monday = first_of_month + timedelta(days=days_until_monday)

                    # Get the start of the requested week
                    start_of_week = first_monday + timedelta(weeks=week_num - 1)
                    end_of_week = start_of_week + timedelta(days=6)

                    params["time_min"] = start_of_week.strftime('%Y-%m-%d')
                    params["time_max"] = end_of_week.strftime('%Y-%m-%d')
                elif "next" in goal.lower():
                    start_of_week = today - timedelta(days=today.weekday()) + timedelta(days=7)
                    end_of_week = start_of_week + timedelta(days=6)
                    params["time_min"] = start_of_week.strftime('%Y-%m-%d')
                    params["time_max"] = end_of_week.strftime('%Y-%m-%d')
                else:
                    # Default to this week
                    start_of_week = today - timedelta(days=today.weekday())
                    end_of_week = start_of_week + timedelta(days=6)
                    params["time_min"] = start_of_week.strftime('%Y-%m-%d')
                    params["time_max"] = end_of_week.strftime('%Y-%m-%d')

        # For creating events
        elif tool_name == "create_event":
            # Extract event details from goal
            import re
            # Look for date/time patterns
            date_pattern = r'\b\d{4}-\d{2}-\d{2}\b'
            dates = re.findall(date_pattern, goal)
            if dates:
                params["start_time"] = dates[0]
                if len(dates) > 1:
                    params["end_time"] = dates[1]

        return params

    def _suggest_tools(self, goal: str, result: Optional[Dict[str, Any]]) -> None:
        """Suggest additional tools that could help accomplish the goal better."""
        self.suggested_tools = []
        goal_lower = goal.lower()

        # Suggest tools based on goal type
        suggestions = {
            "email filters": "A tool to create and manage Gmail filters for automatic email organization",
            "email templates": "Pre-built email templates for common messages",
            "calendar reminders": "A tool to set and manage calendar event reminders",
            "email scheduling": "Schedule emails to be sent at a specific time",
            "calendar sharing": "Share calendars with other users",
            "email attachments": "Enhanced handling of email attachments",
            "bulk operations": "Perform bulk operations on multiple emails or events",
            "email search advanced": "Advanced search with complex query building",
            "calendar sync": "Sync calendars with external sources",
            "task management": "Google Tasks integration for task tracking",
        }

        # Add suggestions based on what was used
        if any(word in goal_lower for word in ["filter", "organize", "label", "sort"]):
            self.suggested_tools.append("Gmail Filters Tool - " + suggestions.get("email filters", ""))

        if any(word in goal_lower for word in ["template", "compose", "draft"]):
            self.suggested_tools.append("Email Templates - " + suggestions.get("email templates", ""))

        if any(word in goal_lower for word in ["reminder", "notify", "alert"]):
            self.suggested_tools.append("Calendar Reminders Tool - " + suggestions.get("calendar reminders", ""))

        if any(word in goal_lower for word in ["schedule", "send later"]):
            self.suggested_tools.append("Email Scheduling - " + suggestions.get("email scheduling", ""))

        if any(word in goal_lower for word in ["share", "permission", "access"]):
            self.suggested_tools.append("Calendar Sharing - " + suggestions.get("calendar sharing", ""))

        if any(word in goal_lower for word in ["bulk", "multiple", "batch"]):
            self.suggested_tools.append("Bulk Operations Tool - " + suggestions.get("bulk operations", ""))

    def _log(self, message: str) -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(f"[GoogleAgent] {message}")

    def get_task_history(self) -> list:
        """Get the history of executed tasks."""
        return self.task_history

    def list_available_tools(self) -> Dict[str, str]:
        """List all available tools with their descriptions."""
        return self.toolkit.list_tools()

    def add_custom_tool(self, name: str, tool: Tool) -> None:
        """Add a custom tool to the agent.

        Args:
            name: Name of the tool
            tool: Tool instance implementing the Tool interface
        """
        self.toolkit.tools[name] = tool
        self._log(f"Added custom tool: {name}")

    def reset_history(self) -> None:
        """Clear the task history."""
        self.task_history = []
        self._log("Task history cleared")

    def export_history(self, filepath: str) -> None:
        """Export task history to a JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.task_history, f, indent=2, default=str)
        self._log(f"Task history exported to {filepath}")

    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and statistics."""
        total_tasks = len(self.task_history)
        successful_tasks = sum(1 for task in self.task_history if task["error"] is None)

        return {
            "status": "active",
            "total_tasks_executed": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": total_tasks - successful_tasks,
            "available_tools": len(self.toolkit.tools),
            "tools": list(self.toolkit.tools.keys()),
        }
