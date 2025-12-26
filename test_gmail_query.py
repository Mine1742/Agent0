#!/usr/bin/env python3
"""Debug script to test Gmail API queries directly."""

from tools.gmail_auth import get_gmail_service

def test_queries():
    """Test the three problem queries."""
    service = get_gmail_service()

    queries = [
        ("is:unread", "Unread emails"),
        ("from:caitrinconroy@gmail.com", "Emails from caitrinconroy@gmail.com"),
        ("from:mine1742@gmail.com", "Emails from mine1742@gmail.com"),
    ]

    for query, description in queries:
        print(f"\n{'='*60}")
        print(f"Testing: {description}")
        print(f"Query: '{query}'")
        print('='*60)

        try:
            # Make the API call
            results = service.users().messages().list(
                userId="me",
                q=query,
                maxResults=1,
            ).execute()

            # Print what we get back
            print(f"Full API response:")
            print(f"  resultSizeEstimate: {results.get('resultSizeEstimate', 0)}")
            print(f"  messages returned: {len(results.get('messages', []))}")
            print(f"  Raw response keys: {results.keys()}")

            # If there's a message, show its details
            if results.get('messages'):
                msg = results['messages'][0]
                print(f"\nFirst message ID: {msg.get('id')}")
                print(f"First message threadId: {msg.get('threadId')}")

        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    test_queries()
