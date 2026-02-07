Python Scripts Workspace — Project Rules

Scope Identification — MANDATORY FIRST STEP
- Before writing ANY code, extract the full project scope from the user's original prompt
- Scope defines the entire project end-to-end: what scripts are needed, their purpose, how they connect
- Break the scope into phases, where each phase produces one script or group
- For each script identify:
  - Purpose: what it does in one sentence
  - Inputs: what data/files/args it consumes
  - Outputs: what data/files it produces (filename + JSON schema if applicable)
  - Dependencies: what packages it needs
  - Chain position: which scripts feed into it and which scripts consume its output
- Map the full input/output chain across all scripts before starting any implementation
- Use this scope as the blueprint for TodoWrite phases — one phase per script
- NEVER start coding without a defined scope. If the prompt is ambiguous, ask clarifying questions first.

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

Development Workflow — HEREDOC First
- NEVER create .py files as a first step. Always prototype using HEREDOC + EOF:
  ```bash
  uv run python3 << 'EOF'
  # prototype logic here
  EOF
  ```
- Iterate in HEREDOC until the script logic is fully validated and producing correct output
- Run multiple iterations — fix errors, refine logic, verify all edge cases
- Only after HEREDOC output is 100% correct, save to a .py file in the appropriate folder
- When the script needs dependencies not yet in pyproject.toml, use uv run --with:
  ```bash
  uv run --with httpx --with beautifulsoup4 python3 << 'EOF'
  # test with temporary deps
  EOF
  ```
- After validation, add permanent deps with uv add before saving the .py file
- This pattern prevents broken scripts from entering the codebase

Script Finalization — Saving Validated Code
- Only save to .py file AFTER HEREDOC iteration confirms correct output
- Before saving, ensure the script includes:
  - Module-level docstring with purpose and usage example
  - argparse with help-on-no-args behaviour
  - Error handling with log_error() writing to scripts/errors/
  - Proxy-aware HTTP client (httpx.Client with proxy from env)
  - Type hints on all function signatures
- Placement rules:
  - Single-file script: scripts/individual/<name>.py
  - Multi-file bundle: scripts/groups/<name>/ with __init__.py, client.py, utils.py
- After saving the .py file, immediately create the matching test file:
  - scripts/individual/<name>.py -> tests/individual/test_<name>.py
  - scripts/groups/<name>/ -> tests/groups/<name>/test_client.py
- Add any temporary HEREDOC deps as permanent deps: uv add <package>
- Run uv run ruff check on the saved file before marking the phase complete

Script Requirements
- Every script MUST use argparse for CLI arguments
- Show help when no arguments provided
- Include a docstring at module level describing purpose and usage
- Handle errors using the shared error decorator (see references/style_guide.md)

Proxy Usage
- When a network request fails (timeout, connection refused, 403, 429, geo-block), retry through the proxy
- Proxy server: 5.231.28.18
  - HTTP proxy: http://5.231.28.18:3128
  - SOCKS5 proxy: socks5://5.231.28.18:1080
- Try direct connection first. On failure, retry with HTTP proxy. If still failing, retry with SOCKS5.
- httpx pattern:
  ```python
  import httpx

  def fetch(url: str) -> httpx.Response:
      # Try direct first
      try:
          return httpx.get(url, timeout=15)
      except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError):
          pass
      # Retry with HTTP proxy
      try:
          return httpx.get(url, proxy="http://5.231.28.18:3128", timeout=15)
      except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError):
          pass
      # Retry with SOCKS5 proxy
      return httpx.get(url, proxy="socks5://5.231.28.18:1080", timeout=15)
  ```
- curl_cffi pattern:
  ```python
  from curl_cffi import requests

  def fetch(url: str):
      try:
          return requests.get(url, impersonate="chrome", timeout=15)
      except Exception:
          pass
      try:
          return requests.get(url, impersonate="chrome", proxy="http://5.231.28.18:3128", timeout=15)
      except Exception:
          pass
      return requests.get(url, impersonate="chrome", proxy="socks5://5.231.28.18:1080", timeout=15)
  ```
- For scripts that always need proxy, set environment variables:
  ```bash
  export HTTP_PROXY=http://5.231.28.18:3128
  export HTTPS_PROXY=http://5.231.28.18:3128
  ```

Error Handling
- Wrap main logic in try/except
- Log errors to scripts/errors/ with traceback, timestamp, and environment info
- Never silently swallow exceptions
- Return non-zero exit code on failure

Code Style
- Follow Ruff defaults (line length 88, isort-compatible imports)
- Type hints on all function signatures
- No wildcard imports

Project Tree
  python-scripts-workspace/
  ├── .github/
  │   ├── ISSUE_TEMPLATE/
  │   │   └── bug_report.md
  │   ├── workflows/
  │   │   ├── lint.yml
  │   │   └── test.yml
  │   └── TEMPLATE_DESCRIPTION.md
  ├── .claude/
  │   ├── claude.md
  │   ├── references/
  │   │   ├── api_keys.env.example
  │   │   ├── endpoints.yaml
  │   │   └── style_guide.md
  │   ├── subagents/
  │   │   ├── analyser/
  │   │   │   └── agent.md
  │   │   └── generator/
  │   │       └── agent.md
  │   └── settings.json
  ├── scripts/
  │   ├── individual/          <-- standalone single-file scripts
  │   ├── groups/              <-- multi-file bundles and SDKs
  │   └── errors/
  │       ├── individual/      <-- error logs per standalone script
  │       └── groups/          <-- error logs per group
  ├── tests/
  │   ├── individual/          <-- mirrors scripts/individual/
  │   └── groups/              <-- mirrors scripts/groups/
  ├── proxy/
  │   ├── proxy.conf
  │   ├── ca_certs/
  │   └── setup_proxy.sh
  ├── .env.example
  ├── .gitignore
  ├── .python-version
  ├── pyproject.toml
  ├── uv.lock
  ├── README.md
  └── LICENSE

References
- Check .claude/references/ before generating code
- Read endpoints.yaml for service base URLs
- Read style_guide.md for patterns and conventions
- Never commit real API keys — use .env and api_keys.env.example as templates

Progress Tracking — TodoWrite is MANDATORY
- Every project MUST use TodoWrite to track all phases and steps
- Create the full task list BEFORE writing any code, derived from the Scope Identification
- One task per script/phase (e.g. "Build fetch_prices.py", "Build pricing_sdk group")
- Each task description must include: purpose, inputs, outputs, dependencies
- Workflow for every task:
  1. Mark task as in_progress BEFORE starting work
  2. Prototype in HEREDOC (Development Workflow)
  3. Validate output is correct
  4. Save to .py file (Script Finalization)
  5. Create test file
  6. Run ruff check
  7. Mark task as completed
- NEVER skip tracking. Every phase, every step gets a TodoWrite entry.
- If new tasks are discovered during implementation, add them immediately
- Check the task list after completing each task to identify the next one
- The project is not done until ALL tasks show completed
