from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class AgentState:
    """Minimal serializable agent state used across the template.

    Fields are intentionally small and explicit so agents remain inspectable.
    """

    goal: str
    history: List[str] = field(default_factory=list)
    results: List[Any] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    step: int = 0
    max_steps: int | None = 50
    done: bool = False

    def is_complete(self) -> bool:
        if self.done:
            return True
        if self.max_steps is not None and self.step >= self.max_steps:
            return True
        return False

    def add_history(self, entry: str) -> None:
        self.history.append(entry)

    def add_result(self, result: Any) -> None:
        self.results.append(result)
