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

## Cloudflare 526 / Traefik Default Certificate

If a proxied hostname returns Cloudflare `526`, verify the origin certificate before assuming WAF or bot issues:

```bash
curl -I https://n8n.aiwithapex.com/
echo | openssl s_client -connect 127.0.0.1:443 -servername n8n.aiwithapex.com 2>/dev/null | openssl x509 -noout -subject -issuer -dates
```

If the origin serves `TRAEFIK DEFAULT CERT`, check Traefik ACME storage and compare:

- the hostname key stored in `acme.json`
- the actual certificate subject/SAN
- current Docker and Traefik dynamic routes

For the full incident record, command trail, backup paths, and post-fix audit notes, see:

- `10-tls-incident-and-domain-audit-2026-03-16.md`

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
