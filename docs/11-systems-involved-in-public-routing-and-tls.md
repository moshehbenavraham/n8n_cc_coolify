# Systems Involved in Public Routing and TLS

Server: See `.env` for server details | OS: Ubuntu 24.04 LTS

---

## Purpose

This document is a structured reference for the systems involved in the public request path for `n8n.aiwithapex.com` and related Coolify-managed hostnames.

It is intended to answer:

- which systems are in the path
- what each system is responsible for
- where routing and TLS state actually lives
- which checks distinguish DNS, proxy, TLS, and application failures

State in this document reflects the environment observed on 2026-03-16.

---

## High-Level Flow

```text
Client / Webhook Sender
    |
Cloudflare DNS + Proxy
    |
Server network stack / UFW
    |
coolify-proxy (Traefik)
    |\
    | +-- File provider routes from /data/coolify/proxy/dynamic/
    |
    +-- Docker provider routes from container labels
           |
           +-- Coolify-managed app containers
                  |
                  +-- n8n main container
                  +-- n8n workers / runners
                  +-- n8n Postgres
                  +-- n8n Redis
```

---

## System Inventory

| System | Where It Runs | Primary Responsibility | Key State / Config |
|---|---|---|---|
| Cloudflare | External | Public DNS, proxying, strict TLS validation at edge | DNS records, orange-cloud proxy mode, edge behavior |
| Host networking / UFW | VPS host | Accept traffic on `80/443`, expose Docker-published ports | Host IPs, firewall rules, listeners |
| Coolify app | `coolify` container | Control plane for apps, domains, deployments | Coolify DB, app metadata, generated deployment configs |
| Coolify DB | `coolify-db` container | Stores app, service, domain, and certificate metadata | Tables such as `applications`, `services`, `ssl_certificates` |
| Traefik proxy | `coolify-proxy` container | TLS termination, HTTP routing, ACME certificate issuance | `/data/coolify/proxy/acme.json`, `/data/coolify/proxy/dynamic/` |
| Traefik Docker provider | Docker socket | Builds live routes from container labels | Live container labels on running containers |
| Traefik file provider | `/data/coolify/proxy/dynamic/` | Provides static/dynamic routes outside Docker labels | `coolify.yaml` and related dynamic config files |
| n8n main app | `n8n-*` container | UI, webhooks, API, workflow orchestration | Container labels, environment, `/home/node/.n8n` volume |
| n8n workers / runners | `n8n-worker-*`, `runner-worker-*` containers | Background execution and runner workloads | Queue mode runtime state |
| n8n Postgres | `postgres-*` container | n8n application database | Workflow, execution, credential, settings data |
| n8n Redis | `redis-*` container | Queue transport / coordination for n8n | Redis queue state |

---

## Current Runtime Components

Observed on 2026-03-16:

- Coolify image: `ghcr.io/coollabsio/coolify:4.0.0-beta.463`
- Traefik image: `traefik:latest`
- n8n image: `n8nio/n8n:latest`
- n8n Postgres image: `postgres:16.11-alpine`
- n8n Redis image: `redis:7.4.7-alpine`

Key running containers involved in this path:

- `coolify`
- `coolify-db`
- `coolify-redis`
- `coolify-realtime`
- `coolify-proxy`
- `n8n-b0so00sgcw0ccg0kksg0ocg4-*`
- `n8n-worker-1/2-b0so00sgcw0ccg0kksg0ocg4-*`
- `runner-worker-1/2-b0so00sgcw0ccg0kksg0ocg4-*`
- `postgres-b0so00sgcw0ccg0kksg0ocg4-*`
- `redis-b0so00sgcw0ccg0kksg0ocg4-*`

---

## Source of Truth by Concern

| Concern | Primary Source of Truth | Notes |
|---|---|---|
| Public hostname resolution | Cloudflare DNS | `dig` answers reflect what the internet sees |
| Whether Cloudflare can validate origin TLS | Origin certificate actually served by Traefik | This is what drives Cloudflare `526` |
| Live Docker-routed hostnames | Running container labels | Derived from `traefik.http.routers.*.rule` and `caddy_0` labels |
| Live file-provider hostnames | `/data/coolify/proxy/dynamic/` | Important for `coolify.aiwithapex.com` and other non-Docker routes |
| Current ACME cert inventory | `/data/coolify/proxy/acme.json` | This is the actual Let's Encrypt storage Traefik uses |
| App/domain metadata in Coolify | `coolify-db` | Helpful for intent and deployment state, but not always the immediate runtime truth |
| n8n app health | n8n container + direct origin requests | Routing can be healthy while TLS is broken |

---

## Critical Files and Paths

| Path | Purpose |
|---|---|
| `/data/coolify/proxy/acme.json` | Traefik ACME certificate storage used for origin TLS |
| `/data/coolify/proxy/dynamic/` | Traefik file-provider routing configuration |
| `/data/coolify/proxy/docker-compose.yml` | Proxy stack definition |
| `/data/coolify/source/docker-compose.yml` | Coolify control-plane compose file |
| `/var/run/docker.sock` | Docker provider input for Traefik |
| `/data/coolify/ssl/` | Coolify SSL/CA assets; not the main Let's Encrypt ACME store for Traefik in this setup |
| `/var/lib/docker/volumes/<n8n-id>_n8n-data/_data` | Persistent n8n app data |
| `/artifacts/.../docker-compose.coolify.yml` | Coolify-generated compose for deployed app instances |

---

## Request Path Responsibilities

### 1. Cloudflare

Cloudflare is responsible for:

- resolving public DNS
- proxying public HTTP/S traffic when records are orange-clouded
- validating the origin certificate when strict TLS is enabled

