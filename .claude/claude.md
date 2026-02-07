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
- Every script project gets its own folder: scripts/<script_name>/
- All artifacts for a script live together in that folder:
  - scripts/<script_name>/<script_name>.py
  - scripts/<script_name>/test_<script_name>.py
  - scripts/<script_name>/<script_name>.md
  - scripts/<script_name>/<script_name>.error.log

Naming Conventions
- Script folders: snake_case/ (e.g. scripts/fetch_prices/)
- Scripts: snake_case.py (e.g. fetch_prices.py)
- Tests: test_<script_name>.py
- Summaries: <script_name>.md
- Error logs: <script_name>.error.log

Development Workflow — HEREDOC First
- NEVER create .py files as a first step. Always prototype Python code inline using Bash HEREDOC + EOF.
- Write the full Python script inside the HEREDOC block and execute it via uv run:
  ```bash
  uv run python3 << 'EOF'
  import json
  from pathlib import Path

  data = {"status": "ok", "count": 42}
  print(json.dumps(data, indent=2))
  EOF
  ```
- Iterate in HEREDOC until the script logic is fully validated and producing correct output
- Run multiple iterations — fix errors, refine logic, verify all edge cases
- Only after HEREDOC output is 100% correct, save to a .py file in the appropriate folder
- When the script needs dependencies not yet in pyproject.toml, use uv run --with:
  ```bash
  uv run --with httpx --with beautifulsoup4 python3 << 'EOF'
  import httpx
  from bs4 import BeautifulSoup

  response = httpx.get("https://httpbin.org/html")
  soup = BeautifulSoup(response.text, "html.parser")
  print(f"Title: {soup.find('h1').text}")
  print(f"Status: {response.status_code}")
  EOF
  ```
- After validation, add permanent deps with uv add before saving the .py file
- This pattern prevents broken scripts from entering the codebase

Script Finalization — Saving Validated Code
- Only save to .py file AFTER HEREDOC iteration confirms correct output
- Before saving, ensure the script includes:
  - Module-level docstring with purpose and usage example
  - argparse with help-on-no-args behaviour
  - Error handling with log_error() writing to scripts/<script_name>/
  - Proxy-aware HTTP client (httpx.Client with proxy from env)
  - Type hints on all function signatures
- Placement: scripts/<script_name>/<script_name>.py
- After saving the .py file, immediately create the matching test file:
  - scripts/<script_name>/test_<script_name>.py
- Add any temporary HEREDOC deps as permanent deps: uv add <package>
- Run uv run ruff check on the saved file before marking the phase complete
- MANDATORY: After saving the final .py file, validate it using the analysis subagent:
  - Invoke: Task tool with subagent_type="analysis"
  - Prompt the subagent to:
    1. Read the saved script file
    2. Run the script with sample/test arguments to verify it executes without errors
    3. Validate output matches expected format (JSON schema, stdout, file creation)
    4. Check edge cases: missing args show help, bad input returns non-zero exit code
    5. Confirm error logging writes to scripts/<script_name>/ on failure
  - Do NOT mark the phase as completed until the analysis subagent confirms the script passes
  - If validation fails, fix the script and re-run analysis until it passes
- MANDATORY: After all validation passes, write a final summary .md file in the script folder:
  - Filename: scripts/<script_name>/<script_name>.md
  - Contents must include:
    - Script name and location
    - Test file location
    - What it does (numbered steps)
    - Usage example with full CLI invocation
    - CLI arguments table
    - Dependencies table
    - Validation results (tests passed, analysis checks, ruff status)
    - Any runtime requirements (env vars, credentials, external services)
  - Follow global .md rules: no heading syntax, no bold/italic syntax, no underline headings
  - This file is the single source of truth for understanding what the script does and how to run it

Filepath Validation — MANDATORY AFTER EVERY FILE SAVE
- After saving any script, test, summary, or config file, run tree on the parent directory to confirm correct placement
- Command: tree {{parent_directory}} -I __pycache__
- Verify:
  - The file appears in the expected directory
  - The filename matches the naming convention (snake_case.py, test_<name>.py, <name>.md)
  - Co-located files sit together (e.g. script.py and script.md in the same folder)
- Per script: tree scripts/<script_name>/ -I __pycache__
- All scripts: tree scripts/ -I __pycache__
- NEVER skip this step. Visual confirmation prevents misplaced files from going unnoticed.

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
- Log errors to scripts/<script_name>/ with traceback, timestamp, and environment info
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
  │   └── <script_name>/       <-- one folder per script project
  │       ├── <script_name>.py
  │       ├── test_<script_name>.py
  │       ├── <script_name>.md
  │       └── <script_name>.error.log
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
