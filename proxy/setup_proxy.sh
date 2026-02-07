#!/usr/bin/env bash
# Source this file to configure proxy environment variables.
# Usage: source proxy/setup_proxy.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load proxy config
if [[ -f "$SCRIPT_DIR/proxy.conf" ]]; then
    source "$SCRIPT_DIR/proxy.conf"
else
    echo "Error: proxy/proxy.conf not found" >&2
    return 1 2>/dev/null || exit 1
fi

# Build proxy URL
if [[ -n "${PROXY_USER:-}" && -n "${PROXY_PASS:-}" ]]; then
    PROXY_URL="${PROXY_PROTOCOL}://${PROXY_USER}:${PROXY_PASS}@${PROXY_HOST}:${PROXY_PORT}"
else
    PROXY_URL="${PROXY_PROTOCOL}://${PROXY_HOST}:${PROXY_PORT}"
fi

export HTTP_PROXY="$PROXY_URL"
export HTTPS_PROXY="$PROXY_URL"
export NO_PROXY="localhost,127.0.0.1,::1"

echo "Proxy configured: ${PROXY_PROTOCOL}://${PROXY_HOST}:${PROXY_PORT}"
