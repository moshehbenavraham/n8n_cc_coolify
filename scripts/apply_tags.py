#!/usr/bin/env python3
"""
Apply tags to all deployed voice_ai workflows based on their directory structure.

Tags are applied according to the mapping in voice_ai/workflow-index.md:
- All workflows get 'voice-ai' tag
- Category tags based on top-level directory (01-voice-agents, 02-speech-processing, etc.)
- Subcategory/platform tags based on subdirectory (vapi, retell, twilio, etc.)
"""

import json
import os
import re
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests")
    sys.exit(1)

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


def get_config():
    """Get n8n configuration from environment."""
    load_env()
    url = os.environ.get("N8N_LOCAL_URL") or os.environ.get("N8N_URL")
    api_key = os.environ.get("N8N_API_KEY")

    if not url or not api_key:
        print("Error: N8N_URL and N8N_API_KEY must be set")
        sys.exit(1)

    return {"base_url": url.rstrip("/"), "api_key": api_key}


def parse_deploy_log(log_path):
    """Parse deploy log to get workflow name -> ID mapping."""
    mapping = {}
    with open(log_path) as f:
        for line in f:
            # Format: SUCCESS: <name> (ID: <id>)
            match = re.match(r"SUCCESS: (.+) \(ID: ([^)]+)\)", line.strip())
            if match:
                name = match.group(1)
                workflow_id = match.group(2)
                mapping[name] = workflow_id
    return mapping


def build_name_to_path_mapping(workflow_dir):
    """Build mapping from workflow name to file path (relative to workflows dir)."""
    mapping = {}

    for json_file in Path(workflow_dir).rglob("*.json"):
        try:
            with open(json_file) as f:
                data = json.load(f)

            # Extract name from various JSON structures
            name = None
            if isinstance(data, dict):
                if "workflow" in data and isinstance(data["workflow"], dict):
                    name = data["workflow"].get("name")
                if not name:
                    name = data.get("name")

            if name:
                # Get relative path from workflows directory
                rel_path = json_file.relative_to(workflow_dir)
                # Get directory part (category/subcategory)
                dir_path = str(rel_path.parent)
                mapping[name] = dir_path
        except (json.JSONDecodeError, Exception) as e:
            print(f"Warning: Could not parse {json_file}: {e}")

    return mapping


def get_tags_for_directory(dir_path):
    """Get tag names for a given directory path."""
    # Normalize path separators
    dir_path = dir_path.replace("\\", "/")

    # Try exact match first
    if dir_path in DIRECTORY_TAG_MAPPING:
        return DIRECTORY_TAG_MAPPING[dir_path]

    # Try parent directory
    parts = dir_path.split("/")
    if len(parts) >= 1:
        parent = parts[0]
        if parent in DIRECTORY_TAG_MAPPING:
            return DIRECTORY_TAG_MAPPING[parent]

    # Default to voice-ai only
    return ["voice-ai"]


def tag_workflow(config, workflow_id, tag_ids):
    """Apply tags to a workflow using PUT with full workflow data."""
    url = f"{config['base_url']}/api/v1/workflows/{workflow_id}"
    headers = {
        "X-N8N-API-KEY": config["api_key"],
        "Content-Type": "application/json"
    }

    # First get current workflow
    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code != 200:
        return False, f"Failed to get workflow: HTTP {response.status_code}"

    workflow = response.json()

    # Merge existing tags with new tags
    existing_tag_ids = [t.get("id") for t in workflow.get("tags", [])]
    all_tag_ids = list(set(existing_tag_ids + tag_ids))

    # Build the update payload with required fields
    update_data = {
        "name": workflow.get("name"),
        "nodes": workflow.get("nodes", []),
        "connections": workflow.get("connections", {}),
        "settings": workflow.get("settings", {}),
        "tags": [{"id": tid} for tid in all_tag_ids]
    }

    # Use PUT for full workflow update
    response = requests.put(url, headers=headers, json=update_data, timeout=30)

    if response.status_code == 200:
        return True, None
    else:
        return False, f"HTTP {response.status_code}: {response.text[:100]}"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Apply tags to deployed voice_ai workflows")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--limit", type=int, help="Limit number of workflows to process")
    args = parser.parse_args()

    config = get_config()

    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    deploy_log = script_dir / "deploy_log.txt"
    workflow_dir = project_root / "voice_ai" / "workflows"

    if not deploy_log.exists():
        print(f"Error: Deploy log not found at {deploy_log}")
        sys.exit(1)

    if not workflow_dir.exists():
        print(f"Error: Workflow directory not found at {workflow_dir}")
        sys.exit(1)

    print("Parsing deploy log...")
    name_to_id = parse_deploy_log(deploy_log)
    print(f"Found {len(name_to_id)} deployed workflows")

    print("Building name to path mapping...")
    name_to_path = build_name_to_path_mapping(workflow_dir)
    print(f"Found {len(name_to_path)} workflow files")

    # Process workflows
    success = 0
    failed = 0
    skipped = 0
    processed = 0

    print("\nApplying tags...")
    print("-" * 80)

    for name, workflow_id in name_to_id.items():
        if args.limit and processed >= args.limit:
            break

        processed += 1

        # Find the directory path for this workflow
        dir_path = name_to_path.get(name)
        if not dir_path:
            print(f"[{processed}] SKIP: {name[:50]}... (no path mapping)")
            skipped += 1
            continue

        # Get tags for this directory
        tag_names = get_tags_for_directory(dir_path)
        tag_ids = [TAGS[t] for t in tag_names if t in TAGS]

        if args.dry_run:
            print(f"[{processed}] DRY-RUN: {name[:40]}...")
            print(f"         Path: {dir_path}")
            print(f"         Tags: {', '.join(tag_names)}")
            success += 1
        else:
            ok, error = tag_workflow(config, workflow_id, tag_ids)
            if ok:
                print(f"[{processed}] OK: {name[:50]}... -> {', '.join(tag_names)}")
                success += 1
            else:
                print(f"[{processed}] FAIL: {name[:50]}... - {error}")
                failed += 1

    print("-" * 80)
    print(f"\nResults: {success} success, {failed} failed, {skipped} skipped")

    if args.dry_run:
        print("\n(Dry run - no changes made)")


if __name__ == "__main__":
    main()
