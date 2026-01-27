# Troubleshooting

WSL2 Ubuntu | Docker Compose | ngrok

---

## n8n Not Responding

```bash
# Source environment variables first
source .env
cd $N8N_DEPLOYMENT_PATH

# Check container health
docker compose ps

# Check logs for errors
docker compose logs n8n --tail 100

# Check Redis queue
docker compose exec redis redis-cli LLEN bull:jobs:wait

# Restart the stack
docker compose restart
```

## Database Connection Issues

```bash
# Source environment variables first
source .env
cd $N8N_DEPLOYMENT_PATH

# Test n8n DB connection
docker compose exec postgres pg_isready

# Check database logs
docker compose logs postgres --tail 50
```

## ngrok Tunnel Issues

```bash
# Check if ngrok is running
pgrep -a ngrok

# Restart ngrok tunnel (example)
ngrok http 5678

# Verify tunnel URL matches .env
echo $N8N_URL
```

## Disk Space Issues

```bash
# Check disk usage
df -h /
sudo du -sh /var/lib/docker/

# Clean Docker resources
docker system prune -a --volumes  # CAUTION: removes unused data

# Check volume sizes
docker volume ls
```

---

*Documentation generated: 2026-01-27*
