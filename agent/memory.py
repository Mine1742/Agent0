"""Simple in-memory working memory for the template agent.

This keeps a list of textual memory entries and can produce a joined
context string for planners. It's small and easily replaced by a vector
store in real projects.
"""
from __future__ import annotations

from typing import List


class Memory:
    def __init__(self) -> None:
        self._items: List[str] = []

    def add(self, text: str) -> None:
        """Add a memory item (prefer short, relevant items)."""
        self._items.append(text)

    def recent(self, n: int = 10) -> List[str]:
        return self._items[-n:]

    def build_context(self, max_items: int = 10) -> str:
        return "\n".join(self.recent(max_items))
