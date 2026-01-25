# Backup Commands

Server: See .env for server details | OS: Ubuntu 24.04 LTS

---

## n8n Database Backup

```bash
# Source environment variables first
source .env

# Full backup
sudo docker exec $(sudo docker ps -qf name=postgres-$N8N_NETWORK_ID) pg_dump -U $N8N_DB_USERNAME -d n8n > n8n_backup_$(date +%Y%m%d).sql

# Workflows only
sudo docker exec $(sudo docker ps -qf name=postgres-$N8N_NETWORK_ID) pg_dump -U $N8N_DB_USERNAME -d n8n -t workflow_entity > n8n_workflows_$(date +%Y%m%d).sql
```

## Agent Memory Backup

```bash
# Source environment variables first
source .env

sudo docker exec $AGENT_MEMORY_CONTAINER_ID pg_dump -U $AGENT_MEMORY_DB_USERNAME -d $AGENT_MEMORY_DB_NAME > agent_memory_backup_$(date +%Y%m%d).sql
```

## Coolify Backup

```bash
# Source environment variables first
source .env

sudo docker exec coolify-db pg_dump -U $COOLIFY_DB_USERNAME > coolify_backup_$(date +%Y%m%d).sql
```

---

*Documentation generated: 2026-01-18*
