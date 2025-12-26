from __future__ import annotations

from typing import Any, Dict


class Tool:
    """Base class for tools.

    Subclasses should set `name` and `description`, and implement `run`.
    """

    name: str = "unnamed"
    description: str = ""

    def run(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover - simple base
        raise NotImplementedError()


class NoopTool(Tool):
    """A no-operation tool that does nothing.

    Used when the agent decides no action is needed.
    """

    name = "noop"
    description = "Do nothing. Use when the goal is satisfied or no action is needed."

    def run(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return {"done": True, "message": "No action taken"}


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def as_dict(self) -> Dict[str, Tool]:
        return dict(self._tools)
