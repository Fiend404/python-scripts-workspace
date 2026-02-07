"""Tests for scrape_and_generate.py."""

import subprocess
import sys

import pytest

SCRIPT = "scripts/scrape_and_generate/scrape_and_generate.py"


def test_help_on_no_args():
    """Running with no args prints help and exits 0."""
    result = subprocess.run(
        [sys.executable, SCRIPT],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--website_url" in result.stdout
    assert "--context" in result.stdout


def test_missing_required_args():
    """Running with partial args exits non-zero."""
    result = subprocess.run(
        [sys.executable, SCRIPT, "--website_url", "https://example.com"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_missing_api_key(monkeypatch):
    """Running without GOOGLE_API_KEY exits 1 with error message."""
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    result = subprocess.run(
        [
            sys.executable,
            SCRIPT,
            "--website_url", "https://example.com",
            "--context", "test",
            "--html_filepath", "/tmp/test.html",
            "--output_python_script_filepath", "/tmp/test_parser.py",
        ],
        capture_output=True,
        text=True,
        env={k: v for k, v in __import__("os").environ.items() if k != "GOOGLE_API_KEY"},
    )
    assert result.returncode == 1
    assert "GOOGLE_API_KEY" in result.stderr


def test_strip_markdown_fences():
    """strip_markdown_fences removes code fences."""
    sys.path.insert(0, "scripts/scrape_and_generate")
    from scrape_and_generate import strip_markdown_fences

    assert strip_markdown_fences("```python\nprint('hi')\n```") == "print('hi')"
    assert strip_markdown_fences("```\ncode\n```") == "code"
    assert strip_markdown_fences("no fences") == "no fences"
