# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Important Rules / Notes

 - If you have SUDO access, use it carefully
 - If committing or pushing to repo, do NOT add attributions and do NOT add co-authors
 - ASCII UTF-8 LF only
 = Never make up URLs (you have webtools to verify!)
 - Never make assumptions
 - Do not be lazy or take shortcuts
 - Pattern match precisely
 - Validate systematically

## Project Overview

This is a resource project to enable you to build, edit, and debug n8n workflows.  It includes specialized n8n MCP servers, specialized n8n Skills, and infrastructure documentation for a local WSL2 Ubuntu Docker + ngrok n8n stack.

**Actual Deployment**: The n8n Docker stack runs at `$N8N_DEPLOYMENT_PATH` (see .env) - you can directly access this as needed for reference/information but should not edit.

**Documentation**: See `docs/` folder (index: `docs/README_docs.md`)

**Credentials**: All credentials stored in `.env` file (source it before running commands)

## n8n MCP Server

An MCP server is connected to `$N8N_URL` (see .env) providing programmatic workflow management.

**Documentation Tools** (7): `search_nodes`, `get_node`, `validate_node`, `validate_workflow`, `get_template`, `search_templates`, `tools_documentation`

**Management Tools** (13): `n8n_create_workflow`, `n8n_get_workflow`, `n8n_update_full_workflow`, `n8n_update_partial_workflow`, `n8n_delete_workflow`, `n8n_list_workflows`, `n8n_validate_workflow`, `n8n_autofix_workflow`, `n8n_test_workflow`, `n8n_executions`, `n8n_health_check`, `n8n_workflow_versions`, `n8n_deploy_template`

**Capabilities**: Create/read/update/delete workflows, search 500+ nodes, validate configurations, deploy templates, view execution history, auto-fix common issues, trigger webhook/form/chat workflows.

## n8n Instance MCP

An official lightweight MCP server for direct workflow interaction via n8n's API.

**Tools** (3): `search_workflows`, `get_workflow_details`, `execute_workflow`

**Capabilities**: List/search workflows, get full workflow details with trigger info, execute workflows (webhook/form/chat triggers). Requires `availableInMCP: true` in workflow settings.

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

**Deployment Path**: `$N8N_DEPLOYMENT_PATH` (see .env)

The n8n stack runs locally via Docker Compose in WSL2 Ubuntu. Public access is provided via ngrok tunnel.

**GitHub Repo**: `moshehbenavraham/n8n-aiwithapex` (branch: `main`)

## Scripts

Utility scripts in `scripts/` folder (run from project root, source `.env` first):

| Script | Purpose |
|--------|---------|
| `upgrade_node_versions.sh` | Batch upgrade node typeVersions across workflows. Usage: `./scripts/upgrade_node_versions.sh [preview\|apply] [workflow_id\|all]` |
| `fix_and_deploy_workflows.sh` | Clean non-standard node properties and deploy workflows. Fixes "additional properties" API errors. |
| `deploy_voice_ai_workflows.sh` | Bulk deploy all workflows from `voice_ai/workflows/` directory |
| `deploy_remaining.sh` | Resume interrupted deployment (skips already-deployed workflows) |
| `n8n_tags.py` | Tag management CLI: list, create, delete, rename tags (Community Edition) |
| `n8n_projects.py` | Project management CLI (Enterprise only) |

## Project-Specific Rules

- Container management uses standard `docker compose` commands
- Run commands from the deployment directory: `cd $N8N_DEPLOYMENT_PATH`
- Source `.env` before running database commands
