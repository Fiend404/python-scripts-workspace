"""
SDK Name — Example multi-file script bundle.

Usage:
    from sdk_name import ExampleClient

    client = ExampleClient(base_url="https://api.example.com/v1")
    data = client.get_data()
"""

__version__ = "0.1.0"

from sdk_name.client import ExampleClient

__all__ = ["ExampleClient"]
