# Atlas - AI Executive Assistant Agent Workflow

Server: See .env for server details | OS: Ubuntu 24.04 LTS

---

## Overview

- **Workflow ID**: `$ATLAS_WORKFLOW_ID` (see .env)
- **URL**: `$N8N_URL/workflow/$ATLAS_WORKFLOW_ID`
- **Status**: Active
- **Created**: 2025-03-04
- **Last Updated**: 2026-01-18
- **Total Nodes**: 56

## Purpose

Atlas is an advanced AI Executive Assistant agent that provides:
- Workflow automation and task management
- Calendar management (Google Calendar)
- Contact management (Airtable)
- Email communications (Gmail)
- Voice calling via Vapi AI
- Knowledge base queries (Pinecone Vector DB)
- Web search (SerpAPI)
- Social media content relay
- Telegram-based user interface

## Architecture Flow

```
                                    +------------------+
                                    | Telegram Trigger |
                                    +--------+---------+
                                             |
                                    +--------v---------+
                                    |   Set Variables  |
                                    +--------+---------+
                                             |
                                    +--------v---------+
                                    |      Switch      |
                                    +--+-----+-----+---+
                                       |     |     |
              +------------------------+     |     +------------------------+
              |                              |                              |
     +--------v---------+         +----------v----------+         +---------v--------+
     | Get Audio File   |         | Label Output 'text' |         | Get Image File   |
     +--------+---------+         +----------+----------+         +---------+--------+
              |                              |                              |
     +--------v---------+                    |                    +---------v--------+
     | OpenAI Transcribe|                    |                    |  Analyze Image   |
     +--------+---------+                    |                    +---------+--------+
              |                              |                              |
     +--------v---------+                    |                    +---------v--------+
     | Revise Output    |                    |                    | Label Image      |
     +--------+---------+                    |                    +---------+--------+
              |                              |                              |
              +------------->+---------------v---------------+<-------------+
                             |          AI AGENT             |
                             |   (OpenAI gpt-5.2 Model)      |
                             +------+---------------+--------+
                                    |               |
                             +------v------+ +------v------+
                             | Chat Memory | | 15 AI Tools |
                             | (Postgres)  | +-------------+
                             +-------------+
                                    |
                             +------v-------------+
                             | Send to Telegram   |
                             +--------------------+

External Inputs:
+------------------+     +-------------------------+
| Webhook (Vapi)   |---->| Process Call Report     |---> AI Agent ---> Telegram + Gmail
+------------------+     +-------------------------+

+------------------+     +-------------------------+
| Social Media     |---->| Relay to AI Agent       |---> Telegram
| Agent Webhook    |     +-------------------------+
+------------------+
```

## Entry Points (Triggers)

| Trigger | Type | Description |
|---------|------|-------------|
| Telegram Trigger | telegramTrigger | Receives messages from Telegram |
| Webhook from Vapi | webhook | Receives AI voice call reports |
| Webhook from Social Media Agent | webhook | Receives social media content results |

## AI Agent Configuration

**Model**: OpenAI gpt-5.2
**Memory**: Postgres Chat Memory (session key: `memory_key_{{$workflow.id}}`)

**Connected Tools** (15 tools):

| Tool | Type | Purpose |
|------|------|---------|
| SerpAPI | Web Search | External information retrieval |
| Vector Store Tool | Knowledge Base | Query Pinecone vector database |
| Google Calendar Check | Calendar | Check availability and events |
| Google Calendar Create | Calendar | Create new calendar events |
| Notion Search ToDo | Task Management | Search existing todos |
| Notion Add to ToDo | Task Management | Create new todos |
| Voice Calling Agent | Communication | Initiate AI voice calls |
| Calculator | Utility | Mathematical calculations |
| Hacker News | Research | YCombinator news access |
| postgres_access_session_memory | Memory | Extended chat history access |
| Airtable Get Contacts | CRM | Retrieve contact information |
| Airtable Add Contact | CRM | Add new contacts |
| Gmail Check Messages | Email | Check inbox messages |
| Gmail Send Messages | Email | Send outbound emails |
| Social Media Agent | HTTP Tool | Relay social media requests |

## Input Types Handled

| Input Tag | Source | Processing |
|-----------|--------|------------|
| [[TEXT]] | Direct Telegram message | Pass to AI Agent |
| [[VOICE]] | Voice message | Transcribe via OpenAI -> AI Agent |
| [[IMAGE]] | Image attachment | Analyze via OpenAI Vision -> AI Agent |
| [[CALL_REPORT]] | Vapi webhook | Summarize -> AI Agent + Gmail |
| [[SOCIAL_MEDIA_AGENT]] | SMA webhook | Direct relay to AI Agent |

## Webhook Endpoints

See n8n UI for current webhook paths. Webhook UUIDs are auto-generated.

## System Message Summary

Atlas operates as Max/Mosheh's Executive Assistant with these principles:
- **Persistence**: Continue until user request is fully resolved
- **Tool Usage**: Always verify data via tools, never fabricate
- **Planning**: Step-by-step reasoning for complex tasks
- **Contact Validation**: NEVER guess email/phone - always verify via Airtable
- **Emergency Protocol**: Call verified contacts only, report location
- **Social Media**: Relay all content requests to Social Media Agent unchanged

## Output Format (Telegram)

- Default: Plain text
- Allowed HTML tags: `<b>`, `<i>`, `<code>`, `<pre>`, `<a>`
- Emails must be wrapped in `<code>` tags
- Escape special characters: `&`, `<`, `>`

## Call Report Format

```
A call took place on [YYYY-MM-DD], between Atlas (AI Executive Assistant)
calling from [phone] and [contact name] at [phone]. The call lasted
[XX.XXX] seconds (starting at [HH:MM:SS] and ending at [HH:MM:SS] UTC)
and ended when [reason]. The conversation resulted in [specific outcome].
The total cost of the call was $[X.XXXX]. Here is the recording: [URL].
```

## Integrations Required

| Service | Credential Type | Purpose |
|---------|-----------------|---------|
| OpenAI | API Key | LLM, transcription, vision |
| Telegram Bot | Bot Token | User interface |
| Google Calendar | OAuth2 | Calendar management |
| Gmail | OAuth2 | Email send/receive |
| Notion | API Key | Todo management |
| Airtable | API Key | Contact management |
| Pinecone | API Key | Vector knowledge base |
| SerpAPI | API Key | Web search |
| Vapi | Webhook | Voice calling integration |

## Management Commands

```bash
# Source environment variables first
source .env

# View workflow in database
sudo docker exec $(sudo docker ps -qf name=postgres-$N8N_NETWORK_ID) psql -U $N8N_DB_USERNAME -d n8n -c "SELECT id, name, active FROM workflow_entity WHERE id = '$ATLAS_WORKFLOW_ID';"

# Check workflow execution history
sudo docker exec $(sudo docker ps -qf name=postgres-$N8N_NETWORK_ID) psql -U $N8N_DB_USERNAME -d n8n -c "SELECT id, status, \"startedAt\", \"stoppedAt\" FROM execution_entity WHERE \"workflowId\" = '$ATLAS_WORKFLOW_ID' ORDER BY \"startedAt\" DESC LIMIT 10;"

# Deactivate workflow (emergency)
# Use Coolify dashboard or n8n UI - avoid direct DB modification
```

---

*Documentation generated: 2026-01-18*
