# Google Agent - Deployment Checklist

Use this checklist when deploying the Google Agent to a new project.

## Pre-Deployment

- [ ] Python 3.8+ installed
- [ ] pip package manager available
- [ ] Git (optional, for version control)
- [ ] Google account with Gmail and Calendar access

## File Copy

Copy these files to your new project:

### Agent Files
- [ ] `agents/__init__.py`
- [ ] `agents/google_agent.py`
- [ ] `agents/GOOGLE_AGENT_GUIDE.md`
- [ ] `agents/README_PORTABLE.md`
- [ ] `agents/DEPLOYMENT_CHECKLIST.md`

### Tool Files
- [ ] `tools/__init__.py`
- [ ] `tools/base.py`
- [ ] `tools/gmail.py`
- [ ] `tools/calendar.py`
- [ ] `tools/gmail_auth.py`

### Optional (for testing)
- [ ] `test_google_agent.py`

## Google Cloud Setup

- [ ] Create Google Cloud project (https://console.cloud.google.com/)
- [ ] Enable Gmail API
- [ ] Enable Google Calendar API
- [ ] Create OAuth 2.0 credentials (Desktop application type)
- [ ] Download credentials.json
- [ ] Place credentials.json in project root directory
- [ ] Verify credentials.json is in .gitignore (don't commit!)

## Python Environment

```bash
# Install required packages
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

- [ ] google-auth-oauthlib installed
- [ ] google-auth-httplib2 installed
- [ ] google-api-python-client installed

## First Run Authentication

```bash
# Test basic import
python -c "from agents import GoogleAgent; print('Success')"
```

First time you run an agent task:
- [ ] Browser window opens for Google auth
- [ ] You click "Allow" to authorize
- [ ] token.pickle is created (don't commit!)
- [ ] Subsequent runs use cached token

If "Insufficient authentication scopes" error appears:
```bash
rm token.pickle
python your_script.py  # This will re-authenticate
```

- [ ] Initial authentication successful
- [ ] token.pickle created
- [ ] Agent can access Gmail API
- [ ] Agent can access Calendar API

## Verification Tests

```bash
# Run basic tests
python test_google_agent.py
```

### Expected Results

**Test 1: List Available Tools**
- [ ] Shows 8 tools (4 Gmail + 4 Calendar)
- [ ] All tool descriptions display

**Test 2: Agent Status**
- [ ] Status shows "active"
- [ ] 8 available tools listed

**Test 3: Sample Tasks**
- [ ] Task executes (may show False due to logging, but results are returned)
- [ ] Email counts are returned
- [ ] Calendar events are returned

**Test 4: Export**
- [ ] agent_history.json file created
- [ ] File contains task execution records

## Configuration

### Optional: Verbose Logging

```python
# Enable detailed execution logs
agent = GoogleAgent(verbose=True)

# Disable for production
agent = GoogleAgent(verbose=False)
```

- [ ] Decide on verbose mode for your use case
- [ ] Update code as needed

### Optional: Custom Tools

If adding custom tools:
- [ ] Create tool class inheriting from Tool
- [ ] Implement name, description, run()
- [ ] Register with agent: `agent.add_custom_tool()`

## Security Checklist

- [ ] credentials.json is in .gitignore
- [ ] token.pickle is in .gitignore
- [ ] Never commit authentication files
- [ ] Restrict file permissions (if on shared system)
- [ ] Review Google Cloud IAM permissions

## Integration Checklist

### Basic Integration

```python
from agents import GoogleAgent

agent = GoogleAgent()
result = agent.execute_task("Check inbox")
```

- [ ] Agent imports successfully
- [ ] Can create agent instance
- [ ] Can execute tasks
- [ ] Results are returned correctly

### Task Integration

- [ ] Email counting works
- [ ] Calendar queries work
- [ ] Parameter extraction works
- [ ] Tool selection works

### History & Export

- [ ] Task history is recorded
- [ ] History export works
- [ ] Can retrieve agent status
- [ ] Metrics are calculated

## Production Readiness

### Error Handling

```python
try:
    result = agent.execute_task("task")
    if result['ok']:
        # Process result
    else:
        # Handle error
except Exception as e:
    # Handle exception
```

- [ ] Implement try/except blocks
- [ ] Handle task failures gracefully
- [ ] Log errors appropriately
- [ ] Provide user feedback

### Performance

- [ ] Agent initialized once (reused across tasks)
- [ ] Long-running tasks have timeouts
- [ ] History pruned if needed
- [ ] Memory usage monitored

### Monitoring

- [ ] Task history exported regularly
- [ ] Success rates tracked
- [ ] Failures logged
- [ ] Alerts configured (if applicable)

## Documentation

- [ ] README_PORTABLE.md reviewed
- [ ] GOOGLE_AGENT_GUIDE.md reviewed
- [ ] Code comments added (if customized)
- [ ] Usage examples documented
- [ ] Setup instructions documented

## Testing Scenarios

### Email Tasks

```python
# Test 1: Unread count
result = agent.execute_task("How many unread emails?")
assert result['ok'] or result['result'] is not None

# Test 2: Sender search
result = agent.execute_task("Count emails from test@example.com")
assert 'count' in result['result']

# Test 3: Folder filtering
result = agent.execute_task("Unread in inbox?")
assert result['result'] is not None
```

- [ ] Email counting works
- [ ] Sender filtering works
- [ ] Folder filtering works
- [ ] Result format correct

### Calendar Tasks

```python
# Test 1: List calendars
result = agent.execute_task("List all calendars")
assert 'calendars' in result['result']

# Test 2: Today's events
result = agent.execute_task("What events today?")
assert 'events' in result['result']

# Test 3: Week schedule
result = agent.execute_task("What's on my calendar this week?")
assert result['ok'] or result['result'] is not None
```

- [ ] Calendar listing works
- [ ] Today's events show
- [ ] Week schedule works
- [ ] Date range filtering works

### Agent Features

```python
# Test 1: Tool listing
tools = agent.list_available_tools()
assert len(tools) >= 8

# Test 2: Status reporting
status = agent.get_agent_status()
assert status['status'] == 'active'

# Test 3: History tracking
history = agent.get_task_history()
assert len(history) >= 0
```

- [ ] Tool listing works
- [ ] Status reporting works
- [ ] History tracking works

## Deployment to Other Projects

### Quick Copy Template

```bash
# In new project directory
mkdir -p agents tools
cp /path/to/google-agent/agents/* agents/
cp /path/to/google-agent/tools/* tools/
cp /path/to/google-agent/credentials.json .
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

- [ ] All files copied
- [ ] credentials.json placed
- [ ] Dependencies installed
- [ ] First test successful

### Version Control

```bash
# Add to .gitignore
echo "credentials.json" >> .gitignore
echo "token.pickle" >> .gitignore
echo "__pycache__/" >> .gitignore
```

- [ ] .gitignore updated
- [ ] No auth files committed
- [ ] Clean git history

## Post-Deployment

- [ ] Agent is working in production
- [ ] Monitoring is active
- [ ] Documentation is accessible
- [ ] Team knows how to use agent
- [ ] Backup/recovery plan exists

## Troubleshooting Quick Links

If issues occur:

1. **Authentication problems**
   - Delete token.pickle and re-authenticate
   - Check credentials.json exists
   - Verify Google Cloud APIs enabled

2. **Tool not finding emails/events**
   - Check query syntax is correct
   - Verify agent parameter extraction
   - Enable verbose mode for debugging

3. **Performance issues**
   - Monitor task history size
   - Check API rate limits
   - Consider caching results

4. **New environments**
   - Always delete token.pickle when moving
   - Re-authenticate in new environment
   - Verify credentials.json present

## Maintenance

### Regular Tasks

- [ ] Review task history monthly
- [ ] Monitor success rates
- [ ] Update documentation as needed
- [ ] Check for API changes
- [ ] Rotate credentials annually

### Upgrades

When updating agent:
- [ ] Test in staging first
- [ ] Backup task history
- [ ] Plan maintenance window
- [ ] Document changes

## Completion

- [ ] All checkboxes complete
- [ ] Agent tested and working
- [ ] Documentation reviewed
- [ ] Team trained
- [ ] Monitoring active

**Date Deployed:** _______________

**Deployed By:** _______________

**Notes:**
_______________________________________________
_______________________________________________

---

## Quick Reference

### File Locations
- Agent: `agents/google_agent.py`
- Tools: `tools/*.py`
- Config: `credentials.json` (project root)
- Auth Cache: `token.pickle` (auto-created)

### Import Statement
```python
from agents import GoogleAgent
```

### Basic Usage
```python
agent = GoogleAgent()
result = agent.execute_task("your task here")
```

### Test Command
```bash
python test_google_agent.py
```

### Help
- Guide: `agents/GOOGLE_AGENT_GUIDE.md`
- Portable: `agents/README_PORTABLE.md`
- This: `agents/DEPLOYMENT_CHECKLIST.md`
