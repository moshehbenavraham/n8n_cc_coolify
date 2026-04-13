# n8n Infrastructure Documentation

**Version:** 1.4.0

Build, edit, debug, back up, and maintain n8n workflows and the n8n installation with OpenAI Codex CLI.

This repo is centered around a local WSL2 Ubuntu + Docker Compose + ngrok n8n stack, plus project-specific MCP and workflow utility scripts.

Our open-source n8n "Launchpad" production repo: https://github.com/moshehbenavraham/n8n-aiwithapex

Our open-source customized n8n repo: https://github.com/moshehbenavraham/n8n

> **Note:** For more details, tutorials, and community support, join our free AI community: https://www.skool.com/ai-with-apex/about

## Stack

| Service | URL | Purpose |
|---------|-----|---------|
| n8n | `$N8N_URL` (public) / `$N8N_LOCAL_URL` (local) | Workflow automation (queue mode, 3 workers) |
| PostgreSQL | localhost:5432 | n8n database |
| Redis | localhost:6379 | Queue management |

> URLs and credentials are configured in `.env`.

## Setup

1. Copy `.env.example` to `.env`
2. Fill in credentials, URLs, and API keys
3. Source before running commands: `source .env`

## OpenAI Codex CLI Setup

Codex CLI reads project instructions from `AGENTS.md`. It does not read this repo's `.mcp.json` directly, so register the MCP servers once in your Codex CLI config:

```bash
cd /absolute/path/to/n8n_cc_coolify
source .env

codex mcp add n8n-mcp -- "$PWD/scripts/run-n8n-mcp.sh"
codex mcp add n8n-instance-mcp --url "$N8N_INSTANCE_LEVEL_MCP_URL" \
  --bearer-token-env-var N8N_INSTANCE_LEVEL_MCP_TOKEN
```

Verify with:

```bash
codex mcp list
```

`.mcp.json.example` is still included for tools that support project-local `mcp.json` files.

## Documentation

See [`docs/README_docs.md`](docs/README_docs.md) for the full index.

| Doc | Description |
|-----|-------------|
| [01-prompting-codex](docs/01-prompting-codex.md) | Codex workflow engineering prompt |
| [02-n8n](docs/02-n8n.md) | n8n setup and management |
| [04-troubleshooting](docs/04-troubleshooting.md) | Common issues |
| [05-backups](docs/05-backups.md) | Backup commands |
| [06-network-topology](docs/06-network-topology.md) | Infrastructure diagram |
| [07-docker-networks](docs/07-docker-networks.md) | Docker network reference |
| [08-important-notes](docs/08-important-notes.md) | Critical operational notes |

## Quick Commands

```bash
source .env
cd $N8N_DEPLOYMENT_PATH

# List n8n containers
docker compose ps

# View n8n logs
docker compose logs -f n8n

# Restart n8n stack
docker compose restart

# Access n8n database
docker compose exec postgres psql -U $N8N_DB_USERNAME -d n8n

# Backup n8n database
docker compose exec postgres pg_dump -U $N8N_DB_USERNAME -d n8n > n8n_backup_$(date +%Y%m%d).sql
```

## Codex + MCP Tooling

This project is designed to work with:

| Tool | Source | Purpose |
|------|--------|---------|
| n8n MCP Server | https://github.com/czlonkowski/n8n-mcp-cc-buildier | Node docs, templates, validation |
| n8n Instance MCP | https://docs.n8n.io/advanced-ai/accessing-n8n-mcp-server/ | Direct workflow execution (search, get, execute) |
| Repo `AGENTS.md` | This repository | Codex CLI project guidance and operating rules |

## Scripts

Utility scripts in `scripts/` (source `.env` first):

```bash
source .env

# Upgrade node typeVersions across all workflows
./scripts/upgrade_node_versions.sh preview all
./scripts/upgrade_node_versions.sh apply all

# Fix and deploy workflows with validation errors
./scripts/fix_and_deploy_workflows.sh path/to/workflow.json

# Bulk deploy workflows from voice_ai/workflows/
./scripts/deploy_voice_ai_workflows.sh

# Tag management (Community Edition)
python scripts/n8n_tags.py list
python scripts/n8n_tags.py create "My Tag"

# Project management (Enterprise only)
python scripts/n8n_projects.py list
```

## Deployment

The n8n stack runs locally at `$N8N_DEPLOYMENT_PATH` via Docker Compose. Public access is provided via ngrok through `$N8N_URL`.
