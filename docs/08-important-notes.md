# Important Notes

WSL2 Ubuntu | Docker Compose | ngrok

---

1. **Encryption Key**: The `N8N_ENCRYPTION_KEY` is critical. If lost, all credentials in n8n become unrecoverable.

2. **Workers**: n8n runs in queue mode with 3 workers + 3 runners for parallel execution.

3. **ngrok URL**: The ngrok tunnel URL changes on restart (unless using a paid plan with reserved domains). Update `.env` and MCP server config when it changes.

4. **Local Only**: This stack runs locally in WSL2. External access requires the ngrok tunnel to be active.

5. **Docker Compose**: All container management uses standard `docker compose` commands from `$N8N_DEPLOYMENT_PATH`.

---

*Documentation generated: 2026-01-27*
