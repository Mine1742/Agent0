#!/usr/bin/env python3
"""Test script for Google Agent demonstration."""

from agents import GoogleAgent
import json


def main():
    """Run demonstration of Google Agent capabilities."""
    print("=" * 70)
    print("GOOGLE AGENT DEMONSTRATION")
    print("=" * 70)

    # Initialize agent with verbose output
    agent = GoogleAgent(verbose=True)

    print("\n1. Listing Available Tools")
    print("-" * 70)
    tools = agent.list_available_tools()
    for tool_name, description in tools.items():
        print(f"  • {tool_name}")
        print(f"    {description}\n")

    print("\n2. Checking Agent Status")
    print("-" * 70)
    status = agent.get_agent_status()
    print(f"Status: {status['status']}")
    print(f"Available tools: {status['available_tools']}")
    print(f"Tools: {', '.join(status['tools'])}")

    print("\n3. Executing Sample Tasks")
    print("-" * 70)

    # Task 1: Check unread emails in inbox
    print("\nTask 1: How many unread emails are in my inbox?")
    result1 = agent.execute_task("How many unread emails are in my inbox?")
    print(f"Success: {result1['ok']}")
    if result1['result']:
        print(f"Result: {result1['result'].get('summary', 'N/A')}")
    if result1['suggested_tools']:
        print(f"Suggested tools: {result1['suggested_tools'][0]}")

    # Task 2: Check calendar
    print("\nTask 2: What events do I have today?")
    result2 = agent.execute_task("What events do I have today?")
    print(f"Success: {result2['ok']}")
    if result2['result']:
        print(f"Result: {result2['result'].get('summary', 'N/A')}")

    # Task 3: Check specific email sender
    print("\nTask 3: How many emails from caitrinconroy@gmail.com in my inbox?")
    result3 = agent.execute_task(
        "How many emails from caitrinconroy@gmail.com in my inbox?"
    )
    print(f"Success: {result3['ok']}")
    if result3['result']:
        print(f"Result: {result3['result'].get('summary', 'N/A')}")

    # Task 4: Check work schedule
    print("\nTask 4: How many days does AJ work this week?")
    result4 = agent.execute_task("How many days does AJ work this week?")
    print(f"Success: {result4['ok']}")
    if result4['result']:
        print(f"Result: {result4['result'].get('summary', 'N/A')}")

    print("\n4. Task History Summary")
    print("-" * 70)
    history = agent.get_task_history()
    for i, task in enumerate(history, 1):
        status_icon = "[OK]" if task["error"] is None else "[FAIL]"
        print(f"{status_icon} Task {i}: {task['goal']}")
        if task['error']:
            print(f"  Error: {task['error']}")

    print("\n5. Agent Statistics")
    print("-" * 70)
    final_status = agent.get_agent_status()
    total = final_status['total_tasks_executed']
    successful = final_status['successful_tasks']
    failed = final_status['failed_tasks']

    print(f"Total tasks executed: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    if total > 0:
        success_rate = (successful / total) * 100
        print(f"Success rate: {success_rate:.1f}%")

    print("\n6. Exporting Task History")
    print("-" * 70)
    export_file = "agent_history.json"
    agent.export_history(export_file)
    print(f"[OK] Task history exported to {export_file}")

    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nTo use the agent in your code:")
    print("  from agents import GoogleAgent")
    print("  agent = GoogleAgent()")
    print("  result = agent.execute_task('your task here')")
    print("\nFor more information, see: agents/GOOGLE_AGENT_GUIDE.md")


if __name__ == "__main__":
    main()
