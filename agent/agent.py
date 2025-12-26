"""Core agent loop implementation for the template.

This loop is intentionally minimal and synchronous. It:
- builds context from memory
- asks the planner for an action proposal
- validates and executes a matching tool
- updates state and memory

Tool execution is explicit and synchronous to keep behavior obvious.
"""
from __future__ import annotations

from typing import Dict, Any

from .state import AgentState
from .memory import Memory
from .planner import Planner


def run_agent(state: AgentState, *, tools: Dict[str, Any], planner: Planner, memory: Memory) -> AgentState:
    """Run a single-agent loop until completion and return final state.

    - `tools` is a mapping of tool name -> tool instance (must implement `.run(...)`).
    - `planner` proposes actions but does not run them.
    - `memory` accumulates observations and provides context.
    """

    while not state.is_complete():
        state.step += 1
        ctx = memory.build_context()
        # Pass tools to planner if it supports tool awareness
        if hasattr(planner, "plan_with_tools"):
            proposal = planner.plan_with_tools(state, ctx, tools)
        else:
            proposal = planner.plan(state, ctx)

        name = proposal.get("name")
        args = proposal.get("args", {})
        reason = proposal.get("reason")

        state.add_history(f"Step {state.step}: planner proposed {name} ({reason})")

        tool = tools.get(name)
        if tool is None:
            state.add_history(f"No tool named '{name}' registered. Skipping.")
            continue

        # Execute tool and record result
        try:
            result = tool.run(**args)
        except Exception as exc:  # noqa: BLE001 - we want to capture tool errors in state
            result = {"error": str(exc)}

        state.add_result({"tool": name, "result": result})

        # Build memory entry with prominent warnings
        memory_entry = f"Tool {name} result: {result}"
        if isinstance(result, dict) and result.get("discrepancy_warning"):
            # Make the warning very prominent
            memory_entry = (
                f"⚠️⚠️⚠️ IMPORTANT DISCREPANCY ⚠️⚠️⚠️\n"
                f"{result['discrepancy_warning']}\n"
                f"Tool {name} result: {result}"
            )
        memory.add(memory_entry)

        # Simple finishing condition: tool can set state.done in its result or effects
        if getattr(result, "get", None) and result.get("done"):
            state.done = True

    return state
