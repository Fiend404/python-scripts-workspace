"""
Shared utilities for SDK Name.
"""


def build_headers(api_key: str) -> dict[str, str]:
    """Build request headers with authentication."""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers
