"""Small script to test Claude client locally.

Run:
    python examples/claude_test.py

It will raise if the API key is not set.
"""
import os
import sys

# Ensure project root is on sys.path so `tools` package can be imported
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.claude_client import ClaudeClient


def main():
    try:
        client = ClaudeClient()
        print(client.send_prompt("Say hello in one sentence."))
    except Exception as e:
        print("Error running Claude example:", e)
        print()
        print("Quick checks:")
        print("- Have you installed dependencies? run: pip install -r requirements.txt")
        print("- Is ANTHROPIC_API_KEY set? e.g. export ANTHROPIC_API_KEY=sk-... or create a .env file")
        raise


if __name__ == "__main__":
    main()
