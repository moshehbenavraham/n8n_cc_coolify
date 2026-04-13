#!/bin/bash
# Wrapper script to run n8n-mcp with environment variables from .env

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
fi

N8N_BASE_URL="${N8N_LOCAL_URL:-${N8N_URL:-}}"

if [ -z "$N8N_BASE_URL" ] || [ -z "${N8N_API_KEY:-}" ]; then
    echo "Error: N8N_LOCAL_URL or N8N_URL, and N8N_API_KEY, must be set." >&2
    exit 1
fi

export N8N_API_URL="${N8N_BASE_URL%/}/api/v1"
export N8N_API_KEY
export MCP_MODE="stdio"
export LOG_LEVEL="error"
export DISABLE_CONSOLE_OUTPUT="true"

exec npx -y n8n-mcp@latest
