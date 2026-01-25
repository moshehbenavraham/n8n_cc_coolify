# Important Notes

Server: See .env for server details | OS: Ubuntu 24.04 LTS

---

1. **Encryption Key**: The `N8N_ENCRYPTION_KEY` is critical. If lost, all credentials in n8n become unrecoverable.

2. **Agent Memory DB**: Exposed on port 5400. Firewall allows Docker internal access (172.17.0.0/16). Review if external access is needed.

3. **Workers**: n8n runs in queue mode with 3 workers + 3 runners for parallel execution.

4. **Coolify Management**: All services are managed via Coolify dashboard. Avoid manual Docker changes when possible.

5. **Traefik**: Handles SSL via Let's Encrypt automatically. Certificates stored in `/data/coolify/ssl/`.

---

*Documentation generated: 2026-01-18*
