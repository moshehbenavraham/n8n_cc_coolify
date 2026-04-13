#!/bin/bash
# Wrapper script to run n8n-mcp with environment variables from .env

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$PROJECT_DIR/.env" ]; then
    N8N_URL=$(grep '^N8N_URL=' "$PROJECT_DIR/.env" | cut -d'=' -f2-)
    N8N_API_KEY=$(grep '^N8N_API_KEY=' "$PROJECT_DIR/.env" | cut -d'=' -f2-)
fi

export N8N_API_URL="${N8N_URL}/api/v1"
export N8N_API_KEY
export MCP_MODE="stdio"
export LOG_LEVEL="error"
export DISABLE_CONSOLE_OUTPUT="true"

exec npx -y n8n-mcp@latest
