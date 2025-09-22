"""Utilities for the Research API."""

import json
from typing import (
    AsyncGenerator,
    Optional,
    Dict,
)

import httpx
from thesis_py.research.events.event import Event

from thesis_py.research.events.serialization.event_utils import (
    event_from_dict as parse_research_event,
)


async def async_stream_sse_events(
    response: httpx.Response,
) -> AsyncGenerator[Event, None]:
    """Stream SSE events from an httpx Response.

    Args:
        response: The async streaming response object.

    Yields:
        Parsed Event objects.
    """

    # Buffer to handle chunked JSON
    buffer = ""

    async for chunk in response.aiter_text():
        buffer += chunk

        # Process complete JSON objects from buffer
        while buffer:
            try:
                # Try to decode JSON from the buffer
                decoder = json.JSONDecoder()
                event, idx = decoder.raw_decode(buffer)

                # Successfully parsed a JSON object
                try:
                    if "type" in event and event["type"] == "oh_event":
                        event = event["data"]
                        event = parse_research_event(event)
                        yield event
                    elif (
                        "type" in event
                        and event["type"] == "connection"
                        and "status" in event
                        and event["status"] == "connected"
                    ):
                        print(
                            f"\n✅ Stream connected successfully. Waiting for events from Thesis.io..."
                        )
                except ValueError:
                    continue
                except Exception as e:
                    print(f"❌ Error parsing event: {e}")

                # Remove processed JSON from buffer
                buffer = buffer[idx:].lstrip()

                if isinstance(event, Event):
                    continue
                if isinstance(event, dict):
                    # Check for completion
                    if event.get("type") == "completion":
                        status = event.get("status", "finished")
                        if status == "cancelled":
                            print(
                                f"\n🚫 Stream cancelled: {event.get('message', 'Stream was cancelled')}"
                            )
                        elif status == "finished":
                            print(
                                f"\n✅ Stream completed successfully with message: {event.get('message', 'Unknown message')}"
                            )
                        else:
                            print(
                                f"\n🏁 Stream ended with status '{status}': {event.get('message', 'No message')}"
                            )
                        return
                    if event.get("type") == "error":
                        print(
                            f"\n❌ Stream ended with error: {event.get('message', 'Unknown error')}"
                        )
                        raise ValueError(
                            f"❌ Stream ended with error: {event.get('message', 'Unknown error')}"
                        )

            except json.JSONDecodeError:
                # Incomplete JSON in buffer, wait for more data
                break


def build_pagination_params(
    offset: Optional[int] = None, limit: Optional[int] = None
) -> Dict[str, str]:
    """Build pagination parameters for list requests.

    Args:
        offset: Pagination offset.
        limit: Maximum number of results.

    Returns:
        Dictionary of query parameters.
    """
    params = {}
    if offset is not None:
        params["offset"] = offset
    if limit is not None:
        params["limit"] = str(limit)
    return params
