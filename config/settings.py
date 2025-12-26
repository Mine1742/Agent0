"""Default configuration values for the agent template.

Override by importing and setting values in your deployment environment.
"""
from __future__ import annotations

import os

# Maximum number of planning/execution steps before the agent stops
MAX_STEPS: int | None = int(os.getenv("AGENT_MAX_STEPS", "50"))

# Whether the agent should automatically allow potentially destructive tools
APPROVE_DESTRUCTIVE: bool = os.getenv("AGENT_APPROVE_DESTRUCTIVE", "false").lower() == "true"

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# LLM provider selection (left generic so users can adapt)
LLM_PROVIDER: str = os.getenv("AGENT_LLM_PROVIDER", "anthropic")

# Anthropic / Claude settings
# Set your Anthropic API key in the environment variable `ANTHROPIC_API_KEY`.
ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY", None)
# Default Claude model to use (can be overridden via env or runtime config)
CLAUDE_MODEL: str = os.getenv("AGENT_CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
# Optional request timeout (seconds)
CLAUDE_REQUEST_TIMEOUT: int = int(os.getenv("AGENT_CLAUDE_TIMEOUT", "30"))
