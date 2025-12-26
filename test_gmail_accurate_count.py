#!/usr/bin/env python3
"""Get accurate email counts by retrieving all pages."""

from tools.gmail_auth import get_gmail_service

def get_accurate_count(query: str, description: str):
    """Get actual count by paginating through all results."""
    service = get_gmail_service()

    print(f"\n{'='*60}")
    print(f"Counting: {description}")
    print(f"Query: '{query}'")
    print('='*60)

    all_message_ids = []
    next_page_token = None
    page_count = 0

    try:
        while True:
            page_count += 1
            results = service.users().messages().list(
                userId="me",
                q=query,
                maxResults=100,
                pageToken=next_page_token,
            ).execute()

            messages = results.get("messages", [])
            all_message_ids.extend([m["id"] for m in messages])

            estimate = results.get("resultSizeEstimate", 0)
            print(f"Page {page_count}: Retrieved {len(messages)} messages")
            print(f"  API estimate: {estimate}")
            print(f"  Total so far: {len(all_message_ids)}")

            next_page_token = results.get("nextPageToken")
            if not next_page_token:
                break

        print(f"\nFinal Results:")
        print(f"  API estimate: {estimate}")
        print(f"  Actual count: {len(all_message_ids)}")
        print(f"  Pages retrieved: {page_count}")

        return len(all_message_ids), estimate

    except Exception as e:
        print(f"ERROR: {e}")
        return None, None

if __name__ == "__main__":
    queries = [
        ("is:unread", "Unread emails"),
        ("from:caitrinconroy@gmail.com", "Emails from caitrinconroy@gmail.com"),
        ("from:mine1742@gmail.com", "Emails from mine1742@gmail.com"),
    ]

    results = {}
    for query, description in queries:
        actual, estimate = get_accurate_count(query, description)
        results[description] = {"actual": actual, "estimate": estimate}

    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    for desc, counts in results.items():
        if counts["actual"] is not None:
            print(f"{desc}:")
            print(f"  API estimate: {counts['estimate']}")
            print(f"  Actual count: {counts['actual']}")
            print(f"  Discrepancy: {counts['estimate'] - counts['actual']}")
