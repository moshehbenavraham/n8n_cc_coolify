# TLS Incident and Domain Audit - 2026-03-16

Server: See `.env` for server details | OS: Ubuntu 24.04 LTS

---

## Scope

This note captures the operational work completed on 2026-03-16 for:

- `n8n.aiwithapex.com` returning Cloudflare `526`
- Traefik ACME state in `coolify-proxy`
- Orphaned certificate renewal noise
- Public subdomains that still terminate TLS but no longer map to active Coolify resources

---

## Executive Summary

### Primary incident

`https://n8n.aiwithapex.com/` was returning Cloudflare `526`.

The root cause was not Cloudflare WAF or bot protection. Traefik was routing the request to n8n correctly, but the origin certificate state for `n8n.aiwithapex.com` was corrupt:

- `127.0.0.1:443` with SNI `n8n.aiwithapex.com` initially served `TRAEFIK DEFAULT CERT`
- Traefik `acme.json` contained two entries keyed as `n8n.aiwithapex.com`
- Both stored certificates were actually issued for the old hostname `n8n-apex.aiwithapex.com`

That mismatch caused Cloudflare strict TLS to fail.

### Fix applied

- Backed up Traefik ACME storage:
  - `/data/coolify/proxy/acme.json.bak-20260316T135542Z`
- Removed only the broken `n8n.aiwithapex.com` ACME entries from Traefik storage
- Restarted `coolify-proxy`
- Forced a fresh TLS handshake for `n8n.aiwithapex.com`

Traefik then issued a fresh Let's Encrypt certificate with:

- Subject: `CN = n8n.aiwithapex.com`
- Issuer: `Let's Encrypt R13`
- Validity: `2026-03-16 12:58:07 GMT` to `2026-06-14 12:58:06 GMT`

### Secondary cleanup

An unrelated orphaned certificate for `voiceaibonanza.com` was still present in Traefik ACME storage and was causing repeated renewal failures. There was no active router for that hostname on this server.

- Backup created:
  - `/data/coolify/proxy/acme.json.bak-voice-20260316T141238Z`
- Removed the stale `voiceaibonanza.com` ACME entry

This stopped the active renewal noise without affecting live services on this server.

---

## Key Findings

### 1. n8n routing was healthy before TLS was healthy

Direct origin checks showed that Traefik was routing `n8n.aiwithapex.com` to the application even while TLS was wrong:

```bash
curl -k -I --resolve n8n.aiwithapex.com:443:127.0.0.1 https://n8n.aiwithapex.com/
```

This returned `HTTP/2 200` before the certificate problem was fixed. The failure was certificate presentation, not application reachability.

### 2. Coolify domain metadata was mixed but not the direct blocker

Coolify database state for application `obsidian-forge-n8n` showed:

- `applications.fqdn` blank
- `applications.docker_compose_domains` populated with `https://n8n.aiwithapex.com`
- Correct Traefik labels on the live n8n container

This meant the router configuration existed even though one metadata field looked stale.

### 3. Cloudflare / DNS were not the active cause of the n8n outage

During the incident:

- public HTTP for `n8n.aiwithapex.com` reached origin successfully
- the host had global IPv6 configured
- ports `80` and `443` were listening on both IPv4 and IPv6

No Cloudflare DNS change was required to fix the incident.

### 4. Traefik audits must include both Docker and file-provider routes

`coolify.aiwithapex.com` is routed from Traefik dynamic file configuration, not only Docker labels. Any future "ACME store vs current routes" audit must account for:

- Docker-provided routes from container labels
- file-provider routes under `/data/coolify/proxy/dynamic/`

### 5. Not all "extra" certificates are safe to remove

The following hostnames currently have valid origin certificates and public DNS pointing at this server, but no active Coolify applications or services were found for them during this session:

- `baseagent.aiwithapex.com`
- `crawl4ai.aiwithapex.com`
- `flowise.aiwithapex.com`
- `meilisearch.aiwithapex.com`
- `opensearch.aiwithapex.com`
- `searchxng.aiwithapex.com`

Public HTTPS for these hostnames currently returns `503`, not `526`, because Traefik still has valid matching certificates for them.

Do **not** remove those certificates blindly. If removed while DNS still points at this server, Cloudflare strict TLS would likely change those hostnames from `503` to `526`.

These need an intent decision:

- redeploy or restore the backing services, or
- remove/repoint their DNS records

### 6. Some earlier proxy errors were historical only

Historical errors were found in `coolify-proxy` logs for:

- `status.aiwithapex.com` ACME failures while DNS was missing
- Diamond Mine using the wrong middleware / certificate resolver names on 2026-03-09 and 2026-03-10

Current checks during this session showed:

- `status.aiwithapex.com` now serves a valid Let's Encrypt origin certificate
- `skool.aiwithapex.com` serves a valid Let's Encrypt origin certificate
- `skool-api.aiwithapex.com` is reachable; a `404` at `/` is application behavior, not TLS failure

No additional fix was required for those items during this session.

---

## Verification Commands

### Public status check

```bash
curl -I https://n8n.aiwithapex.com/
```

Expected after the fix:

- no `526`
- `HTTP/2 200`

### Origin certificate check

```bash
echo | openssl s_client -connect 127.0.0.1:443 -servername n8n.aiwithapex.com 2>/dev/null | openssl x509 -noout -subject -issuer -dates
```

Expected after the fix:

- subject for `n8n.aiwithapex.com`
- Let's Encrypt issuer
- not `TRAEFIK DEFAULT CERT`

### Audit current routed domains from Docker labels

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

### Audit current ACME domains

```bash
docker exec coolify-proxy cat /traefik/acme.json > /tmp/acme.audit.full.json
jq -r '.letsencrypt.Certificates[] | [.domain.main] + (.domain.sans // []) | .[]' /tmp/acme.audit.full.json | sort -u
```

---

## Current Operational State After Session

As of 2026-03-16:

- `n8n.aiwithapex.com` is healthy over public HTTPS
- `n8n.aiwithapex.com` presents a valid Let's Encrypt origin certificate
- `voiceaibonanza.com` is no longer generating active Traefik renewal errors on this server
- no active Traefik certificate / middleware errors were found in the final post-fix log window

---

## Follow-Up Recommendations

### High priority

- Decide whether the `503` subdomains listed above should be restored or removed from DNS

### Good hygiene

- When auditing Traefik certs, compare ACME hostnames against:
  - Docker-routed hostnames
  - Traefik file-provider hostnames
- Keep the two ACME backup files until the next stable operating window:
  - `/data/coolify/proxy/acme.json.bak-20260316T135542Z`
  - `/data/coolify/proxy/acme.json.bak-voice-20260316T141238Z`

---

## Session Artifacts

- Main n8n ACME backup: `/data/coolify/proxy/acme.json.bak-20260316T135542Z`
- Orphan-cert cleanup backup: `/data/coolify/proxy/acme.json.bak-voice-20260316T141238Z`
