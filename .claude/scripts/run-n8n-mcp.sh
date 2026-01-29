#!/bin/bash
# Wrapper script to run n8n-mcp with environment variables from .env

# Find the project root (where .env is located)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Source only the needed variables from .env (handles special characters)
if [ -f "$PROJECT_DIR/.env" ]; then
    N8N_URL=$(grep '^N8N_URL=' "$PROJECT_DIR/.env" | cut -d'=' -f2-)
    N8N_API_KEY=$(grep '^N8N_API_KEY=' "$PROJECT_DIR/.env" | cut -d'=' -f2-)
fi

# Set n8n-mcp required environment variables
export N8N_API_URL="${N8N_URL}/api/v1"
export N8N_API_KEY
export MCP_MODE="stdio"
export LOG_LEVEL="error"
export DISABLE_CONSOLE_OUTPUT="true"

# Run the MCP server using npx
exec npx -y n8n-mcp@latest
