"""Google Calendar query and interaction tools.

These tools allow the agent to:
- List calendars
- Query events
- Create events
- Update events
- Delete events
"""
from __future__ import annotations

from typing import Any, Dict, Optional
from datetime import datetime, timedelta

from .base import Tool
from .gmail_auth import get_calendar_service


class ListCalendars(Tool):
    """List all available calendars."""

    name = "list_calendars"
    description = "List all available Google Calendars"

    def run(self) -> Dict[str, Any]:
        """Get all calendars.

        Returns:
            Dictionary with list of calendars
        """
        try:
            service = get_calendar_service()
            results = service.calendarList().list().execute()

            calendars = results.get("items", [])
            calendar_list = [
                {
                    "id": cal["id"],
                    "summary": cal.get("summary", "[Unnamed]"),
                    "primary": cal.get("primary", False),
                    "timezone": cal.get("timeZone", "UTC"),
                }
                for cal in calendars
            ]

            return {
                "ok": True,
                "total": len(calendar_list),
                "calendars": calendar_list,
            }

        except FileNotFoundError as e:
            return {"ok": False, "error": str(e)}
        except Exception as e:
            return {"ok": False, "error": f"Failed to list calendars: {e}"}


class QueryEvents(Tool):
    """Search and query events from a calendar."""

    name = "query_events"
    description = (
        "Query events from a Google Calendar. "
        "Can filter by calendar ID, time range, and search text. "
        "Default calendar is primary. "
        "Use time_min/time_max for date ranges (ISO 8601 format like '2025-12-26')"
    )

    def run(
        self,
        calendar_id: str = "primary",
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        search_text: Optional[str] = None,
        max_results: int = 10,
    ) -> Dict[str, Any]:
        """Query events from a calendar.

        Args:
            calendar_id: Calendar ID (default: 'primary' for main calendar)
            time_min: Start time for range (ISO 8601, e.g., '2025-12-26')
            time_max: End time for range (ISO 8601, e.g., '2025-12-31')
            search_text: Text to search for in event titles
            max_results: Maximum number of events to return (1-100, default 10)

        Returns:
            Dictionary with matching events
        """
        try:
            service = get_calendar_service()

            # Validate max_results
            if not isinstance(max_results, int) or max_results < 1:
                max_results = 10
            if max_results > 100:
                max_results = 100

            # Build the request
            kwargs = {
                "calendarId": calendar_id,
                "maxResults": max_results,
                "singleEvents": True,
                "orderBy": "startTime",
            }

            # Add time range if provided
            if time_min:
                # Convert date string to RFC 3339 format if needed
                if "T" not in time_min:
                    time_min = f"{time_min}T00:00:00Z"
                elif not time_min.endswith("Z"):
                    time_min = f"{time_min}Z"
                kwargs["timeMin"] = time_min

            if time_max:
                # Convert date string to RFC 3339 format if needed
                if "T" not in time_max:
                    time_max = f"{time_max}T23:59:59Z"
                elif not time_max.endswith("Z"):
                    time_max = f"{time_max}Z"
                kwargs["timeMax"] = time_max

            # Add search text if provided
            if search_text:
                kwargs["q"] = search_text

            results = service.events().list(**kwargs).execute()

            events = results.get("items", [])
            event_summaries = []

            for event in events:
                start = event.get("start", {})
                end = event.get("end", {})

                event_summaries.append({
                    "id": event.get("id"),
                    "summary": event.get("summary", "[No Title]"),
                    "start": start.get("dateTime") or start.get("date"),
                    "end": end.get("dateTime") or end.get("date"),
                    "description": event.get("description", ""),
                    "location": event.get("location", ""),
                })

            summary = f"Found {len(event_summaries)} events"
            if len(event_summaries) < max_results:
                summary += " total"
            else:
                summary += f" (showing {len(event_summaries)} of possibly more)"

            return {
                "ok": True,
                "calendar_id": calendar_id,
                "returned": len(event_summaries),
                "summary": summary,
                "events": event_summaries,
            }

        except FileNotFoundError as e:
            return {"ok": False, "error": str(e)}
        except Exception as e:
            return {"ok": False, "error": f"Failed to query events: {e}"}


class CreateEvent(Tool):
    """Create an event in a calendar."""

    name = "create_event"
    description = (
        "Create a new event in Google Calendar. "
        "Provide event title, start and end times. "
        "Times should be in ISO 8601 format (e.g., '2025-12-26T10:00:00') or date only (e.g., '2025-12-26')"
    )

    def run(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        calendar_id: str = "primary",
        description: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create an event.

        Args:
            summary: Event title
            start_time: Start time (ISO 8601)
            end_time: End time (ISO 8601)
            calendar_id: Calendar ID (default: 'primary')
            description: Event description (optional)
            location: Event location (optional)

        Returns:
            Dictionary with created event details
        """
        try:
            service = get_calendar_service()

            # Parse and format times
            start = self._parse_time(start_time)
            end = self._parse_time(end_time)

            event = {
                "summary": summary,
                "start": start,
                "end": end,
            }

            if description:
                event["description"] = description

            if location:
                event["location"] = location

            result = service.events().insert(
                calendarId=calendar_id,
                body=event,
            ).execute()

            return {
                "ok": True,
                "event_id": result.get("id"),
                "summary": result.get("summary"),
                "start": result.get("start", {}).get("dateTime") or result.get("start", {}).get("date"),
                "end": result.get("end", {}).get("dateTime") or result.get("end", {}).get("date"),
                "status": "created",
            }

        except FileNotFoundError as e:
            return {"ok": False, "error": str(e)}
        except Exception as e:
            return {"ok": False, "error": f"Failed to create event: {e}"}

    @staticmethod
    def _parse_time(time_str: str) -> Dict[str, str]:
        """Parse time string and return Calendar API format."""
        # If it's a date-only string (YYYY-MM-DD)
        if len(time_str) == 10 and time_str.count("-") == 2:
            return {"date": time_str}

        # Otherwise treat as datetime
        # Ensure it has Z suffix for UTC
        if not time_str.endswith("Z"):
            if "T" in time_str:
                time_str = f"{time_str}Z"
            else:
                time_str = f"{time_str}T00:00:00Z"

        return {"dateTime": time_str}


class DeleteEvent(Tool):
    """Delete an event from a calendar."""

    name = "delete_event"
    description = "Delete an event from a Google Calendar by its ID"

    def run(
        self,
        event_id: str,
        calendar_id: str = "primary",
    ) -> Dict[str, Any]:
        """Delete an event.

        Args:
            event_id: Event ID
            calendar_id: Calendar ID (default: 'primary')

        Returns:
            Dictionary with deletion status
        """
        try:
            service = get_calendar_service()

            service.events().delete(
                calendarId=calendar_id,
                eventId=event_id,
            ).execute()

            return {
                "ok": True,
                "event_id": event_id,
                "status": "deleted",
            }

        except FileNotFoundError as e:
            return {"ok": False, "error": str(e)}
        except Exception as e:
            return {"ok": False, "error": f"Failed to delete event: {e}"}
