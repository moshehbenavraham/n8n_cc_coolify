# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Important Rules / Notes

 - You have SUDO access, use it carefully
 - If committing or pushing to repo, do NOT add attributions and do NOT add co-authors
 - ASCII UTF-8 LF only
 - Never make assumptions
 - Do not be lazy or take shortcuts
 - Pattern match precisely
 - Validate systematically

## Project Overview

This is an infrastructure documentation project for a production Coolify + n8n + PostgreSQL stack. Server details are in the .env file.

**Documentation**: See `docs/` folder (index: `docs/README_docs.md`)

**Credentials**: All credentials stored in `.env` file (source it before running commands)

## n8n MCP Server

An MCP server is connected to `$N8N_URL` (see .env) providing programmatic workflow management.

**Documentation Tools** (7): `search_nodes`, `get_node`, `validate_node`, `validate_workflow`, `get_template`, `search_templates`, `tools_documentation`

**Management Tools** (13): `n8n_create_workflow`, `n8n_get_workflow`, `n8n_update_full_workflow`, `n8n_update_partial_workflow`, `n8n_delete_workflow`, `n8n_list_workflows`, `n8n_validate_workflow`, `n8n_autofix_workflow`, `n8n_test_workflow`, `n8n_executions`, `n8n_health_check`, `n8n_workflow_versions`, `n8n_deploy_template`

**Capabilities**: Create/read/update/delete workflows, search 500+ nodes, validate configurations, deploy templates, view execution history, auto-fix common issues, trigger webhook/form/chat workflows.

## n8n Skills

Seven specialized skills provide expert guidance for n8n workflow development:

| Skill | Purpose |
|-------|---------|
| `n8n-expression-syntax` | Expression format `{{$json.body.field}}`, webhook data access, common mistakes |
| `n8n-validation-expert` | Validation profiles, error interpretation, validate-fix loop |
| `n8n-workflow-patterns` | 5 core patterns: Webhook, HTTP API, Database, AI Agent, Scheduled |
| `n8n-code-javascript` | Code nodes: `$input.all()`, `$helpers.httpRequest()`, DateTime |
| `n8n-code-python` | Python Code nodes (beta): `_input.all()`, see Python Libraries below |
| `n8n-mcp-tools-expert` | MCP tool usage, nodeType formats, smart parameters |
| `n8n-node-configuration` | Operation-aware config, property dependencies, detail levels |

**Key Rules**: Webhook data under `$json.body`, Code nodes return `[{json:{...}}]`, nodeType `nodes-base.*` for search/validate vs `n8n-nodes-base.*` for workflows.

---

## Python Code Node Libraries

**NOT JUST STANDARD LIBRARY** - n8n Python Code nodes use Pyodide (WebAssembly) which includes **200+ packages**:

**Data Science**: `numpy`, `pandas`, `scipy`, `scikit-learn`, `scikit-image`, `xarray`

**Visualization**: `matplotlib`, `bokeh`, `plotly`

**ML/AI**: `lightgbm`, `xgboost`

**Web/HTTP**: `aiohttp`, `fastapi`, `requests` (via pyodide-http)

**Geospatial**: `geopandas`, `rasterio`, `Cartopy`

Packages load at runtime. Full list: https://pyodide.org/en/stable/usage/packages-in-pyodide.html

---

## Deployment

**GitHub Repo**: `moshehbenavraham/n8n-aiwithapex` (branch: `main`)

Commits to `main` automatically trigger Coolify to rebuild and deploy the n8n stack. The repo contains `docker-compose.coolify.yml` and related configuration.

## Project-Specific Rules

- Use Coolify dashboard or API for deployments when possible
- Avoid manual Docker changes that bypass Coolify
- Container IDs change on redeployment; verify with `docker ps`
- Source `.env` before running database commands
