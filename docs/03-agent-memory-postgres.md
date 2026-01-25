# Agent Memory PostgreSQL

Server: See .env for server details | OS: Ubuntu 24.04 LTS

---

## Overview

This is a **separate** PostgreSQL instance used specifically for n8n agent/chat memory storage (Atlas n8n Workflow).

- **Container**: `$AGENT_MEMORY_CONTAINER_ID` (see .env)
- **Image**: `postgres:16`
- **External Port**: 5400 (mapped to internal 5432)

## Connection Details

```
Host: localhost (from server) / $AGENT_MEMORY_DB_HOST (from Docker network)
Port: $AGENT_MEMORY_DB_PORT_EXTERNAL (external) / $AGENT_MEMORY_DB_PORT_INTERNAL (internal)
Database: $AGENT_MEMORY_DB_NAME
Username: $AGENT_MEMORY_DB_USERNAME
Password: $AGENT_MEMORY_DB_PASSWORD
```

> Credentials stored in `.env` file

## Connection String (for n8n nodes)

```
postgresql://$AGENT_MEMORY_DB_USERNAME:$AGENT_MEMORY_DB_PASSWORD@$AGENT_MEMORY_DB_HOST:$AGENT_MEMORY_DB_PORT_INTERNAL/$AGENT_MEMORY_DB_NAME
```

## Agent Memory Table Structure

```sql
Table: n8n_chat_histories

Columns:
- id          (integer, PRIMARY KEY, auto-increment)
- session_id  (varchar(255), NOT NULL)
- message     (jsonb, NOT NULL)
- created_at  (time with timezone, default CURRENT_TIMESTAMP)

Index: n8n_chat_histories_pkey (btree on id)
```

## Management Commands

```bash
# Source environment variables first
source .env

# Access agent memory database
sudo docker exec -it $AGENT_MEMORY_CONTAINER_ID psql -U $AGENT_MEMORY_DB_USERNAME

# List tables
sudo docker exec $AGENT_MEMORY_CONTAINER_ID psql -U $AGENT_MEMORY_DB_USERNAME -c "\dt"

# View chat history sessions
sudo docker exec $AGENT_MEMORY_CONTAINER_ID psql -U $AGENT_MEMORY_DB_USERNAME -c "SELECT DISTINCT session_id FROM n8n_chat_histories;"

# Count messages per session
sudo docker exec $AGENT_MEMORY_CONTAINER_ID psql -U $AGENT_MEMORY_DB_USERNAME -c "SELECT session_id, COUNT(*) FROM n8n_chat_histories GROUP BY session_id;"

# View recent messages
sudo docker exec $AGENT_MEMORY_CONTAINER_ID psql -U $AGENT_MEMORY_DB_USERNAME -c "SELECT * FROM n8n_chat_histories ORDER BY id DESC LIMIT 10;"

# Clear all chat history (DESTRUCTIVE)
sudo docker exec $AGENT_MEMORY_CONTAINER_ID psql -U $AGENT_MEMORY_DB_USERNAME -c "TRUNCATE n8n_chat_histories RESTART IDENTITY;"

# Delete specific session
sudo docker exec $AGENT_MEMORY_CONTAINER_ID psql -U $AGENT_MEMORY_DB_USERNAME -c "DELETE FROM n8n_chat_histories WHERE session_id = 'SESSION_ID_HERE';"
```

## Data Volume

```
postgres-data-$AGENT_MEMORY_CONTAINER_ID
```

---

*Documentation generated: 2026-01-18*
