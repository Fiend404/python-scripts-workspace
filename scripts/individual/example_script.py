"""
Script: example_script.py
Purpose: Example standalone script demonstrating workspace conventions.

Usage:
    uv run python scripts/individual/example_script.py --url https://httpbin.org/get
    uv run python scripts/individual/example_script.py --url https://httpbin.org/get --output result.json --verbose
"""

import argparse
import json
import logging
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

SCRIPT_NAME = Path(__file__).stem
ERROR_DIR = Path(__file__).resolve().parent.parent / "errors" / "individual"


def log_error(error: Exception) -> None:
    """Write error details to scripts/errors/individual/example_script.error.log."""
    ERROR_DIR.mkdir(parents=True, exist_ok=True)
    log_path = ERROR_DIR / f"{SCRIPT_NAME}.error.log"

    entry = (
        f"[{datetime.now(timezone.utc).isoformat()}]\n"
        f"Error: {error}\n"
        f"Traceback:\n{traceback.format_exc()}\n"
        f"{'=' * 60}\n"
    )

    with open(log_path, "a") as f:
        f.write(entry)

    logger.error("Error logged to %s", log_path)


def get_client() -> httpx.Client:
    """Return an httpx client configured with proxy from environment."""
    proxy_url = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
    if proxy_url:
        return httpx.Client(proxy=proxy_url)
    return httpx.Client()


def fetch_url(url: str) -> dict:
    """Fetch a URL and return the JSON response."""
    with get_client() as client:
        response = client.get(url)
        response.raise_for_status()
        return response.json()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch a URL and save the JSON response."
    )
    parser.add_argument("--url", required=True, help="URL to fetch")
    parser.add_argument("--output", default=None, help="Output file path (optional)")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    try:
        logger.info("Fetching %s", args.url)
        data = fetch_url(args.url)

        if args.output:
            output_path = Path(args.output)
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)
            logger.info("Saved response to %s", output_path)
        else:
            print(json.dumps(data, indent=2))

    except Exception as e:
        log_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
