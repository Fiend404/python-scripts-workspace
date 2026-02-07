Python Scripts Workspace

Template for creating, analysing, and validating Python scripts with Claude Code integration, UV package management, and proxy-aware networking.

Quick Start

    # Clone the template
    gh repo create my-project --template org/python-scripts-workspace

    # Install UV (if not present)
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Sync dependencies
    uv sync

    # Configure proxy
    cp .env.example .env          # fill in proxy creds & API keys
    source proxy/setup_proxy.sh

    # Run a script
    uv run python scripts/individual/example_script.py --url https://httpbin.org/get

Project Structure

    scripts/individual/     Standalone single-file scripts
    scripts/groups/         Multi-file script bundles and SDKs
    scripts/errors/         Error logs per script/group
    tests/                  Mirrors scripts/ structure
    proxy/                  Dedicated IP proxy configuration
    .claude/                Claude Code rules, references, and subagents

Components

UV Package Manager
    All installs via uv add. All runs via uv run. No pip, no conda.

Claude Code Integration
    .claude/claude.md defines project rules. Subagents in .claude/subagents/ handle
    script generation (generator) and validation (analyser).

Proxy Configuration
    All outbound HTTP routes through the dedicated IP proxy. Configure in proxy/proxy.conf
    and source proxy/setup_proxy.sh to set environment variables.

Error Reports
    Every script logs failures to scripts/errors/ with tracebacks, timestamps, and
    environment info.

CI Workflows
    Ruff linting on push (.github/workflows/lint.yml) and Pytest matrix across Python
    versions (.github/workflows/test.yml).

Adding a Script

    Individual: Create scripts/individual/my_script.py following .claude/references/style_guide.md.
    Group/SDK: Create scripts/groups/my_sdk/ with __init__.py, client.py, utils.py.
    Tests: Mirror the path under tests/.

License

    MIT
