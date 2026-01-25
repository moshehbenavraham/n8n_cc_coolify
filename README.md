# n8n Infrastructure Documentation

**Version:** 1.0.0

Build, edit, debug, backup, maintain n8n workflows and the n8n installation with Claude Code.

Built using Private infrastructure documentation for a production Coolify + n8n stack.

Our Open-Source n8n "Launchpad" production repo: https://github.com/moshehbenavraham/n8n-aiwithapex

Our Open-Source customized n8n, at this stage mostly for experimentation: https://github.com/moshehbenavraham/n8n

> **Note:** The Atlas workflow and Agent Memory PostgreSQL are examples of mapping specific workflows with customized containers. For more details, tutorials, and community support, join our free AI community: https://www.skool.com/ai-with-apex/about

## Stack

| Service | URL | Purpose |
|---------|-----|---------|
| Coolify | `$COOLIFY_URL` | Container orchestration |
| n8n | `$N8N_URL` | Workflow automation (queue mode, 3 workers) |
| Agent Memory | localhost:5400 | PostgreSQL for AI chat history |

> URLs configured in `.env` file.

## Setup

1. Copy `.env.example` to `.env`
2. Fill in credentials and container IDs
3. Source before running commands: `source .env`

## Documentation

See [`docs/README_docs.md`](docs/README_docs.md) for full index.

| Doc | Description |
|-----|-------------|
| [01-coolify](docs/01-coolify.md) | Coolify configuration |
| [02-n8n](docs/02-n8n.md) | n8n setup and management |
| [03-agent-memory](docs/03-agent-memory-postgres.md) | Chat history database |
| [04-troubleshooting](docs/04-troubleshooting.md) | Common issues |
| [05-backups](docs/05-backups.md) | Backup commands |
| [06-network-topology](docs/06-network-topology.md) | Infrastructure diagram |
| [09-atlas-workflow](docs/09-atlas-workflow.md) | AI Executive Assistant agent |

## Quick Commands

```bash
source .env

# List n8n containers
sudo docker ps -f name=$N8N_NETWORK_ID

# View n8n logs
sudo docker logs $(sudo docker ps -qf name=n8n-$N8N_NETWORK_ID | head -1) -f

# Restart n8n stack
sudo docker restart $(sudo docker ps -qf name=$N8N_NETWORK_ID)

# Access n8n database
sudo docker exec -it $(sudo docker ps -qf name=postgres-$N8N_NETWORK_ID) psql -U $N8N_DB_USERNAME -d n8n

# Backup n8n database
sudo docker exec $(sudo docker ps -qf name=postgres-$N8N_NETWORK_ID) pg_dump -U $N8N_DB_USERNAME -d n8n > n8n_backup_$(date +%Y%m%d).sql
```

## Environment Variables

All credentials and IDs stored in `.env` (git-ignored). See `.env.example` for required variables:

- Server identity
- Container/network IDs (change on redeployment)
- Workflow IDs
- Coolify, n8n, and Agent Memory database credentials
- n8n encryption key and runner auth token

## Claude Code Tooling

This project uses Claude Code with n8n-specific MCP server and skills:

| Tool | Source | Purpose |
|------|--------|---------|
| n8n MCP Server | https://github.com/czlonkowski/n8n-mcp-cc-buildier | Programmatic workflow management |
| n8n Skills | https://github.com/czlonkowski/n8n-skills | Expression syntax, validation, patterns, Code nodes |

## Deployment

Commits to `main` trigger Coolify to rebuild and deploy the n8n stack from the production repo.
