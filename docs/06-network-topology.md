# Network Topology

Server: See .env for server details | OS: Ubuntu 24.04 LTS

---

```
Internet
    |
[Cloudflare] ──── aiwithapex.com
    |
[UFW Firewall] ──── $SERVER_IP
    |
[coolify-proxy/Traefik] :80/:443
    |
    ├── coolify.aiwithapex.com ──► [coolify:8080]
    │                                    |
    │                              [coolify-db:5432]
    │
    └── n8n.aiwithapex.com ──► [n8n:5678]
                                    |
                    ┌───────────────┼───────────────┐
                    |               |               |
              [n8n-worker-1]  [n8n-worker-2]  [n8n-worker-3]
                    |               |               |
              [runner-1]      [runner-2]      [runner-3]
                    |
                    ├── [postgres (n8n DB):5432]
                    ├── [redis:6379]
                    └── [agent-memory (Postgres):5400]
```

---

*Documentation generated: 2026-01-18*
