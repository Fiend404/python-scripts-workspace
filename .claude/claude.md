Python Scripts Workspace — Project Rules

Package Management
- UV is the only package manager. No pip, no conda.
- Install: uv add <package>
- Run: uv run python scripts/...
- Never use python or python3 directly

File Placement
- Standalone scripts go in scripts/individual/
- Multi-file bundles and SDKs go in scripts/groups/<name>/
- Tests mirror scripts/ structure under tests/
- Error logs go in scripts/errors/ matching the script path

Naming Conventions
- Scripts: snake_case.py (e.g. fetch_prices.py)
- Groups: snake_case/ directory (e.g. pricing_sdk/)
- Tests: test_<script_name>.py
- Error logs: <script_name>.error.log

Script Requirements
- Every script MUST use argparse for CLI arguments
- Show help when no arguments provided
- Include a docstring at module level describing purpose and usage
- Handle errors using the shared error decorator (see references/style_guide.md)

Proxy Usage
- All HTTP requests MUST route through the configured proxy
- Load proxy settings from environment variables (HTTP_PROXY, HTTPS_PROXY)
- Use requests.Session() or httpx.Client() with proxy config, never bare requests.get()
- Reference proxy/proxy.conf for connection details

Error Handling
- Wrap main logic in try/except
- Log errors to scripts/errors/ with traceback, timestamp, and environment info
- Never silently swallow exceptions
- Return non-zero exit code on failure

Code Style
- Follow Ruff defaults (line length 88, isort-compatible imports)
- Type hints on all function signatures
- No wildcard imports

References
- Check .claude/references/ before generating code
- Read endpoints.yaml for service base URLs
- Read style_guide.md for patterns and conventions
- Never commit real API keys — use .env and api_keys.env.example as templates
