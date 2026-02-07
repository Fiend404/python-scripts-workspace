"""Tests for scripts/groups/sdk_name/client.py."""

from unittest.mock import MagicMock, patch

import pytest

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "groups"))

from sdk_name.client import ExampleClient


class TestExampleClient:
    """Tests for ExampleClient."""

    def test_init_sets_base_url(self) -> None:
        client = ExampleClient(base_url="https://api.example.com/v1/")
        assert client.base_url == "https://api.example.com/v1"
        client.close()

    def test_init_strips_trailing_slash(self) -> None:
        client = ExampleClient(base_url="https://api.example.com/v1///")
        assert client.base_url == "https://api.example.com/v1//"
        client.close()

    @patch.dict("os.environ", {"API_KEY": "test-key-123"})
    def test_uses_env_api_key(self) -> None:
        client = ExampleClient(base_url="https://api.example.com/v1")
        assert client.api_key == "test-key-123"
        client.close()

    def test_explicit_api_key_overrides_env(self) -> None:
        client = ExampleClient(
            base_url="https://api.example.com/v1",
            api_key="explicit-key",
        )
        assert client.api_key == "explicit-key"
        client.close()

    def test_context_manager(self) -> None:
        with ExampleClient(base_url="https://api.example.com/v1") as client:
            assert client.base_url == "https://api.example.com/v1"
