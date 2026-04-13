#!/usr/bin/env python3
"""
Apply tags to all deployed voice_ai workflows using direct database access.

The n8n public API v1 doesn't support updating workflow tags, so this script
uses PostgreSQL directly to insert tag associations.
"""

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# Tag IDs from workflow-index.md
TAGS = {
    # Parent tag
    "voice-ai": "UWjQVM4os19WtLu8",

    # Category tags
    "voice-agents": "s4r8s1vRiiWzJt1G",
    "speech-processing": "HOA6OdXgt8vhpemf",
    "messaging-bots": "lJ8hf3WiU2bSlRJK",
    "content-creation": "1uxOyzZsht9OIkFF",
    "business-automation": "NIBbB2W50ma4sLFU",
    "ai-assistants": "ZUE2fN0CLZoPBcNa",
    "utilities": "L53QZlJKyJHeajcE",

    # Platform tags
    "vapi": "zNiQsUuvQOZ9P0TB",
    "retell": "BW0dK8vklZ7pKlID",
    "twilio": "lLxLt8ZwYyoE4g6j",
    "elevenlabs": "jDlNTa5HnrptJUAn",
    "whisper": "lwmduhBeNcVyogNi",
    "telegram": "EQdXWLa65zK23wsb",
    "whatsapp": "fXQENEHAx4lteMH8",
    "slack": "T0qwVYgShehCPKTe",

    # Use case tags
    "booking-scheduling": "kD2nI6QrYKIUjlXH",
    "lead-generation": "vt2Zq8H97fqQVOC1",
    "notifications": "RRDbhLpoCabOUjHV",
    "video": "LOx99HmiWQLfYmw3",
    "podcast-audio": "fIiodwbaCRLgy0JJ",

    # Technology tags
    "tts": "8qM0l9XNrlwrEBnL",
    "stt": "rqtbJhO70yAqDHFp",
}

# Directory to tag mapping
DIRECTORY_TAG_MAPPING = {
    "01-voice-agents": ["voice-ai", "voice-agents"],
    "01-voice-agents/vapi": ["voice-ai", "voice-agents", "vapi"],
    "01-voice-agents/retell": ["voice-ai", "voice-agents", "retell"],
    "01-voice-agents/twilio": ["voice-ai", "voice-agents", "twilio"],

    "02-speech-processing": ["voice-ai", "speech-processing"],
    "02-speech-processing/elevenlabs": ["voice-ai", "speech-processing", "elevenlabs", "tts"],
    "02-speech-processing/whisper": ["voice-ai", "speech-processing", "whisper", "stt"],
    "02-speech-processing/other-tts": ["voice-ai", "speech-processing", "tts"],

    "03-messaging-bots": ["voice-ai", "messaging-bots"],
    "03-messaging-bots/telegram": ["voice-ai", "messaging-bots", "telegram"],
    "03-messaging-bots/whatsapp": ["voice-ai", "messaging-bots", "whatsapp"],
    "03-messaging-bots/slack": ["voice-ai", "messaging-bots", "slack"],

    "04-content-creation": ["voice-ai", "content-creation"],
    "04-content-creation/video": ["voice-ai", "content-creation", "video"],
    "04-content-creation/podcast-audio": ["voice-ai", "content-creation", "podcast-audio"],

    "05-business-automation": ["voice-ai", "business-automation"],
    "05-business-automation/booking-scheduling": ["voice-ai", "business-automation", "booking-scheduling"],
    "05-business-automation/lead-generation": ["voice-ai", "business-automation", "lead-generation"],
    "05-business-automation/notifications": ["voice-ai", "business-automation", "notifications"],

    "06-ai-assistants": ["voice-ai", "ai-assistants"],

    "07-utilities": ["voice-ai", "utilities"],
}


def load_env():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    if key not in os.environ:
                        os.environ[key] = value


def run_sql(query):
    """Execute SQL query in n8n PostgreSQL container."""
    cmd = [
        "docker", "exec", "n8n-postgres",
        "psql", "-U", "n8n", "-d", "n8n", "-t", "-c", query
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"SQL Error: {result.stderr}")
        return None
    return result.stdout.strip()


def get_config():
    """Get n8n configuration from environment."""
    url = os.environ.get("N8N_LOCAL_URL") or os.environ.get("N8N_URL")
    api_key = os.environ.get("N8N_API_KEY")

    if not url or not api_key:
        print("Error: N8N_LOCAL_URL or N8N_URL, and N8N_API_KEY, must be set")
        sys.exit(1)

    return {"base_url": url.rstrip("/"), "api_key": api_key}


def parse_deploy_log(log_path):
    """Parse deploy log to get workflow name -> ID mapping."""
    mapping = {}
    with open(log_path) as f:
        for line in f:
            match = re.match(r"SUCCESS: (.+) \(ID: ([^)]+)\)", line.strip())
            if match:
                name = match.group(1)
                workflow_id = match.group(2)
                mapping[name] = workflow_id
    return mapping


