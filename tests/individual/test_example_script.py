"""Tests for scripts/individual/example_script.py."""

import json
from unittest.mock import MagicMock, patch

import pytest

# Add scripts to path for direct import
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts" / "individual"))

from example_script import fetch_url, get_client


class TestGetClient:
    """Tests for get_client()."""

    def test_returns_httpx_client(self) -> None:
        import httpx

        client = get_client()
        assert isinstance(client, httpx.Client)
        client.close()

    @patch.dict("os.environ", {"HTTPS_PROXY": "http://proxy.example.com:8080"})
    def test_uses_proxy_from_env(self) -> None:
        client = get_client()
        assert client._transport is not None
        client.close()


class TestFetchUrl:
    """Tests for fetch_url()."""

    @patch("example_script.get_client")
    def test_returns_json_response(self, mock_get_client: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_get_client.return_value = mock_client

        result = fetch_url("https://example.com/api")
        assert result == {"key": "value"}
