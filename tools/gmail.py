"""Gmail query and interaction tools for the agent.

These tools allow the agent to:
- Search and query emails
- Read email content
- Send emails
- List Gmail labels
"""
from __future__ import annotations

import base64
from typing import Any, Dict, Optional
from email.mime.text import MIMEText

from .base import Tool
from .gmail_auth import get_gmail_service


class QueryGmail(Tool):
    """Search and query emails from Gmail."""

    name = "query_gmail"
    description = (
        "Search emails in Gmail by query string. "
        "Supports: 'from:user@example.com', 'subject:keyword', 'is:unread', "
        "'newer_than:1d' (today), 'older_than:7d', 'label:inbox', and combinations like 'from:user is:unread'. "
        "Optional: max_results (1-100, default 10) to retrieve more matching emails. "
        "Use count_all=True to count all matching emails (accurate but slower), or count_only=True for API estimate."
    )

    def run(self, query: str, max_results: int = 10, count_only: bool = False, count_all: bool = False) -> Dict[str, Any]:
        """Search emails matching the query.

        Args:
            query: Gmail search query string. Use 'newer_than:1d' for today's emails.
            max_results: Maximum number of results to return (1-100, default 10)
            count_only: If True, return API's resultSizeEstimate (fast but may be inaccurate)
            count_all: If True, count all matching emails by paginating (accurate but slower)

        Returns:
            Dictionary with search results, metadata, and count information
        """
        try:
            service = get_gmail_service()

            # For count_all, paginate through all results to get accurate count
            if count_all:
                all_ids = []
                next_page_token = None

                while True:
                    results = service.users().messages().list(
                        userId="me",
                        q=query,
                        maxResults=100,
                        pageToken=next_page_token,
                    ).execute()

                    messages = results.get("messages", [])
                    all_ids.extend([m["id"] for m in messages])

                    next_page_token = results.get("nextPageToken")
                    if not next_page_token:
                        break

                return {
                    "ok": True,
                    "query": query,
                    "count": len(all_ids),
                    "summary": f"Found {len(all_ids)} emails matching query (accurate count)",
                }

            # For count_only, use API estimate (faster, may be inaccurate)
            if count_only:
                results = service.users().messages().list(
                    userId="me",
                    q=query,
                    maxResults=1,
                ).execute()

                estimate = results.get("resultSizeEstimate", 0)

                return {
                    "ok": True,
                    "query": query,
                    "count": estimate,
                    "count_note": "This is an API estimate and may be inaccurate. Use count_all=True for accurate count.",
                    "summary": f"Found {estimate} emails (API estimate)",
                }

            # Validate and constrain max_results
            if not isinstance(max_results, int) or max_results < 1:
                max_results = 10
            if max_results > 100:
                max_results = 100

            results = service.users().messages().list(
                userId="me",
                q=query,
                maxResults=max_results,
            ).execute()

            messages = results.get("messages", [])
            total = results.get("resultSizeEstimate", 0)

            # Get minimal info for each message
            email_summaries = []
            unique_senders = set()
            for msg in messages:
                try:
                    message = service.users().messages().get(
                        userId="me",
                        id=msg["id"],
                        format="metadata",
                        metadataHeaders=["From", "To", "Subject", "Date"],
                    ).execute()

                    headers = message["payload"]["headers"]
                    header_dict = {h["name"]: h["value"] for h in headers}
                    from_addr = header_dict.get("From", "[Unknown]")
                    unique_senders.add(from_addr)

                    email_summaries.append({
                        "id": msg["id"],
                        "subject": header_dict.get("Subject", "[No Subject]"),
                        "from": from_addr,
                        "date": header_dict.get("Date", "[Unknown]"),
                    })
                except Exception:
                    continue

            returned = len(email_summaries)

            # Build clear summary message
            summary = f"Found {returned} emails"
            if returned < total:
                summary += f" (showing {returned} of {total} total matching emails)"
            else:
                summary += f" total"

            # Check for API estimate inconsistency
            # Gmail's API resultSizeEstimate can be inflated; flag large discrepancies
            discrepancy_warning = None
            if returned > 0 and total > returned * 2:
                discrepancy_warning = (
                    f"Note: API reports {total} total results but only {returned} were retrieved. "
                    f"Gmail's API estimate may be inflated. For accurate counts, verify in Gmail's web UI."
                )

            return {
                "ok": True,
                "query": query,
                "total_results": total,
                "returned": returned,
                "summary": summary,
                "unique_senders": list(unique_senders),
                "discrepancy_warning": discrepancy_warning,
                "emails": email_summaries,
            }

        except FileNotFoundError as e:
            return {"ok": False, "error": str(e)}
        except Exception as e:
            return {"ok": False, "error": f"Gmail query failed: {e}"}


