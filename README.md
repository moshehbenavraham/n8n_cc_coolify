# n8n Infrastructure Documentation

**Version:** 1.3.0

Build, edit, debug, backup, maintain n8n workflows and the n8n installation with Claude Code.

How?  By using a specialized n8n MCP server, n8n skill, direct access to n8n install, and infrastructure documentation for a local WSL2 Ubuntu Docker + ngrok n8n stack.

Our Open-Source n8n "Launchpad" production repo: https://github.com/moshehbenavraham/n8n-aiwithapex

Our Open-Source customized n8n, at this stage mostly for experimentation: https://github.com/moshehbenavraham/n8n

> **Note:** For more details, tutorials, and community support, join our free AI community: https://www.skool.com/ai-with-apex/about

## Stack

| Service | URL | Purpose |
|---------|-----|---------|
| n8n | `$N8N_URL` (ngrok) | Workflow automation (queue mode, 3 workers) |
| PostgreSQL | localhost:5432 | n8n database |
| Redis | localhost:6379 | Queue management |

> URLs configured in `.env` file.

## Setup

1. Copy `.env.example` to `.env`
2. Fill in credentials and ngrok URL
3. Source before running commands: `source .env`

## Documentation

See [`docs/README_docs.md`](docs/README_docs.md) for full index.

| Doc | Description |
|-----|-------------|
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

## Environment Variables

All credentials and IDs stored in `.env` (git-ignored). See `.env.example` for required variables:

- n8n URL (ngrok public URL)
- Deployment path
- n8n database credentials
- n8n encryption key

## Claude Code Tooling

This project uses Claude Code with n8n-specific MCP servers and skills:

| Tool | Source | Purpose |
|------|--------|---------|
| n8n MCP Server | https://github.com/czlonkowski/n8n-mcp-cc-buildier | Node docs, templates, validation |
| n8n Instance MCP | https://docs.n8n.io/advanced-ai/accessing-n8n-mcp-server/ | Direct workflow execution (search, get, execute) |
| n8n Skills | https://github.com/czlonkowski/n8n-skills | Expression syntax, validation, patterns, Code nodes |

## Scripts

Utility scripts in `scripts/` (source `.env` first):

```bash
source .env

# Upgrade node typeVersions across all workflows
./scripts/upgrade_node_versions.sh preview all    # Preview changes
./scripts/upgrade_node_versions.sh apply all      # Apply upgrades

# Fix and deploy workflows with validation errors
./scripts/fix_and_deploy_workflows.sh             # Cleans non-standard properties

# Bulk deploy workflows from voice_ai/workflows/
./scripts/deploy_voice_ai_workflows.sh

# Tag management (Community Edition)
python scripts/n8n_tags.py list
python scripts/n8n_tags.py create "My Tag"

# Project management (Enterprise only)
python scripts/n8n_projects.py list
```

## Deployment

The n8n stack runs locally at `$N8N_DEPLOYMENT_PATH` via Docker Compose. Public access is provided via ngrok tunnel to `$N8N_URL`.
