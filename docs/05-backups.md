# Backup Commands

WSL2 Ubuntu | Docker Compose | ngrok

---

## n8n Database Backup

```bash
# Source environment variables first
source .env
cd $N8N_DEPLOYMENT_PATH

# Full backup
docker compose exec postgres pg_dump -U $N8N_DB_USERNAME -d n8n > n8n_backup_$(date +%Y%m%d).sql

# Workflows only
docker compose exec postgres pg_dump -U $N8N_DB_USERNAME -d n8n -t workflow_entity > n8n_workflows_$(date +%Y%m%d).sql
```

## n8n Data Volume Backup

```bash
# Source environment variables first
source .env
cd $N8N_DEPLOYMENT_PATH

# Backup n8n data volume
docker run --rm -v n8n_n8n-data:/data -v $(pwd):/backup alpine tar czf /backup/n8n_data_$(date +%Y%m%d).tar.gz -C /data .
```

## Restore Database

```bash
# Source environment variables first
source .env
cd $N8N_DEPLOYMENT_PATH

# Restore from backup
cat n8n_backup_YYYYMMDD.sql | docker compose exec -T postgres psql -U $N8N_DB_USERNAME -d n8n
```

---

*Documentation generated: 2026-01-27*
