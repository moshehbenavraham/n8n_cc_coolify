# Coolify + n8n + Agent Memory PostgreSQL Documentation

Server: See .env for server details | OS: Ubuntu 24.04 LTS

---

## Quick Reference

| Service | URL | Port |
|---------|-----|------|
| Coolify Dashboard | `$COOLIFY_URL` | 8000 (internal 8080) |
| n8n | `$N8N_URL` | 5678 |
| Agent Memory PostgreSQL | localhost:5400 | 5400->5432 |
| Traefik Dashboard | :8080 (internal only) | 8080 |

> URLs configured in `.env` file.

---

## Documentation Index

| # | Document | Description |
|---|----------|-------------|
| 1 | [Coolify](01-coolify.md) | Container orchestration platform configuration |
| 2 | [n8n Workflow Automation](02-n8n.md) | Workflow engine setup and credentials |
| 3 | [Agent Memory PostgreSQL](03-agent-memory-postgres.md) | Chat history database for AI agents |
| 4 | [Troubleshooting](04-troubleshooting.md) | Common issues and diagnostic commands |
| 5 | [Backup Commands](05-backups.md) | Database backup procedures |
| 6 | [Network Topology](06-network-topology.md) | Infrastructure diagram |
| 7 | [Docker Networks](07-docker-networks.md) | Container network reference |
| 8 | [Important Notes](08-important-notes.md) | Critical operational warnings |
| 9 | [Atlas Workflow](09-atlas-workflow.md) | AI Executive Assistant agent documentation |

---

## Architecture Overview

```
Internet -> Cloudflare -> UFW -> Traefik (coolify-proxy)
                                      |
                    +----------------+----------------+
                    |                                 |
        coolify.aiwithapex.com            n8n.aiwithapex.com
                    |                                 |
              [coolify:8080]                    [n8n:5678]
              [coolify-db]                          |
              [coolify-redis]         +-------------+-------------+
              [coolify-realtime]      |             |             |
                                 [worker-1]    [worker-2]    [worker-3]
                                 [runner-1]    [runner-2]    [runner-3]
                                      |
                    +-----------------+-----------------+
                    |                 |                 |
              [postgres:5432]    [redis:6379]    [agent-memory:5400]
                 (n8n DB)          (queue)         (chat history)
```

---

## Key Services

| Service | Container/Network ID | Purpose |
|---------|---------------------|---------|
| Coolify | coolify | Container orchestration platform |
| n8n Main | $N8N_NETWORK_ID | Workflow automation engine |
| Agent Memory DB | $AGENT_MEMORY_CONTAINER_ID | PostgreSQL 16 for chat history |

> IDs stored in `.env` file. IDs change on redeployment.

---

## Essential Commands

### Container Management

```bash
# Source environment variables first
source .env

# List all n8n containers
sudo docker ps -f name=$N8N_NETWORK_ID

# Restart n8n stack
sudo docker restart $(sudo docker ps -qf name=$N8N_NETWORK_ID)

# View n8n logs
sudo docker logs $(sudo docker ps -qf name=n8n-$N8N_NETWORK_ID | head -1) -f
```

### Database Access

```bash
# Source environment variables first
source .env

# n8n database
sudo docker exec -it $(sudo docker ps -qf name=postgres-$N8N_NETWORK_ID) psql -U $N8N_DB_USERNAME -d n8n

# Agent memory database
sudo docker exec -it $AGENT_MEMORY_CONTAINER_ID psql -U $AGENT_MEMORY_DB_USERNAME

# Coolify database
sudo docker exec -it coolify-db psql -U $COOLIFY_DB_USERNAME
```

### Backups

```bash
# Source environment variables first
source .env

# n8n database
sudo docker exec $(sudo docker ps -qf name=postgres-$N8N_NETWORK_ID) pg_dump -U $N8N_DB_USERNAME -d n8n > n8n_backup_$(date +%Y%m%d).sql

# Agent memory
sudo docker exec $AGENT_MEMORY_CONTAINER_ID pg_dump -U $AGENT_MEMORY_DB_USERNAME -d $AGENT_MEMORY_DB_NAME > agent_memory_backup_$(date +%Y%m%d).sql
```

---

*Documentation generated: 2026-01-18*
*Server details in .env file*
