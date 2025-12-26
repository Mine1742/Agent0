"""Google API authentication and credential management.

This module handles:
- OAuth 2.0 authentication flow
- Credential storage and refresh
- Gmail and Calendar API service initialization
"""
from __future__ import annotations

import os
import pickle
import pathlib
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar",
]

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.pickle"


def get_gmail_service(credentials_path: Optional[str] = None):
    """Get an authenticated Gmail API service.

    Args:
        credentials_path: Path to credentials.json file (optional)

    Returns:
        Authenticated Gmail API service object

    Raises:
        FileNotFoundError: If credentials.json not found and no valid token exists
    """
    from googleapiclient.discovery import build

    token_file = pathlib.Path(TOKEN_FILE)
    creds = None

    # Load cached token if it exists
    if token_file.exists():
        with open(token_file, "rb") as f:
            creds = pickle.load(f)

    # Refresh token if needed
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds or not creds.valid:
        # Need to authenticate
        cred_file = credentials_path or CREDENTIALS_FILE

        if not os.path.exists(cred_file):
            raise FileNotFoundError(
                f"credentials.json not found at {cred_file}. "
                "Please download it from Google Cloud Console and place it in the project root."
            )

        flow = InstalledAppFlow.from_client_secrets_file(cred_file, SCOPES)
        creds = flow.run_local_server(port=0)

        # Save the token for future use
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return build("gmail", "v1", credentials=creds)


def get_calendar_service(credentials_path: Optional[str] = None):
    """Get an authenticated Google Calendar API service.

    Args:
        credentials_path: Path to credentials.json file (optional)

    Returns:
        Authenticated Calendar API service object

    Raises:
        FileNotFoundError: If credentials.json not found and no valid token exists
    """
    from googleapiclient.discovery import build

    token_file = pathlib.Path(TOKEN_FILE)
    creds = None

    # Load cached token if it exists
    if token_file.exists():
        with open(token_file, "rb") as f:
            creds = pickle.load(f)

    # Refresh token if needed
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds or not creds.valid:
        # Need to authenticate
        cred_file = credentials_path or CREDENTIALS_FILE

        if not os.path.exists(cred_file):
            raise FileNotFoundError(
                f"credentials.json not found at {cred_file}. "
                "Please download it from Google Cloud Console and place it in the project root."
            )

        flow = InstalledAppFlow.from_client_secrets_file(cred_file, SCOPES)
        creds = flow.run_local_server(port=0)

        # Save the token for future use
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return build("calendar", "v3", credentials=creds)


def clear_cached_token():
    """Clear cached credentials. Call this to force re-authentication."""
    token_file = pathlib.Path(TOKEN_FILE)
    if token_file.exists():
        token_file.unlink()
