# AI Agent Template (Framework-Free)

This repository provides a minimal, extensible template for building and deploying AI agents **without third-party agent frameworks**.  
The goal is clarity, control, and long-term maintainability.

An agent here is treated as a **software system**, not a chatbot.

---

## What This Template Is

This project is a reference implementation of an AI agent built from first principles:

- Explicit agent state  
- Deterministic tools  
- Controlled execution loop  
- Clear separation of concerns  

There is **no LangChain, AutoGPT, n8n, or orchestration framework** involved.

Everything is readable, testable, and modifiable.

---

## Mental Model

An agent is composed of:

1. **Planner** – Uses an LLM to decide what to do next  
2. **Memory** – Controls what context the agent sees  
3. **Tools** – Deterministic code that performs actions  
4. **Agent Loop** – Orchestrates decisions and execution  

The LLM never directly performs work.  
It proposes actions.  
Your code decides whether those actions happen.

---

## Project Structure

agent_project/
│
├── agent/
│ ├── agent.py # Core agent loop
│ ├── planner.py # LLM decision logic
│ ├── memory.py # Context assembly
│ └── state.py # Agent state definition
│
├── tools/
│ ├── base.py # Tool interface
│ ├── filesystem.py # Example tool
│ └── network.py # Example tool
│
├── prompts/
│ └── system.txt # Agent identity & rules
│
├── config/
│ └── settings.py # Configuration values
│
├── main.py # Entry point
└── README.md



Each directory has a single responsibility.  
This structure is intentional and designed to scale.

---

## Requirements

- Python 3.11+  
- OpenAI Python SDK (or compatible LLM SDK)  
- Python standard library for everything else  

Install dependencies:

```bash
pip install openai

## Running the Agent

Edit main.py to define the agent’s goal:

from agent.agent import run_agent
from agent.state import AgentState

state = AgentState(
    goal="Summarize the contents of README.md"
)

run_agent(state)



Run the agent:
python main.py

The agent will:

Build context

Ask the planner what to do

Execute tools (if approved)

Update internal state

Exit when the goal is satisfied

Tools

Tools are plain Python classes with a shared interface.

Example:
class ReadFile(Tool):
    name = "read_file"
    description = "Reads a text file from disk"

    def run(self, path: str):
        with open(path, "r") as f:
            return f.read()

Tool design rules:

Deterministic behavior

Explicit side effects

No LLM calls inside tools

Easy to unit test

If a tool can cause harm (delete files, make network calls), the agent loop should explicitly gate its execution.


Prompts

The system prompt lives in prompts/system.txt.

This file defines:

Agent identity

Behavioral constraints

Tool usage rules

Changing this file alone should materially change agent behavior without modifying code.


Extending the Agent

Common extensions include:

Structured JSON tool calls

Tool schemas and validation

Permissioning and approval logic

Long-term memory via embeddings

Multi-agent coordination

API, worker, or cron-based deployment

This template stays minimal so extensions remain understandable rather than magical.

Philosophy

This project follows three principles:

Explicit state beats implicit behavior

LLMs decide, code executes

Understanding beats abstraction

Most agent frameworks are convenience layers over these same ideas.
This template keeps the mechanics visible.

Intended Audience

Engineers learning how agents actually work

Security-conscious or regulated environments

Internal automation and tooling teams

Anyone tired of black-box “AI magic”

License

Use freely. Modify aggressively.
Just don’t lie to yourself about what the agent is doing.


This README is now **drop-in ready** and sets a stable foundation for every agent and tool you build from here.

---

## Claude (Anthropic) setup

To use Claude as the LLM provider in this project:

- **Install dependencies:**

```bash
pip install -r requirements.txt
```

- **Set your API key:** create a `.env` file or set the environment variable `ANTHROPIC_API_KEY` with your Anthropic API key.

- **Configuration:** `config/settings.py` contains `ANTHROPIC_API_KEY`, `CLAUDE_MODEL`, and `CLAUDE_REQUEST_TIMEOUT` settings. You can also set `AGENT_LLM_PROVIDER=anthropic`.

- **Usage example:** import and use the provided client:

```python
from tools.claude_client import ClaudeClient

client = ClaudeClient()
resp = client.send_prompt("Write a one-line greeting")
print(resp)
```

This project provides a lightweight wrapper at `tools/claude_client.py` that handles basic Anthropic SDK usage.


