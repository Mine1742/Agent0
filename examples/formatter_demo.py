"""Demo of human-readable output formatting.

This example shows how the new OutputFormatter displays results
in a clean, easy-to-read format instead of raw JSON.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import OutputFormatter, print_result, print_tool_output, print_tools_list


def demo_agent_result():
    """Show formatted agent result output."""
    print("\n" + "=" * 70)
    print("AGENT RESULT FORMAT")
    print("=" * 70 + "\n")

    result = {
        "ok": True,
        "goal": "Count unread emails and show today's calendar events",
        "result": {
            "emails": {
                "unread_count": 7,
                "from_alice": 3,
                "from_bob": 2,
            },
            "calendar": {
                "events_today": 4,
                "next_event": "Team standup at 10:00 AM",
            }
        },
        "steps_executed": 3,
        "suggested_tools": ["send_email", "create_event"],
        "task_id": 42,
    }

    print_result(result)


def demo_tool_output():
    """Show formatted tool output."""
    print("\n" + "=" * 70)
    print("TOOL OUTPUT FORMAT")
    print("=" * 70 + "\n")

    output = {
        "ok": True,
        "result": {
            "emails": [
                {
                    "from": "alice@example.com",
                    "subject": "Project update",
                    "snippet": "Here's the latest status on the project...",
                },
                {
                    "from": "bob@example.com",
                    "subject": "Meeting tomorrow",
                    "snippet": "Let's sync up about the new initiative...",
                }
            ],
            "count": 2,
            "query": "is:unread from:alice OR from:bob",
        },
        "message": "Successfully retrieved 2 emails matching query"
    }

    print_tool_output("QueryGmail", output)


def demo_tools_list():
    """Show formatted tools list."""
    print("\n" + "=" * 70)
    print("TOOLS LIST FORMAT")
    print("=" * 70 + "\n")

    tools = {
        "query_gmail": "Query Gmail with filters (from, to, subject, etc)",
        "read_email": "Read the full content of an email by message ID",
        "send_email": "Send an email to one or more recipients",
        "list_gmail_labels": "List all labels in Gmail",
        "query_events": "Query calendar events with date ranges",
        "create_event": "Create a new calendar event",
    }

    print_tools_list(tools)


def demo_failed_result():
    """Show formatted error result."""
    print("\n" + "=" * 70)
    print("FAILED RESULT FORMAT")
    print("=" * 70 + "\n")

    result = {
        "ok": False,
        "goal": "Send email to invalid.user@",
        "error": "Invalid email address: invalid.user@",
        "suggested_tools": ["send_email"],
        "task_id": 43,
    }

    print_result(result)


def demo_complex_nested_result():
    """Show formatted result with complex nested data."""
    print("\n" + "=" * 70)
    print("COMPLEX NESTED RESULT FORMAT")
    print("=" * 70 + "\n")

    result = {
        "ok": True,
        "goal": "Get comprehensive email and calendar summary",
        "result": {
            "email_summary": {
                "total_unread": 12,
                "by_sender": {
                    "alice@example.com": 5,
                    "bob@example.com": 3,
                    "team@example.com": 4,
                },
                "recent_subjects": [
                    "Project kickoff meeting",
                    "Budget review",
                    "Weekly status",
                ]
            },
            "calendar_summary": {
                "events_today": 3,
                "events_this_week": 8,
                "busy_hours": "9:00 AM - 12:00 PM, 2:00 PM - 4:00 PM",
            },
            "action_items": [
                "Reply to Alice about Q4 roadmap",
                "Prepare budget presentation",
                "Schedule 1:1 with team lead",
            ]
        },
        "steps_executed": 4,
        "suggested_tools": ["send_email", "create_event", "read_email"],
        "task_id": 44,
    }

    print_result(result)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Human-Readable Output Formatter Demo")
    print("=" * 70)

    demo_agent_result()
    demo_tool_output()
    demo_tools_list()
    demo_failed_result()
    demo_complex_nested_result()

    print("\n" + "=" * 70)
    print("All demos completed! The formatter makes output much more readable.")
    print("=" * 70 + "\n")
