# AGENTS.md

This file provides project guidance for OpenAI Codex CLI and other agents that support `AGENTS.md`.

## Important Rules

- Do not edit the live deployment at `$N8N_DEPLOYMENT_PATH`; use it for inspection and reference only.
- Source `.env` before running scripts that talk to n8n, Docker, or the database.
- Prefer `N8N_LOCAL_URL` over `N8N_URL` for local API calls to avoid ngrok or auth issues.
- Keep edits ASCII UTF-8 with LF line endings unless a file already requires something else.
- Validate changes systematically. Do not guess URLs, API shapes, or node properties when you can verify them.

## Project Overview

This repo is a resource project for building, editing, and debugging n8n workflows. It includes:

- Infrastructure documentation for a local WSL2 Ubuntu + Docker + ngrok n8n stack
- MCP bootstrap scripts for n8n tooling
- Utility scripts for workflow deployment, repair, tagging, and upgrades
- Reference material for common n8n workflow patterns

## Documentation

- Start with `README.md` and `docs/README_docs.md`
- Prompt/session guidance lives in `docs/01-prompting-codex.md`
- Deployment and operating notes live under `docs/`

## MCP Servers

This project commonly uses two MCP servers:

- `n8n-mcp`: documentation, templates, validation, and workflow helpers
- `n8n-instance-mcp`: direct search/get/execute access to workflows exposed by the local n8n instance

The stdio wrapper for `n8n-mcp` is [`scripts/run-n8n-mcp.sh`](scripts/run-n8n-mcp.sh).

## Workflow Rules

- Webhook payload data is typically under `$json.body`
- n8n Code nodes should return arrays like `[{ json: {...} }]`
- Use `nodes-base.*` identifiers for node search/validation tools and `n8n-nodes-base.*` identifiers inside workflow JSON where applicable

## Scripts

- `scripts/run-n8n-mcp.sh`: starts the stdio MCP wrapper with values loaded from `.env`
- `scripts/upgrade_node_versions.sh`: previews or applies known node `typeVersion` upgrades
- `scripts/fix_and_deploy_workflows.sh`: strips unsupported properties and deploys workflow JSON files
- `scripts/deploy_voice_ai_workflows.sh`: bulk deploys workflows from `voice_ai/workflows/`
- `scripts/n8n_tags.py`: manage tags in Community Edition
- `scripts/n8n_projects.py`: manage projects in Enterprise Edition
