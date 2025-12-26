"""Planner interface and implementations.

Planners accept the current state and context, and return a simple action
specification. Production planners should wrap an LLM SDK.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass
from typing import Any, Dict, Protocol, Optional

from tools.claude_client import ClaudeClient
from config.settings import CLAUDE_MODEL, ANTHROPIC_API_KEY


class Planner(Protocol):
    def plan(self, state: "AgentState", context: str) -> Dict[str, Any]:
        """Return an action dict with keys: name (str) and args (dict).

        The planner should NOT execute tools; it only *proposes* actions.
        """


@dataclass
class MockPlanner:
    """A simple rule-based planner used as a default example.

    It demonstrates the planner contract without requiring an LLM.
    """

    def plan_with_tools(self, state: "AgentState", context: str, tools: Dict[str, Any]) -> Dict[str, Any]:
        # Very small rule set: if goal mentioned in context, finish; else ask to inspect
        if state.goal.lower() in context.lower():
            return {"name": "noop", "args": {}, "reason": "goal appears in context"}
        # Default action: use noop (no other tools to use in mock planner)
        return {"name": "noop", "args": {}, "reason": "default mock action"}

    def plan(self, state: "AgentState", context: str) -> Dict[str, Any]:
        # Very small rule set: if goal mentioned in context, finish; else ask to inspect
        if state.goal.lower() in context.lower():
            return {"name": "noop", "args": {}, "reason": "goal appears in context"}
        # Default action: summarize current state
        return {"name": "describe_state", "args": {"brief": True}, "reason": "default summarization"}


class ClaudePlanner:
    """LLM-based planner using Claude and the Anthropic API.

    This planner uses the Claude API to decide what action to take next.
    It reads the system prompt from prompts/system.txt and formats a message
    with the current goal, context, and available tools.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize the Claude planner.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY from config)
            model: Model name (defaults to CLAUDE_MODEL from config)
        """
        self.api_key = api_key or ANTHROPIC_API_KEY
        self.model = model or CLAUDE_MODEL

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set. Please configure it in your .env file.")

        self.client = ClaudeClient(api_key=self.api_key, model=self.model)

        # Load system prompt
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load the system prompt from prompts/system.txt."""
        try:
            prompt_path = pathlib.Path(__file__).resolve().parent.parent / "prompts" / "system.txt"
            if prompt_path.exists():
                return prompt_path.read_text(encoding="utf-8")
        except Exception:
            pass

        # Fallback prompt if file doesn't exist
        return """You are an autonomous software agent. Follow these rules strictly:

- Behave as a helpful, honest, and conservative software engineer.
- When proposing an action, respond with valid JSON containing 'name' and 'args' keys.
- Use the format: {"name": "tool_name", "args": {"key": "value"}, "reason": "explanation"}
- Only propose actions that are safe and deterministic.
- If the goal is satisfied, propose the 'noop' action with reason 'goal_satisfied'."""

    def plan_with_tools(self, state: "AgentState", context: str, tools: Dict[str, Any]) -> Dict[str, Any]:
        """Use Claude to propose the next action, aware of available tools.

        Args:
            state: Current agent state
            context: Available context from memory
            tools: Available tools dict

        Returns:
            Action dict with keys: name, args, reason
        """
        # Build tool descriptions
        tool_descriptions = []
        for tool_name, tool in tools.items():
            desc = getattr(tool, "description", "No description")
            tool_descriptions.append(f"- {tool_name}: {desc}")

        tools_section = "\n".join(tool_descriptions) if tool_descriptions else "No tools available"

        # Build the prompt for Claude
        prompt = f"""Current Goal: {state.goal}

Available Context:
{context}

Agent Step: {state.step}

Available Tools:
{tools_section}

Based on the goal and context above, decide what action to take next using only the available tools.
Respond with a JSON object containing 'name', 'args', and 'reason' keys.
Example: {{"name": "read_file", "args": {{"path": "/tmp/file.txt"}}, "reason": "reading file to check contents"}}

If the goal has been satisfied or you cannot proceed, respond with: {{"name": "noop", "args": {{}}, "reason": "explanation"}}

Your response must be valid JSON only, no other text."""

        return self._execute_plan(prompt)

    def plan(self, state: "AgentState", context: str) -> Dict[str, Any]:
        """Use Claude to propose the next action based on state and context.

        Args:
            state: Current agent state
            context: Available context from memory

        Returns:
            Action dict with keys: name, args, reason
        """
        # Build the prompt for Claude
        prompt = f"""Current Goal: {state.goal}

Available Context:
{context}

Agent Step: {state.step}

Based on the goal and context above, decide what action to take next.
Respond with a JSON object containing 'name', 'args', and 'reason' keys.
Example: {{"name": "read_file", "args": {{"path": "/tmp/file.txt"}}, "reason": "reading file to check contents"}}

If the goal has been satisfied or you cannot proceed, respond with: {{"name": "noop", "args": {{}}, "reason": "explanation"}}

Your response must be valid JSON only, no other text."""

        return self._execute_plan(prompt)

    def _execute_plan(self, prompt: str) -> Dict[str, Any]:
        """Execute the planning prompt and parse the response.

        Args:
            prompt: The prompt to send to Claude

        Returns:
            Action dict
        """
        try:
            response = self.client.send_prompt(prompt, max_tokens=512, temperature=0.3)

            # Clean up markdown code blocks if present
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]  # Remove ```json
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]  # Remove ```
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]  # Remove trailing ```
            cleaned = cleaned.strip()

            # Parse the JSON response
            action = json.loads(cleaned)

            # Ensure required keys exist
            if "name" not in action:
                action["name"] = "noop"
            if "args" not in action:
                action["args"] = {}
            if "reason" not in action:
                action["reason"] = "Claude response"

            return action

        except json.JSONDecodeError as e:
            # If parsing fails, return a noop action
            return {
                "name": "noop",
                "args": {},
                "reason": f"Failed to parse Claude response: {e}"
            }
        except Exception as e:
            # Catch any other errors and return noop
            return {
                "name": "noop",
                "args": {},
                "reason": f"Planner error: {e}"
            }
