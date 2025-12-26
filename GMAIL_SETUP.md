# Gmail Tool Setup Guide

This guide explains how to set up OAuth 2.0 authentication for the Gmail tools in your agent.

## Prerequisites

1. **Python packages installed:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Google Account** - You'll need a Gmail account to authenticate with.

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the Gmail API:
   - Search for "Gmail API"
   - Click "Enable"

## Step 2: Create OAuth 2.0 Credentials

### A) Configure OAuth Consent Screen First

1. Go to **APIs & Services** → **OAuth Consent Screen**
2. Select **User Type: External**
3. Fill in the form with:
   - **App name**: "First Project Gmail Agent"
   - **User support email**: Your email
   - **Developer contact**: Your email
4. On the **Scopes** step, add these:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.modify`
5. Continue through and save

### B) Add Yourself as a Test User (IMPORTANT!)

6. Back on **OAuth Consent Screen** page
7. Scroll down to **"Test users"** section
8. Click **"+ Add users"**
9. Enter **your Gmail address**
10. Click **Save**

**This step is critical** - without it, you'll get a 403 error!

### C) Create Credentials

11. Go to **APIs & Services** → **Credentials**
12. Click **"+ Create Credentials"** → **"OAuth 2.0 Client ID"**
13. Choose **Desktop application**
14. Download the JSON file and save as `credentials.json` in project root

## Step 3: Run Your Agent

First time using Gmail tools:

```bash
python main.py --goal "List my Gmail labels"
```

The first time you use a Gmail tool, your browser will open asking you to authenticate with your Gmail account. This is safe—the credentials are stored locally in `token.pickle`.

## Available Gmail Tools

### 1. **query_gmail** - Search emails
```python
# Search unread emails from specific sender
query_gmail(query="from:john@example.com is:unread", max_results=10)

# Common query examples:
# - "is:unread" - Unread emails
# - "from:sender@example.com" - From specific person
# - "subject:meeting" - Subject contains text
# - "after:2024-01-01" - After date
# - "label:important" - With specific label
```

### 2. **read_email** - Read full email content
```python
# Get full content of an email (use message ID from query_gmail)
read_email(message_id="<message_id_from_query>")
```

### 3. **send_email** - Send an email
```python
# Send an email (use with caution!)
send_email(to="recipient@example.com", subject="Hello", body="Email content")
```

### 4. **list_gmail_labels** - List all Gmail folders/labels
```python
# List all available labels
list_gmail_labels()
```

## Example Agent Goals

```bash
# Search for unread emails
python main.py --goal "Find my unread emails from the last week"

# Read a specific email (you'll need to search first)
python main.py --goal "Search for emails from my boss and read the most recent one"

# Send email
python main.py --goal "Send a thank you email to john@example.com"

# List labels
python main.py --goal "What labels/folders do I have in Gmail?"
```

## Security & Privacy

- **token.pickle** - Contains your authenticated session. Keep this private.
- **credentials.json** - Contains your OAuth credentials. Keep this private.
- Neither file should be committed to version control.

Add to `.gitignore`:
```
token.pickle
credentials.json
```

## Troubleshooting

### "Error 403: access_denied"
**This is the most common issue!** Solution:

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → Your Project
2. Go to **APIs & Services** → **OAuth Consent Screen**
3. Scroll down to **"Test users"** section
4. Click **"+ Add users"**
5. Enter **your Gmail address**
6. Click **Save**
7. Delete `token.pickle` file in your project (to clear cache)
8. Try again: `python main.py --goal "List my Gmail labels"`

**Why this happens:** Google requires you to add yourself as a test user when the app is in "External" mode. This is a security feature.

### "credentials.json not found"
- Make sure you downloaded the file from Google Cloud Console
- Save it as `credentials.json` in the project root

### "Invalid credentials"
- Delete `token.pickle` to force re-authentication
- Or call `clear_cached_token()` from `tools.gmail_auth`

### "Gmail API not enabled"
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Search for "Gmail API"
- Make sure it's enabled (blue toggle)

## Revoking Access

To revoke the application's access to your Gmail:

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Find "First Project" in "Third-party apps & services"
3. Click to remove access

This will also delete the local `token.pickle` file on next authentication.

## Learning Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api/guides)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- [Gmail Search Query Syntax](https://support.google.com/mail/answer/7190?hl=en)
