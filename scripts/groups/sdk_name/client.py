"""
Client module for SDK Name.

Provides the main ExampleClient class for interacting with the API.
"""

import logging
import os
from typing import Any

import httpx

from sdk_name.utils import build_headers

logger = logging.getLogger(__name__)


class ExampleClient:
    """HTTP client for the Example API."""

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        timeout: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("API_KEY", "")
        self.timeout = timeout
        self._client = self._build_client()

    def _build_client(self) -> httpx.Client:
        """Build an httpx client with proxy and auth headers."""
        proxy_url = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
        headers = build_headers(self.api_key)
        return httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=self.timeout,
            proxy=proxy_url,
        )

    def get_data(self, endpoint: str = "/data") -> dict[str, Any]:
        """Fetch data from the API."""
        response = self._client.get(endpoint)
        response.raise_for_status()
        return response.json()

    def post_data(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Send data to the API."""
        response = self._client.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> "ExampleClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
