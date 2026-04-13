# Network Topology

WSL2 Ubuntu | Docker Compose | ngrok

---

```
Internet
    |
[ngrok] ──── $N8N_URL (public HTTPS)
    |
    | (tunnel to localhost:5678)
    |
[WSL2 Ubuntu]
    |
[Docker Network: n8n-network]
    |
    ├── [n8n:5678] ──► Main n8n instance
    │        |
    │   ┌────┼────────────────┐
    │   |    |                |
    │ [worker-1] [worker-2] [worker-3]
    │   |         |           |
    │ [runner-1] [runner-2] [runner-3]
    │
    ├── [postgres:5432] ──► n8n database
    │
    └── [redis:6379] ──► Queue management
```

---

*Documentation generated: 2026-01-27*
