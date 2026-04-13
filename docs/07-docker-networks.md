# Docker Networks

WSL2 Ubuntu | Docker Compose | ngrok

---

| Network | Name | Purpose |
|---------|------|---------|
| n8n-network | n8n stack | n8n + workers + postgres + redis |

## Network Details

The n8n stack uses a single Docker bridge network (`n8n-network`) for inter-container communication.

```bash
# List networks
docker network ls

# Inspect n8n network
docker network inspect n8n-network
```

## Container Connectivity

All containers in the stack communicate via the `n8n-network`:

- **n8n** -> postgres (database)
- **n8n** -> redis (queue)
- **workers** -> postgres (database)
- **workers** -> redis (queue)

---

*Documentation generated: 2026-01-27*
