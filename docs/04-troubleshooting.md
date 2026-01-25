# Troubleshooting

Server: See .env for server details | OS: Ubuntu 24.04 LTS

---

## n8n Not Responding

```bash
# Source environment variables first
source .env

# Check container health
sudo docker ps -f name=$N8N_NETWORK_ID

# Check logs for errors
sudo docker logs $(sudo docker ps -qf name=n8n-$N8N_NETWORK_ID | head -1) --tail 100

# Check Redis queue
sudo docker exec $(sudo docker ps -qf name=redis-$N8N_NETWORK_ID) redis-cli LLEN bull:jobs:wait

# Restart the stack
sudo docker restart $(sudo docker ps -qf name=$N8N_NETWORK_ID)
```

## Database Connection Issues

```bash
# Source environment variables first
source .env

# Test n8n DB connection
sudo docker exec $(sudo docker ps -qf name=postgres-$N8N_NETWORK_ID) pg_isready

# Test agent memory DB connection
sudo docker exec $AGENT_MEMORY_CONTAINER_ID pg_isready

# Check database logs
sudo docker logs $(sudo docker ps -qf name=postgres-$N8N_NETWORK_ID) --tail 50
sudo docker logs $AGENT_MEMORY_CONTAINER_ID --tail 50
```

## Coolify Issues

```bash
# Check all Coolify containers
sudo docker ps -f name=coolify

# View Coolify logs
sudo docker logs coolify --tail 100

# Restart Coolify stack
sudo docker restart coolify coolify-db coolify-redis coolify-realtime

# Check Traefik routing
sudo docker logs coolify-proxy --tail 50
```

## Disk Space Issues

```bash
# Check disk usage
df -h /
sudo du -sh /var/lib/docker/

# Clean Docker resources
sudo docker system prune -a --volumes  # CAUTION: removes unused data

# Check volume sizes
sudo du -sh /var/lib/docker/volumes/*
```

---

*Documentation generated: 2026-01-18*