def fetch_live_workflow_ids(config):
    """Fetch workflow name -> ID mapping from the live n8n instance."""
    mapping = {}
    next_cursor = None

    while True:
        query = {"limit": 250}
        if next_cursor:
            query["cursor"] = next_cursor

        url = (
            f"{config['base_url']}/api/v1/workflows?"
            f"{urllib.parse.urlencode(query)}"
        )
        request = urllib.request.Request(
            url,
            headers={"X-N8N-API-KEY": config["api_key"]},
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            print(f"Error: Failed to fetch live workflows - {exc}")
            sys.exit(1)

        for workflow in payload.get("data", []):
            name = workflow.get("name")
            workflow_id = workflow.get("id")
            if name and workflow_id and name not in mapping:
                mapping[name] = workflow_id

        next_cursor = payload.get("nextCursor")
        if not next_cursor:
            return mapping


def build_name_to_path_mapping(workflow_dir):
    """Build mapping from workflow name to file path (relative to workflows dir)."""
    mapping = {}

    for json_file in Path(workflow_dir).rglob("*.json"):
        try:
            with open(json_file) as f:
                data = json.load(f)

            name = None
            if isinstance(data, dict):
                if "workflow" in data and isinstance(data["workflow"], dict):
                    name = data["workflow"].get("name")
                if not name:
                    name = data.get("name")

            if name:
                rel_path = json_file.relative_to(workflow_dir)
                dir_path = str(rel_path.parent)
                mapping[name] = dir_path
        except Exception:
            pass

    return mapping


def get_tags_for_directory(dir_path):
    """Get tag names for a given directory path."""
    dir_path = dir_path.replace("\\", "/")

    if dir_path in DIRECTORY_TAG_MAPPING:
        return DIRECTORY_TAG_MAPPING[dir_path]

    parts = dir_path.split("/")
    if len(parts) >= 1:
        parent = parts[0]
        if parent in DIRECTORY_TAG_MAPPING:
            return DIRECTORY_TAG_MAPPING[parent]

    return ["voice-ai"]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Apply tags to deployed voice_ai workflows via database")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--limit", type=int, help="Limit number of workflows to process")
    args = parser.parse_args()

    load_env()
    config = get_config()

    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    deploy_log = script_dir / "deploy_log.txt"
    workflow_dir = project_root / "voice_ai" / "workflows"

    if not workflow_dir.exists():
        print(f"Error: Workflow directory not found at {workflow_dir}")
        sys.exit(1)

    # Test database connection
    print("Testing database connection...")
    test_result = run_sql("SELECT count(*) FROM tag_entity")
    if test_result is None:
        print("Error: Cannot connect to database")
        sys.exit(1)
    print(f"Connected. Found {test_result.strip()} tags in database.")

    deploy_log_mapping = {}
    if deploy_log.exists():
        print("Parsing deploy log...")
        deploy_log_mapping = parse_deploy_log(deploy_log)
        print(f"Found {len(deploy_log_mapping)} workflows in deploy log")
    else:
        print(f"Deploy log not found at {deploy_log}, skipping log bootstrap")

    print("Fetching live workflow list...")
    live_mapping = fetch_live_workflow_ids(config)
    print(f"Found {len(live_mapping)} workflows in n8n")

    print("Building name to path mapping...")
    name_to_path = build_name_to_path_mapping(workflow_dir)
    print(f"Found {len(name_to_path)} workflow files")

    name_to_id = dict(deploy_log_mapping)
    name_to_id.update(live_mapping)

    missing_from_log = sorted(set(name_to_path) - set(deploy_log_mapping))
    if deploy_log_mapping and missing_from_log:
        print(f"Deploy log is missing {len(missing_from_log)} workflow(s); using live API IDs for them")

    # Build SQL statements
    sql_statements = []
    processed = 0
    skipped = 0

    for name in sorted(name_to_path):
        if args.limit and processed >= args.limit:
            break

        processed += 1

        workflow_id = name_to_id.get(name)
        if not workflow_id:
            skipped += 1
            continue

        dir_path = name_to_path.get(name)
        if not dir_path:
            skipped += 1
            continue

        tag_names = get_tags_for_directory(dir_path)
        tag_ids = [TAGS[t] for t in tag_names if t in TAGS]

        for tag_id in tag_ids:
            # Use INSERT ... ON CONFLICT DO NOTHING for idempotency
            sql = f"INSERT INTO workflows_tags (\"workflowId\", \"tagId\") VALUES ('{workflow_id}', '{tag_id}') ON CONFLICT DO NOTHING"
            sql_statements.append((name, workflow_id, tag_names, sql))

    print(f"\nGenerated {len(sql_statements)} tag associations for {processed - skipped} workflows")
    print("-" * 80)

    if args.dry_run:
        # Show sample of what would be done
        seen_workflows = set()
        for name, wf_id, tags, sql in sql_statements[:50]:
            if wf_id not in seen_workflows:
                print(f"DRY-RUN: {name[:50]}...")
                print(f"         Tags: {', '.join(tags)}")
                seen_workflows.add(wf_id)
        if len(sql_statements) > 50:
            print(f"... and {len(sql_statements) - 50} more tag associations")
        print("-" * 80)
        print("(Dry run - no changes made)")
        return

    # Execute SQL statements
    success = 0
    failed = 0

    print("Applying tags...")

    # Batch the SQL statements for efficiency
    batch_size = 100
    for i in range(0, len(sql_statements), batch_size):
        batch = sql_statements[i:i + batch_size]
        combined_sql = "; ".join(sql for _, _, _, sql in batch)

        result = run_sql(combined_sql)
        if result is not None:
            success += len(batch)
        else:
            # Try individual statements if batch fails
            for name, wf_id, tags, sql in batch:
                if run_sql(sql) is not None:
                    success += 1
                else:
                    failed += 1
                    print(f"FAIL: {name[:50]}...")

        # Progress update
        print(f"Progress: {min(i + batch_size, len(sql_statements))}/{len(sql_statements)}")

    print("-" * 80)
    print(f"\nResults: {success} tag associations created, {failed} failed, {skipped} workflows skipped")


if __name__ == "__main__":
    main()
