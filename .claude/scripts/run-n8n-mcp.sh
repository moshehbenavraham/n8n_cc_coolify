#!/bin/bash
# Wrapper script to run n8n-mcp with environment variables from .env

# Find the project root (where .env is located)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Source the .env file and export all variables
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)
fi

# Run the MCP server
exec docker run --rm -i \
    --network n8n_n8n-network \
    -e "N8N_API_URL=http://n8n-main:5678/api/v1" \
    -e "N8N_API_KEY=$N8N_API_KEY" \
    -e "MCP_MODE=stdio" \
    -e "LOG_LEVEL=error" \
    -e "DISABLE_CONSOLE_OUTPUT=true" \
    ghcr.io/czlonkowski/n8n-mcp:latest