Cloudflare is **not** the place to debug first when the symptom is `526`. A `526` means origin TLS validation failed, so the first meaningful check is the certificate Traefik is serving for the requested SNI.

### 2. Traefik

Traefik is the runtime TLS and routing boundary on this server.

Responsibilities:

- answer on `:80` and `:443`
- issue and renew Let's Encrypt certificates
- select a certificate by SNI
- route requests to the correct container based on host rules

Relevant runtime configuration observed:

- file provider enabled from `/traefik/dynamic/`
- Docker provider enabled
- ACME HTTP challenge enabled on the `http` entrypoint
- ACME storage at `/traefik/acme.json`

### 3. Coolify

Coolify defines intent and deployment state.

Responsibilities:

- track apps, services, and domains
- generate deployment artifacts
- attach labels and settings that Traefik later consumes

Important operational point:

Coolify metadata can be partly stale while runtime routing still works. During the 2026-03-16 incident, the `obsidian-forge-n8n` application had a blank `applications.fqdn` value, but the actual live n8n container still had the correct Traefik labels for `n8n.aiwithapex.com`.

### 4. n8n Stack

The n8n stack is the application target behind Traefik.

Responsibilities:

- serve UI and API
- handle public webhooks
- execute workflows through workers/runners
- persist workflow and execution state in Postgres
- use Redis for queue mode

Important operational point:

Application routing can be correct even when TLS is broken. During the incident, direct origin requests routed to n8n successfully while the wrong certificate was being served.

---

## Quick Diagnostic Matrix

| Symptom | Most Likely Layer | First Checks |
|---|---|---|
| `526` from Cloudflare | Origin TLS / Traefik cert selection | `curl -I https://host`, then `openssl s_client -connect 127.0.0.1:443 -servername host` |
| `503` from public hostname | Traefik route exists but backend service missing/unhealthy | public `curl`, then inspect current routers / running containers |
| `404` from app hostname | Often app behavior, not TLS | compare public `404` with direct origin `404` |
| `NXDOMAIN` in Traefik ACME logs | DNS missing or wrong | `dig A` and `dig AAAA` for hostname |
| Direct origin returns `TRAEFIK DEFAULT CERT` | No matching cert selected for that SNI | inspect `/data/coolify/proxy/acme.json` and current routers |
| Host routes correctly with `curl -k --resolve`, but public path fails | TLS mismatch more likely than app/routing failure | compare direct origin behavior and public behavior |

---

## Core Commands

### Public edge check

```bash
curl -I https://n8n.aiwithapex.com/
```

### Direct origin certificate check

```bash
echo | openssl s_client -connect 127.0.0.1:443 -servername n8n.aiwithapex.com 2>/dev/null | openssl x509 -noout -subject -issuer -dates
```

### Direct origin route check ignoring certificate validity

```bash
curl -k -I --resolve n8n.aiwithapex.com:443:127.0.0.1 https://n8n.aiwithapex.com/
```

### Current ACME hostname inventory

```bash
docker exec coolify-proxy cat /traefik/acme.json > /tmp/acme.audit.full.json
jq -r '.letsencrypt.Certificates[] | [.domain.main] + (.domain.sans // []) | .[]' /tmp/acme.audit.full.json | sort -u
```

### Current Docker-routed hostnames

```bash
docker ps -q | xargs -r docker inspect > /tmp/docker_inspect_running.json
jq -r '.[].Config.Labels // {} | to_entries[]? |
  if .key=="caddy_0" then
    .value | sub("^https?://"; "") | split("/")[0]
  elif (.key|test("^traefik\\.http\\.routers\\..*\\.rule$")) then
    .value | capture("Host\\(`(?<h>[^`]+)`\\)").h
  else
    empty
  end' /tmp/docker_inspect_running.json | sort -u
```

### Current Traefik proxy logs

```bash
docker logs coolify-proxy --tail 200
```

---

## Operational Guardrails

### 1. Do not equate "extra cert in ACME" with "safe to delete"

A certificate can still be operationally important even when no current Coolify app record is easy to find. If DNS still points at this server and Traefik still presents that cert, removing it can convert a public `503` into a Cloudflare `526`.

### 2. Audit both runtime routing and DNS before removing certs

Before deleting a cert entry from `acme.json`, confirm:

- the hostname is not present in current Docker routes
- the hostname is not present in Traefik file-provider routes
- the hostname does not still have public DNS pointing at this server
- the hostname is not expected to remain TLS-valid while a backend is temporarily absent

### 3. Back up `acme.json` before any manual edit

Always create a timestamped backup of `/data/coolify/proxy/acme.json` before removing entries.

---

## Known State from 2026-03-16 Audit

### Confirmed good / active

- `n8n.aiwithapex.com`
- `coolify.aiwithapex.com`
- `status.aiwithapex.com`
- `skool.aiwithapex.com`
- `skool-api.aiwithapex.com`
- `nocodb.aiwithapex.com`
- `pwz.aiwithapex.com`
- `appflowy.aiwithapex.com`
- `appflowy-web.aiwithapex.com`
- `appflowy-admin.aiwithapex.com`

### Confirmed stale and removed from ACME

- `voiceaibonanza.com`

### DNS-live hostnames with valid TLS but currently returning `503`

- `baseagent.aiwithapex.com`
- `crawl4ai.aiwithapex.com`
- `flowise.aiwithapex.com`
- `meilisearch.aiwithapex.com`
- `opensearch.aiwithapex.com`
- `searchxng.aiwithapex.com`

These should be treated as product or DNS decisions, not just certificate cleanup candidates.

---

## Related Documents

- `06-network-topology.md`
- `04-troubleshooting.md`
- `10-tls-incident-and-domain-audit-2026-03-16.md`