class ReadEmail(Tool):
    """Read the full content of a specific email."""

    name = "read_email"
    description = "Read the full content of an email by its ID. Get the ID from query_gmail first."

    def run(self, message_id: str) -> Dict[str, Any]:
        """Get full email content.

        Args:
            message_id: Gmail message ID

        Returns:
            Dictionary with full email content
        """
        try:
            service = get_gmail_service()
            message = service.users().messages().get(
                userId="me",
                id=message_id,
                format="full",
            ).execute()

            headers = message["payload"]["headers"]
            header_dict = {h["name"]: h["value"] for h in headers}

            # Extract body
            body_text = ""
            if "parts" in message["payload"]:
                # Multipart message
                for part in message["payload"]["parts"]:
                    if part["mimeType"] == "text/plain":
                        if "data" in part["body"]:
                            body_text = base64.urlsafe_b64decode(
                                part["body"]["data"]
                            ).decode("utf-8")
                        break
            else:
                # Simple message
                if "body" in message["payload"] and "data" in message["payload"]["body"]:
                    body_text = base64.urlsafe_b64decode(
                        message["payload"]["body"]["data"]
                    ).decode("utf-8")

            return {
                "ok": True,
                "id": message_id,
                "from": header_dict.get("From", "[Unknown]"),
                "to": header_dict.get("To", "[Unknown]"),
                "subject": header_dict.get("Subject", "[No Subject]"),
                "date": header_dict.get("Date", "[Unknown]"),
                "body": body_text,
            }

        except FileNotFoundError as e:
            return {"ok": False, "error": str(e)}
        except Exception as e:
            return {"ok": False, "error": f"Failed to read email: {e}"}


class SendEmail(Tool):
    """Send an email via Gmail."""

    name = "send_email"
    description = "Send an email. Use carefully - sent emails cannot be unsent."

    def run(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        """Send an email.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text

        Returns:
            Dictionary with send status
        """
        try:
            service = get_gmail_service()

            # Create message with proper MIME headers
            # IMPORTANT: Must include all headers in this order for Gmail to parse correctly
            message_str = (
                f"To: {to}\r\n"
                f"Subject: {subject}\r\n"
                f"Content-Type: text/plain; charset=\"UTF-8\"\r\n"
                f"\r\n"
                f"{body}"
            )

            # Encode as bytes and then base64
            raw_message = base64.urlsafe_b64encode(message_str.encode("utf-8")).decode()
            send_message = {"raw": raw_message}

            result = service.users().messages().send(
                userId="me",
                body=send_message,
            ).execute()

            return {
                "ok": True,
                "message_id": result["id"],
                "to": to,
                "subject": subject,
                "status": "sent successfully",
            }

        except FileNotFoundError as e:
            return {"ok": False, "error": str(e)}
        except Exception as e:
            return {"ok": False, "error": f"Failed to send email: {e}"}


class ListGmailLabels(Tool):
    """List all Gmail labels/folders."""

    name = "list_gmail_labels"
    description = "List all available Gmail labels (folders/categories)"

    def run(self) -> Dict[str, Any]:
        """Get all Gmail labels.

        Returns:
            Dictionary with list of labels
        """
        try:
            service = get_gmail_service()
            results = service.users().labels().list(userId="me").execute()

            labels = results.get("labels", [])
            label_list = [
                {"id": label["id"], "name": label["name"]}
                for label in labels
            ]

            return {
                "ok": True,
                "total": len(label_list),
                "labels": label_list,
            }

        except FileNotFoundError as e:
            return {"ok": False, "error": str(e)}
        except Exception as e:
            return {"ok": False, "error": f"Failed to list labels: {e}"}
