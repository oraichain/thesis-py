from __future__ import annotations

import os
import json
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Union,
    AsyncGenerator,
    Generator,
)

import httpx
import requests
from thesis_py.api_schema import (
    ConversationCreateResponse,
    CreateNewConversationIntegrationRequest,
    ConversationDetailResponse,
    JoinConversationIntegrationRequest,
    SpaceListResponse,
    SpaceDetailResponse,
    SpaceSectionsResponse,
)
from thesis_py.research.events.event import Event
from thesis_py.research.base import ResearchBaseClient
from thesis_py.research.utils import async_stream_sse_events, build_pagination_params


class Thesis:
    """A client for interacting with Thesis API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = os.getenv("THESIS_BASE_URL", "https://app-be.thesis.io"),
    ):
        """Initialize the Thesis client with the provided API key and optional base URL and user agent.

        Args:
            api_key (str): The API key for authenticating with the Thesis API.
            base_url (str, optional): The base URL for the Thesis API. Defaults to "https://app-be.thesis.io".
        """

        self.base_url = base_url
        self.client = ResearchBaseClient(api_key=api_key, base_url=base_url)

    # Conversation APIs
    def create_conversation(
        self,
        request: CreateNewConversationIntegrationRequest,
    ) -> ConversationCreateResponse:
        """Perform a search with a prompt-engineered query to retrieve relevant results.

        Args:
            request: The request object for creating a new conversation.

        Returns:
            Conversation: The response containing the conversation id.
        """
        data = request.model_dump_json()
        response = self.client.request(
            method="POST",
            endpoint="/conversations",
            data=data,
        )
        if response.status_code != 200 and response.status_code != 201:
            raise requests.HTTPError(response=response)

        return ConversationCreateResponse(**response.json())

    async def create_conversation_async(
        self,
        request: CreateNewConversationIntegrationRequest,
    ) -> ConversationCreateResponse:

        response = await self.client.async_request(
            method="POST",
            endpoint="/conversations",
            data=request.model_dump_json(),
        )
        if response.status_code != 200 and response.status_code != 201:
            raise requests.HTTPError(response=response)

        return ConversationCreateResponse(**response.json())

    def get_conversation_by_id(
        self,
        conversation_id: str,
    ) -> ConversationDetailResponse:
        response = self.client.request(
            method="GET",
            endpoint=f"/conversations/{conversation_id}",
        )
        if response.status_code != 200 and response.status_code != 201:
            raise requests.HTTPError(response=response)
        return ConversationDetailResponse(**response.json())

    async def get_conversation_by_id_async(
        self,
        conversation_id: str,
    ) -> ConversationDetailResponse:
        response = await self.client.async_request(
            method="GET",
            endpoint=f"/conversations/{conversation_id}",
        )
        if response.status_code != 200 and response.status_code != 201:
            raise requests.HTTPError(response=response)
        return ConversationDetailResponse(**response.json())

    async def join_conversation(
        self,
        request: JoinConversationIntegrationRequest,
    ) -> AsyncGenerator[Event, None]:
        try:
            response = await self.client.async_request(
                method="POST",
                endpoint="/conversations/join-conversation",
                data=request.model_dump(),
                params={"stream": "true"},
            )
            if response.status_code != 200 and response.status_code != 201:
                error_text = await response.aread()
                raise ValueError(f"❌ Error reading response: {error_text.decode()}")

            async for event in async_stream_sse_events(response):
                yield event

        except httpx.ConnectError:
            print(f"❌ Failed to connect to {self.base_url}")
            print("Make sure your FastAPI server is running!")
        except httpx.TimeoutException:
            print("⏰ Request timed out")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

    # Space APIs
    def get_spaces(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> SpaceListResponse:
        response = self.client.request(
            method="GET",
            endpoint="/spaces",
            params=build_pagination_params(limit, offset),
        )
        if response.status_code != 200 and response.status_code != 201:
            raise requests.HTTPError(response=response)
        return SpaceListResponse(**response.json())

    async def get_spaces_async(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> SpaceListResponse:
        response = await self.client.async_request(
            method="GET",
            endpoint="/spaces",
            params=build_pagination_params(limit, offset),
        )
        if response.status_code != 200 and response.status_code != 201:
            raise requests.HTTPError(response=response)
        return SpaceListResponse(**response.json())

    def get_space_by_id(
        self,
        space_id: str,
    ) -> SpaceDetailResponse:
        response = self.client.request(
            method="GET",
            endpoint=f"/spaces/{space_id}",
        )
        if response.status_code != 200 and response.status_code != 201:
            raise requests.HTTPError(response=response)
        return SpaceDetailResponse(**response.json())

    async def get_space_by_id_async(
        self,
        space_id: str,
    ) -> SpaceDetailResponse:
        response = await self.client.async_request(
            method="GET",
            endpoint=f"/spaces/{space_id}",
        )
        if response.status_code != 200 and response.status_code != 201:
            raise requests.HTTPError(response=response)
        return SpaceDetailResponse(**response.json())

    def get_space_sections(
        self,
        space_id: str,
    ) -> SpaceSectionsResponse:
        response = self.client.request(
            method="GET",
            endpoint=f"/spaces/{space_id}/sections",
        )
        if response.status_code != 200 and response.status_code != 201:
            raise requests.HTTPError(response=response)
        return SpaceSectionsResponse(**response.json())

    async def get_space_sections_async(
        self,
        space_id: str,
    ) -> SpaceSectionsResponse:
        response = await self.client.async_request(
            method="GET",
            endpoint=f"/spaces/{space_id}/sections",
        )
        if response.status_code != 200 and response.status_code != 201:
            raise requests.HTTPError(response=response)
        return SpaceSectionsResponse(**response.json())
