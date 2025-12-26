"""Simple Anthropic / Claude client wrapper for the project.

Usage:
  from tools.claude_client import ClaudeClient
  client = ClaudeClient()
  resp = client.send_prompt("Say hello")
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional
import re
import pathlib

# Try to load local .env for convenience during development
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEFAULT_MODEL = os.getenv("AGENT_CLAUDE_MODEL", "claude-2.1")
DEFAULT_TIMEOUT = int(os.getenv("AGENT_CLAUDE_TIMEOUT", "30"))


class ClaudeClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, timeout: Optional[int] = None):
        self.api_key = api_key or ANTHROPIC_API_KEY
        self.model = model or DEFAULT_MODEL
        self.timeout = timeout or DEFAULT_TIMEOUT
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set in environment")

        # Attempt to read raw model from .env to handle cases where dotenv truncates or parses incorrectly
        try:
            candidate = pathlib.Path(__file__).resolve().parents[1] / ".env"
            if candidate.exists():
                raw = candidate.read_text(encoding="utf-8")
                m = re.search(r"^AGENT_CLAUDE_MODEL=(.*)$", raw, flags=re.M)
                if m:
                    raw_val = m.group(1).strip().strip('"').strip("'")
                    if raw_val and raw_val != self.model:
                        self.model = raw_val
        except Exception:
            pass

        # Lazy import to avoid hard dependency at module import time
        try:
            import anthropic as _anthropic
            # instantiate client from module (keeps access to exception classes)
            if hasattr(_anthropic, "Anthropic"):
                self._client = _anthropic.Anthropic(api_key=self.api_key)
            elif hasattr(_anthropic, "Client"):
                # newer/alternate SDK naming
                self._client = _anthropic.Client(api_key=self.api_key)
            else:
                # last resort: try to construct using module directly
                self._client = _anthropic
            self._anthropic = _anthropic
        except Exception:
            # If the official SDK isn't available, raise a helpful error
            raise RuntimeError("Failed to import the Anthropic SDK. Install with `pip install anthropic`.")

    def send_prompt(self, prompt: str, max_tokens: int = 512, temperature: float = 0.0) -> str:
        """Send a prompt to Claude and return the assistant text.

        This wrapper attempts to use the `messages.create` (new Messages API) first for modern models,
        then falls back to `completions.create` if needed.
        """
        last_err: Optional[Exception] = None

        # Compose prompt using HUMAN/AI markers if available in the SDK
        try:
            HUMAN_PROMPT = getattr(self._anthropic, "HUMAN_PROMPT", None)
            AI_PROMPT = getattr(self._anthropic, "AI_PROMPT", None)
            if HUMAN_PROMPT and AI_PROMPT:
                full_prompt = f"{HUMAN_PROMPT}{prompt}{AI_PROMPT}"
            else:
                full_prompt = prompt
        except Exception:
            full_prompt = prompt

        # 1) Try messages (new Messages API) first for modern models
        try:
            if hasattr(self._client, "messages"):
                # messages.create expects a `messages` iterable. Build a minimal user message.
                message_obj = [{
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }]
                resp = self._client.messages.create(
                    model=self.model,
                    messages=message_obj,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    timeout=self.timeout,
                )
                # Extract text from response
                if hasattr(resp, 'content') and resp.content:
                    for block in resp.content:
                        if hasattr(block, 'text'):
                            return block.text
                return getattr(resp, "text", "")
        except Exception as e:
            last_err = e
            # If messages fails, fall through to completions

        # 2) Try completions API as fallback
        try:
            if hasattr(self._client, "completions"):
                resp = self._client.completions.create(
                    model=self.model,
                    prompt=full_prompt,
                    max_tokens_to_sample=max_tokens,
                    temperature=temperature,
                    timeout=self.timeout,
                )
                return getattr(resp, "completion", getattr(resp, "text", resp.get("completion", "")))
        except Exception as e:
            if last_err:
                raise RuntimeError(f"Claude request failed: {last_err}")
            raise RuntimeError(f"Claude request failed: {e}")

        if last_err:
            raise RuntimeError(f"Claude request failed: {last_err}")
        raise RuntimeError("Unsupported Anthropic client interface")
