#!/usr/bin/env python3
"""
n8n Tag Management CLI

Simple CLI tool to create and manage tags in n8n.
Tags are the organizational feature available in n8n Community Edition.

Usage:
    python n8n_tags.py list
    python n8n_tags.py create "My Tag"
    python n8n_tags.py delete <tag-id>
    python n8n_tags.py get <tag-id>
    python n8n_tags.py rename <tag-id> "New Name"

Environment variables (or use .env file):
    N8N_LOCAL_URL - Local URL (preferred, bypasses ngrok OAuth)
    N8N_URL - Base URL of your n8n instance
    N8N_API_KEY - Your n8n API key
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests")
    sys.exit(1)


def load_env():
    """Load environment variables from .env file if it exists."""
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

    # Prefer N8N_LOCAL_URL for direct access (bypasses ngrok OAuth)
    url = os.environ.get("N8N_LOCAL_URL") or os.environ.get("N8N_URL")
    api_key = os.environ.get("N8N_API_KEY")

    if not url:
        print("Error: N8N_URL or N8N_LOCAL_URL environment variable not set")
        sys.exit(1)
    if not api_key:
        print("Error: N8N_API_KEY environment variable not set")
        sys.exit(1)

    return {
        "base_url": url.rstrip("/"),
        "api_key": api_key
    }


def make_request(method, endpoint, data=None):
    """Make an authenticated request to the n8n API."""
    config = get_config()
    url = f"{config['base_url']}/api/v1{endpoint}"
    headers = {
        "X-N8N-API-KEY": config["api_key"],
        "Content-Type": "application/json"
    }

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data, timeout=30)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=30)
        else:
            print(f"Error: Unsupported HTTP method: {method}")
            sys.exit(1)

        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: Request failed - {e}")
        sys.exit(1)


def list_tags():
    """List all tags."""
    response = make_request("GET", "/tags")

    if response.status_code == 200:
        try:
            data = response.json()
        except Exception:
            print(f"Error parsing response: {response.text[:500]}")
            return

        # Handle both {data: [...]} and direct array responses
        if isinstance(data, list):
            tags = data
        else:
            tags = data.get("data", [])

        if not tags:
            print("No tags found.")
            return

        print(f"\n{'ID':<40} {'Name':<30} {'Workflows':<10}")
        print("-" * 80)
        for tag in tags:
            tag_id = tag.get("id", "N/A")
            name = tag.get("name", "N/A")
            # usageCount may or may not be present
            usage = tag.get("usageCount", "N/A")
            print(f"{tag_id:<40} {name:<30} {usage:<10}")
        print()
    else:
        print(f"Error: Failed to list tags (HTTP {response.status_code})")
        print(f"Response: {response.text[:500] if response.text else '(empty)'}")


def create_tag(name):
    """Create a new tag."""
    data = {"name": name}
    response = make_request("POST", "/tags", data)

    if response.status_code in (200, 201):
        result = response.json()
        print(f"Tag created successfully!")
        print(f"  ID:   {result.get('id', 'N/A')}")
        print(f"  Name: {result.get('name', 'N/A')}")
    else:
        print(f"Error: Failed to create tag (HTTP {response.status_code})")
        try:
            print(json.dumps(response.json(), indent=2))
        except Exception:
            print(response.text)


def get_tag(tag_id):
    """Get details of a specific tag."""
    response = make_request("GET", f"/tags/{tag_id}")

    if response.status_code == 200:
        result = response.json()
        print(f"\nTag Details:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: Failed to get tag (HTTP {response.status_code})")
        try:
            print(json.dumps(response.json(), indent=2))
        except Exception:
            print(response.text)


def delete_tag(tag_id):
    """Delete a tag."""
    response = make_request("DELETE", f"/tags/{tag_id}")

    if response.status_code in (200, 204):
        print(f"Tag {tag_id} deleted successfully!")
    else:
        print(f"Error: Failed to delete tag (HTTP {response.status_code})")
        try:
            print(json.dumps(response.json(), indent=2))
        except Exception:
            print(response.text)


def rename_tag(tag_id, new_name):
    """Rename a tag."""
    data = {"name": new_name}
    response = make_request("PATCH", f"/tags/{tag_id}", data)

    if response.status_code == 200:
        result = response.json()
        print(f"Tag renamed successfully!")
        print(f"  ID:   {result.get('id', 'N/A')}")
        print(f"  Name: {result.get('name', 'N/A')}")
    else:
        print(f"Error: Failed to rename tag (HTTP {response.status_code})")
        try:
            print(json.dumps(response.json(), indent=2))
        except Exception:
            print(response.text)


def tag_workflow(workflow_id, tag_ids):
    """Add tags to a workflow."""
    # First get the current workflow
    response = make_request("GET", f"/workflows/{workflow_id}")
    if response.status_code != 200:
        print(f"Error: Failed to get workflow (HTTP {response.status_code})")
        return

    workflow = response.json()

    # Update tags - need to include existing tags plus new ones
    existing_tags = [t.get("id") for t in workflow.get("tags", [])]
    all_tags = list(set(existing_tags + tag_ids))

    # Update the workflow with new tags
    update_data = {"tags": [{"id": tid} for tid in all_tags]}
    response = make_request("PATCH", f"/workflows/{workflow_id}", update_data)

    if response.status_code == 200:
        print(f"Workflow {workflow_id} tagged successfully!")
    else:
        print(f"Error: Failed to tag workflow (HTTP {response.status_code})")
        try:
            print(json.dumps(response.json(), indent=2))
        except Exception:
            print(response.text)


def main():
    parser = argparse.ArgumentParser(
        description="n8n Tag Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s list                       List all tags
    %(prog)s create "Production"        Create a new tag
    %(prog)s get <tag-id>               Get tag details
    %(prog)s rename <id> "New Name"     Rename a tag
    %(prog)s delete <tag-id>            Delete a tag
    %(prog)s tag-workflow <wf-id> <tag> Add tag to workflow

Note: Tags are the organizational feature available in n8n Community Edition.
      Folders and Projects require n8n Enterprise license.

Environment:
    N8N_LOCAL_URL  Local URL (preferred, bypasses ngrok OAuth)
    N8N_URL        Public URL of your n8n instance
    N8N_API_KEY    Your n8n API key
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    subparsers.add_parser("list", help="List all tags")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new tag")
    create_parser.add_argument("name", help="Name of the tag to create")

    # Get command
    get_parser = subparsers.add_parser("get", help="Get tag details")
    get_parser.add_argument("tag_id", help="ID of the tag")

    # Rename command
    rename_parser = subparsers.add_parser("rename", help="Rename a tag")
    rename_parser.add_argument("tag_id", help="ID of the tag")
    rename_parser.add_argument("new_name", help="New name for the tag")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a tag")
    delete_parser.add_argument("tag_id", help="ID of the tag to delete")

    # Tag workflow command
    tag_wf_parser = subparsers.add_parser("tag-workflow", help="Add tag(s) to a workflow")
    tag_wf_parser.add_argument("workflow_id", help="ID of the workflow")
    tag_wf_parser.add_argument("tag_ids", nargs="+", help="Tag ID(s) to add")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "list":
        list_tags()
    elif args.command == "create":
        create_tag(args.name)
    elif args.command == "get":
        get_tag(args.tag_id)
    elif args.command == "rename":
        rename_tag(args.tag_id, args.new_name)
    elif args.command == "delete":
        delete_tag(args.tag_id)
    elif args.command == "tag-workflow":
        tag_workflow(args.workflow_id, args.tag_ids)


if __name__ == "__main__":
    main()
