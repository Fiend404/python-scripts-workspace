"""
Script: scrape_and_generate.py
Purpose: Scrape a webpage with pydoll and generate a BS4 parsing script via Gemini.

Usage:
    uv run python scripts/individual/scrape_and_generate.py \
        --website_url https://example.com \
        --context "all product names and prices" \
        --html_filepath output.html \
        --output_python_script_filepath parser.py
"""

import argparse
import asyncio
import logging
import os
import re
import sys
import traceback
from datetime import UTC, datetime
from pathlib import Path

from google import genai
from pydoll.browser.chromium import Chrome
from pydoll.browser.options import Options

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Create a Python script to parse all {context} data metrics from the "
    "following HTML using beautifulsoup4.\n"
    "The output must be returned in json format.\n"
    "You must use pydoll non headless browser to navigate, export and parse "
    "the JSON from HTML."
)

EXAMPLE_SCRIPT = r'''import argparse
import asyncio
import json
from bs4 import BeautifulSoup
from pydoll.browser.chromium import Chrome
from pydoll.browser.options import Options

async def scrape_and_parse(url: str):
    options = Options()
    options.add_argument("--disable-gpu")

    async with Chrome(options=options) as browser:
        tab = await browser.start()
        await tab.go_to(url)

        html = await tab.page_source

    soup = BeautifulSoup(html, "html.parser")

    data = []
    for row in soup.select("table tr"):
        cols = [col.get_text(strip=True) for col in row.find_all(["td", "th"])]
        if cols:
            data.append(cols)

    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Target webpage URL")
    args = parser.parse_args()
    asyncio.run(scrape_and_parse(args.url))
'''


def log_error(script_name: str, error: Exception) -> None:
    """Write error details to scripts/errors/individual/<script>.error.log."""
    error_dir = Path(__file__).resolve().parent.parent / "errors" / "individual"
    error_dir.mkdir(parents=True, exist_ok=True)
    log_path = error_dir / f"{script_name}.error.log"
    entry = (
        f"[{datetime.now(UTC).isoformat()}]\n"
        f"Error: {error}\n"
        f"Traceback:\n{traceback.format_exc()}\n"
        f"{'=' * 60}\n"
    )
    with open(log_path, "a") as f:
        f.write(entry)


def strip_markdown_fences(text: str) -> str:
    """Remove markdown code fences from generated script text."""
    text = re.sub(r"^```(?:python)?\n?", "", text.strip())
    text = re.sub(r"\n?```$", "", text.strip())
    return text


async def scrape_html(url: str) -> str:
    """Launch pydoll Chrome, navigate to url, return full page HTML."""
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    async with Chrome(options=options) as browser:
        tab = await browser.start()
        await tab.go_to(url)
        html: str = await tab.page_source
    return html


def generate_parser_script(
    html: str, context: str, api_key: str
) -> str:
    """Send HTML + context to Gemini 2.0 Flash and return generated script."""
    client = genai.Client(api_key=api_key)

    system_instruction = SYSTEM_PROMPT.format(context=context)
    user_content = f"{html}\n\nExample Python script:\n\n{EXAMPLE_SCRIPT}"

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=user_content,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_instruction,
        ),
    )
    return strip_markdown_fences(response.text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape a webpage and generate a BS4 parsing script via Gemini."
    )
    parser.add_argument(
        "--website_url", required=True, help="Target webpage URL to scrape"
    )
    parser.add_argument(
        "--context", required=True, help="Describe what data to extract"
    )
    parser.add_argument(
        "--html_filepath", required=True, help="File path to save raw HTML"
    )
    parser.add_argument(
        "--output_python_script_filepath",
        required=True,
        help="File path to save generated Python script",
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    return parser.parse_args()


async def async_main(args: argparse.Namespace) -> None:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY environment variable is not set")
        sys.exit(1)

    html_path = Path(args.html_filepath)
    script_path = Path(args.output_python_script_filepath)

    logger.info("Scraping %s with pydoll...", args.website_url)
    html = await scrape_html(args.website_url)

    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")
    logger.info("Saved HTML (%d chars) to %s", len(html), html_path)

    logger.info("Sending HTML to Gemini 2.0 Flash...")
    script_text = generate_parser_script(html, args.context, api_key)

    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script_text, encoding="utf-8")
    logger.info("Saved generated script to %s", script_path)


def main() -> None:
    args = parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    try:
        asyncio.run(async_main(args))
    except Exception as exc:
        log_error("scrape_and_generate", exc)
        logger.exception("Fatal error")
        sys.exit(1)


if __name__ == "__main__":
    main()
