"""Base client classes for the Research API."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

import httpx
import requests

import os
from dotenv import load_dotenv

load_dotenv()


class ResearchBaseClient:
    """Base client for synchronous Research API operations."""

    def __init__(self, base_url: str = "https://app-be.thesis.io", api_key: str = None):
        """Initialize the base client.

        Args:
            base_url: The base URL for the Thesis API.
            api_key: The API key for the Thesis API.
        """
        self.base_url = base_url
        self.base_path = "/api/v1/integration"
        if api_key is None:
            api_key = os.environ.get("THESIS_API_KEY")
            if api_key is None:
                raise ValueError(
                    "API key must be provided as an argument or in THESIS_API_KEY environment variable"
                )
        self.headers = {
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
        }
        self.complete_base_url = self.base_url + self.base_path
        self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        # this may only be a
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url, headers=self.headers, timeout=600
            )
        return self._client

    def request(
        self,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        method: str = "POST",
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Send a request to the Thesis API, optionally streaming if data['stream'] is True.

        Args:
            endpoint (str): The API endpoint (path).
            data (dict, optional): The JSON payload to send. Defaults to None.
            method (str, optional): The HTTP method to use. Defaults to "POST".
            params (Dict[str, Any], optional): Query parameters to include. Defaults to None.
            headers (Dict[str, str], optional): Additional headers to include in the request. Defaults to None.

        Returns:
            Union[dict, requests.Response]: If streaming, returns the Response object.
            Otherwise, returns the JSON-decoded response as a dict.

        Raises:
            ValueError: If the request fails (non-200 status code).
        """
        # Handle the case when data is a string
        if isinstance(data, str):
            # Use the string directly as the data payload
            json_data = data
        else:
            # Otherwise, serialize the dictionary to JSON if it exists
            json_data = json.dumps(data) if data else None

        # Check if we need streaming (either from data for POST or params for GET)
        needs_streaming = (data and isinstance(data, dict) and data.get("stream")) or (
            params and params.get("stream") == "true"
        )

        # Merge additional headers with existing headers
        request_headers = {**self.headers}
        if headers:
            request_headers.update(headers)

        dispatch_url = self.complete_base_url + endpoint
        if method.upper() == "GET":
            if needs_streaming:
                res = requests.get(
                    dispatch_url,
                    headers=request_headers,
                    params=params,
                    stream=True,
                )
                return res
            else:
                res = requests.get(
                    dispatch_url,
                    headers=request_headers,
                    params=params,
                )
        elif method.upper() == "POST":
            if needs_streaming:
                res = requests.post(
                    dispatch_url,
                    data=json_data,
                    headers=request_headers,
                    stream=True,
                )
                return res
            else:
                res = requests.post(
                    dispatch_url, data=json_data, headers=request_headers
                )
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        if res.status_code >= 400:
            raise ValueError(
                f"Request failed with status code {res.status_code}: {res.text}"
            )
        return res

    async def async_request(
        self,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        method: str = "POST",
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Send a request to the Thesis.io API, optionally streaming if data['stream'] is True.

        Args:
            endpoint (str): The API endpoint (path).
            data (dict, optional): The JSON payload to send.
            method (str, optional): The HTTP method to use. Defaults to "POST".
            params (dict, optional): Query parameters.
            headers (Dict[str, str], optional): Additional headers to include in the request. Defaults to None.

        Returns:
            Union[dict, httpx.Response]: If streaming, returns the Response object.
            Otherwise, returns the JSON-decoded response as a dict.

        Raises:
            ValueError: If the request fails (non-200 status code).
        """
        # Check if we need streaming (either from data for POST or params for GET)
        needs_streaming = (data and isinstance(data, dict) and data.get("stream")) or (
            params and params.get("stream") == "true"
        )

        # Merge additional headers with existing headers
        request_headers = {**self.headers}
        if headers:
            request_headers.update(headers)

        dispatch_url = self.complete_base_url + endpoint
        if isinstance(data, dict):
            data = json.dumps(data)

        if method.upper() == "GET":
            if needs_streaming:
                request = httpx.Request(
                    "GET",
                    dispatch_url,
                    params=params,
                    headers=request_headers,
                )
                res = await self.client.send(request, stream=True)
                return res
            else:
                res = await self.client.get(
                    dispatch_url, params=params, headers=request_headers
                )
        elif method.upper() == "POST":
            if needs_streaming:
                request = httpx.Request(
                    "POST", dispatch_url, data=data, headers=request_headers
                )
                res = await self.client.send(request, stream=True)
                return res
            else:
                res = await self.client.post(
                    dispatch_url, data=data, headers=request_headers
                )
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        if res.status_code != 200 and res.status_code != 201:
            raise ValueError(
                f"Request failed with status code {res.status_code}: {res.text}"
            )
        return res
