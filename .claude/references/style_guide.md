Python Scripts Workspace — Style Guide

Script Template

Every script follows this structure:

```python
"""
Script: script_name.py
Purpose: One-line description of what this script does.

Usage:
    uv run python scripts/individual/script_name.py --arg value
"""

import argparse
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="What this script does.")
    parser.add_argument("--input", required=True, help="Input file or value")
    parser.add_argument("--output", default="output.json", help="Output file path")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Main logic here
    logger.info("Starting %s", Path(__file__).stem)


if __name__ == "__main__":
    main()
```

Error Handling Pattern

```python
import traceback
from datetime import datetime, timezone
from pathlib import Path


def log_error(script_name: str, error: Exception) -> None:
    """Write error details to scripts/errors/individual/<script>.error.log."""
    error_dir = Path(__file__).resolve().parent.parent / "errors" / "individual"
    error_dir.mkdir(parents=True, exist_ok=True)
    log_path = error_dir / f"{script_name}.error.log"

    entry = (
        f"[{datetime.now(timezone.utc).isoformat()}]\n"
        f"Error: {error}\n"
        f"Traceback:\n{traceback.format_exc()}\n"
        f"{'=' * 60}\n"
    )

    with open(log_path, "a") as f:
        f.write(entry)
```

Proxy-Aware HTTP Requests

```python
import os
import httpx


def get_client() -> httpx.Client:
    """Return an httpx client configured with proxy from environment."""
    proxy_url = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
    if proxy_url:
        return httpx.Client(proxy=proxy_url)
    return httpx.Client()
```

Conventions

- Imports: stdlib, then third-party, then local (Ruff isort handles this)
- Type hints on all function signatures
- Docstrings on public functions
- Constants in UPPER_SNAKE_CASE at module top
- No global mutable state
- Prefer pathlib.Path over os.path
- Prefer httpx over requests for new scripts (async-ready)
- JSON output: use json.dump with indent=2
