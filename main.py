"""Example runner for the template agent_project.

This file demonstrates wiring together state, memory, a planner, and tools.
It uses the ClaudePlanner with the Anthropic Claude API.
"""
from __future__ import annotations

import argparse

from agent import AgentState
from agent import Memory
from agent import Planner
from agent.planner import ClaudePlanner, MockPlanner
from agent.agent import run_agent

from tools import ToolRegistry
from tools.base import NoopTool
from tools.filesystem import ReadFile, SafeWriteFile
from tools.network import HttpGet
from tools.gmail import QueryGmail, ReadEmail, SendEmail, ListGmailLabels
from utils import print_result, OutputFormatter


def build_tools() -> dict[str, object]:
    registry = ToolRegistry()
    registry.register(NoopTool())
    registry.register(ReadFile())
    registry.register(SafeWriteFile())
    registry.register(HttpGet())

    # Gmail tools
    try:
        registry.register(QueryGmail())
        registry.register(ReadEmail())
        registry.register(SendEmail())
        registry.register(ListGmailLabels())
    except ImportError:
        print("Warning: Gmail tools not available. Install google-auth-oauthlib to enable.")

    return registry.as_dict()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--goal", type=str, default="Describe the README contents")
    parser.add_argument("--use-mock", action="store_true", help="Use MockPlanner instead of ClaudePlanner")
    args = parser.parse_args()

    state = AgentState(goal=args.goal)
    memory = Memory()

    # Use ClaudePlanner by default (requires ANTHROPIC_API_KEY in .env)
    # Use --use-mock flag to use the deterministic MockPlanner instead
    if args.use_mock:
        print("Using MockPlanner (deterministic, no API calls)")
        planner: Planner = MockPlanner()
    else:
        print("Using ClaudePlanner (Anthropic Claude API)")
        try:
            planner = ClaudePlanner()
        except ValueError as e:
            print(f"Error: {e}")
            print("Falling back to MockPlanner. Set ANTHROPIC_API_KEY in .env to use ClaudePlanner.")
            planner = MockPlanner()

    tools = build_tools()

    final = run_agent(state, tools=tools, planner=planner, memory=memory)

    # Print results in human-readable format
    result_dict = {
        "ok": True,
        "goal": final.goal,
        "steps_executed": final.step,
        "complete": final.done,
        "history": final.history[-5:] if final.history else [],
    }
    print_result(result_dict)


if __name__ == "__main__":
    main()
