# n8n Documentation

WSL2 Ubuntu | Docker Compose | ngrok

---

## Quick Reference

| Service | URL | Port |
|---------|-----|------|
| n8n | `$N8N_URL` (public) / `$N8N_LOCAL_URL` (local) | 5678 |
| PostgreSQL | localhost | 5432 |
| Redis | localhost | 6379 |

> URLs configured in `.env`.

---

## Documentation Index

| # | Document | Description |
|---|----------|-------------|
| 0 | [Coding Agent Prompt](00-coding-agent-prompt.md) | Short Codex-oriented prompting reference |
| 1 | [Prompting Codex](01-prompting-codex.md) | Workflow engineering prompt template |
| 2 | [n8n Workflow Automation](02-n8n.md) | Workflow engine setup and credentials |
| 4 | [Troubleshooting](04-troubleshooting.md) | Common issues and diagnostic commands |
| 5 | [Backup Commands](05-backups.md) | Database backup procedures |
| 6 | [Network Topology](06-network-topology.md) | Infrastructure diagram |
| 7 | [Docker Networks](07-docker-networks.md) | Container network reference |
| 8 | [Important Notes](08-important-notes.md) | Critical operational warnings |

---

## Architecture Overview

```
Internet
    |
[ngrok tunnel] ──── $N8N_URL
    |
[WSL2 Ubuntu]
    |
[Docker Compose]
    |
[n8n:5678]
    |
    +-------------+-------------+
    |             |             |
[worker-1]    [worker-2]    [worker-3]
[runner-1]    [runner-2]    [runner-3]
    |
    +-----------------+-----------------+
    |                 |
[postgres:5432]    [redis:6379]
   (n8n DB)          (queue)
```

---

## Essential Commands

### Container Management

```bash
source .env
cd $N8N_DEPLOYMENT_PATH

docker compose ps
docker compose restart
docker compose logs -f n8n
```

### Database Access

```bash
source .env
cd $N8N_DEPLOYMENT_PATH

docker compose exec postgres psql -U $N8N_DB_USERNAME -d n8n
```

### Backups

```bash
source .env
cd $N8N_DEPLOYMENT_PATH

docker compose exec postgres pg_dump -U $N8N_DB_USERNAME -d n8n > n8n_backup_$(date +%Y%m%d).sql
```

---

*Documentation generated: 2026-04-13*
