# Docker Networks

Server: See .env for server details | OS: Ubuntu 24.04 LTS

---

| Network | Name | Purpose |
|---------|------|---------|
| $N8N_NETWORK_ID | n8n stack | n8n + workers + postgres + redis |
| coolify | coolify | Coolify management stack |
| $AGENT_MEMORY_CONTAINER_ID | Agent memory | Standalone Postgres for chat memory |

> Network/Container IDs stored in `.env` file. IDs change on redeployment.

---

*Documentation generated: 2026-01-18*
