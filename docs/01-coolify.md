# Coolify

Server: See .env for server details | OS: Ubuntu 24.04 LTS

---

## Overview

- **Version**: 4.0.0-beta.460
- **Container**: `coolify`
- **Data Directory**: `/data/coolify`

## Access

```
URL: https://coolify.aiwithapex.com
```

## Container Architecture

```
coolify              - Main application (port 8080)
coolify-db           - PostgreSQL 15 (Coolify internal DB)
coolify-redis        - Redis cache
coolify-realtime     - WebSocket server (ports 6001-6002)
coolify-proxy        - Traefik reverse proxy (ports 80, 443, 8080)
```

## Coolify Database Credentials

```
Database: coolify-db container
Username: $COOLIFY_DB_USERNAME
Password: $COOLIFY_DB_PASSWORD
```

> Credentials stored in `.env` file

## Coolify API Configuration

```
# See .env file for credentials
COOLIFY_API_TOKEN=$COOLIFY_API_TOKEN
COOLIFY_API_URL=$COOLIFY_API_URL
```

## Key Directories

```
/data/coolify/
├── applications/    # Deployed apps
├── backups/         # Backup storage
├── databases/       # Database configs
├── proxy/           # Traefik configs
│   └── dynamic/     # Dynamic routing rules
├── services/        # Service definitions
├── source/          # Coolify source + .env
├── ssh/             # SSH keys
└── ssl/             # SSL certificates
```

## Management Commands

```bash
# View Coolify logs
sudo docker logs coolify -f

# Restart Coolify
sudo docker restart coolify

# Restart entire Coolify stack
sudo docker restart coolify coolify-db coolify-redis coolify-realtime coolify-proxy

# Access Coolify database
sudo docker exec -it coolify-db psql -U coolify

# View Traefik routing
sudo cat /data/coolify/proxy/dynamic/coolify.yaml
```

---

*Documentation generated: 2026-01-18*
