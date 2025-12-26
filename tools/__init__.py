"""Tools package for the template project.

Expose commonly used tool base classes for convenience.
"""
from .base import Tool, ToolRegistry
from .claude_client import ClaudeClient

__all__ = ["Tool", "ToolRegistry", "ClaudeClient"]
