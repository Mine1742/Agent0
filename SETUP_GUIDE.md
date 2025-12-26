# Setup Guide - Agent0 Project

This guide will help you get Agent0 up and running on your system.

## Prerequisites

- Python 3.11+
- Git
- Google account (for Gmail & Calendar access)
- Anthropic API key

## Step 1: Clone the Repository

```bash
git clone https://github.com/Mine1742/Agent0.git
cd Agent0
```

## Step 2: Create Python Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Configure Environment Variables

1. Copy the template:
```bash
cp .env.example .env
```

2. Edit `.env` and add your configuration:

```bash
# Get your Anthropic API key from https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-xxxxx-your-key-here

# Optionally specify which Claude model to use
AGENT_CLAUDE_MODEL=claude-haiku-4-5-20251001
```

## Step 5: Set Up Google Authentication

### A. Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable these APIs:
   - Gmail API
   - Google Calendar API
4. Go to "Credentials" and create OAuth 2.0 credentials:
   - Application Type: Desktop application
   - Click "Create"
5. Download the JSON file

### B. Add Credentials to Project

```bash
# Save the downloaded JSON file as credentials.json in the project root
mv ~/Downloads/client_secret_*.json credentials.json
```

### C. First Run Authorization

When you first run the agent with Gmail/Calendar features:
1. A browser window will open
2. Sign in with your Google account
3. Grant the requested permissions
4. A `token.pickle` file will be created automatically (don't commit this!)

## Step 6: Verify Installation

Test the setup:

```bash
# Test with a simple query
python gquery "How many unread emails do I have?"

# Test calendar access
python gquery "What events do I have today?"

# Test with verbose output
python -c "from agents import GoogleAgent; agent = GoogleAgent(verbose=True); print(agent.execute_task('Hello'))"
```

## File Structure

```
Agent0/
├── agents/                 # Agent implementations
│   ├── google_agent.py    # Main Google services agent
│   ├── llm_parser.py      # LLM-powered query parser
│   └── ...
├── tools/                  # Tool implementations
│   ├── gmail.py           # Gmail tools
│   ├── calendar.py        # Calendar tools
│   └── ...
├── utils/                  # Utility modules
│   ├── formatter.py       # Output formatting
│   └── ...
├── .env                    # Environment variables (created by you)
├── credentials.json        # Google OAuth credentials (not in git)
├── token.pickle           # Google OAuth token (auto-generated, not in git)
├── gquery                 # CLI tool for quick queries
├── main.py                # Example main script
└── QUICKSTART.md          # Quick start guide
```

## Configuration Files

### `.env` (Your Local Configuration)
**Never commit this file!** It contains sensitive information.

```bash
ANTHROPIC_API_KEY=your-key-here
AGENT_CLAUDE_MODEL=claude-haiku-4-5-20251001
```

### `.env.example` (Template for Others)
This is the template. Copy it to `.env` and fill in your values.

### `.gitignore` (What Git Ignores)
Prevents committing sensitive files:
- `credentials.json` - Google OAuth credentials
- `token.pickle` - Google OAuth token
- `.env` - Your environment variables
- `__pycache__/` - Python cache
- `.venv/` - Virtual environment

## Security Best Practices

1. **Never commit secrets**:
   - `.env` is in `.gitignore`
   - `credentials.json` is in `.gitignore`
   - `token.pickle` is in `.gitignore`

2. **Protect your API keys**:
   - Keep `ANTHROPIC_API_KEY` secret
   - Keep Google credentials private

3. **Manage token.pickle**:
   - This file is generated automatically
   - Regenerate by deleting if needed
   - Also in `.gitignore`

## Common Commands

### Use the CLI Tool

```bash
# Query events
python gquery "What events do I have this week?"

# Query emails
python gquery "How many unread emails?"

# Count from specific person
python gquery "How many emails from alice@example.com?"
```

### Use Programmatically

```python
from agents import GoogleAgent

agent = GoogleAgent()
result = agent.execute_task("What events do I have today?")
print(result['result'])
```

### Enable Verbose Logging

```python
from agents import GoogleAgent

agent = GoogleAgent(verbose=True)
result = agent.execute_task("your query")
# Shows: [GoogleAgent] Starting task: ...
```

## Troubleshooting

### "API Key not found"
- Make sure `ANTHROPIC_API_KEY` is in `.env`
- Check that `.env` is in the project root
- Verify the key is valid

### "Gmail API not enabled"
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Select your project
- Go to APIs & Services > Enabled APIs & services
- Search for "Gmail API"
- Click "Enable"

### "Insufficient authentication scopes"
- Delete `token.pickle`
- Run the agent again
- Re-authorize when prompted

### "No module named anthropic"
- Make sure virtual environment is activated
- Run: `pip install -r requirements.txt`

### "credentials.json not found"
- Make sure you downloaded the OAuth credentials
- Save it as `credentials.json` in the project root
- Make sure it's NOT in git (should be in `.gitignore`)

## Integration Guide

See [agents/PARSER_INTEGRATION_GUIDE.md](agents/PARSER_INTEGRATION_GUIDE.md) for how to integrate the LLM Query Parser into other agents and tools.

## Next Steps

1. Read [QUICKSTART.md](QUICKSTART.md) for usage examples
2. Try some queries with the `gquery` command
3. Check [agents/README_QUERY_PARSER.md](agents/README_QUERY_PARSER.md) for the LLM parsing system
4. Explore [agents/google_agent.py](agents/google_agent.py) to understand the implementation

## Support

For issues:
1. Check this guide
2. Enable verbose logging: `GoogleAgent(verbose=True)`
3. Check the relevant documentation in the `agents/` directory
4. See git logs: `git log --oneline`

## Updating

To pull latest changes:

```bash
git pull origin main
pip install -r requirements.txt  # In case dependencies changed
```

## Creating New Agents

To create a new agent:

1. See [agents/PARSER_INTEGRATION_GUIDE.md](agents/PARSER_INTEGRATION_GUIDE.md)
2. Use [agents/google_agent.py](agents/google_agent.py) as a reference
3. Integrate the LLM query parser for smart query handling

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | - | Your Anthropic API key |
| `AGENT_CLAUDE_MODEL` | No | `claude-haiku-4-5-20251001` | Claude model to use |
| `GOOGLE_CALENDAR_ID` | No | `primary` | Google Calendar ID |
| `GMAIL_USER_ID` | No | `me` | Gmail user ID |

## Files Not in Git

These files are automatically created and should not be committed:

- `.env` - Your personal configuration
- `credentials.json` - Google OAuth credentials
- `token.pickle` - Google OAuth token (auto-generated)
- `__pycache__/` - Python cache files
- `.venv/` - Virtual environment

All these are listed in `.gitignore`.
