#!/usr/bin/env python3
"""
n8n Project Management CLI

CLI tool to manage projects in n8n.
REQUIRES n8n Enterprise license (feat:projectRole:admin).

NOTE: Projects and Folders are ENTERPRISE features in n8n.
      For Community Edition, use n8n_tags.py instead for organization.

n8n Organization Hierarchy:
    - Projects (Enterprise) -> contain Folders and Workflows
    - Folders (Enterprise)  -> nested inside Projects, contain Workflows
    - Tags (Community)      -> labels for categorizing workflows

Usage:
    python n8n_folders.py list
    python n8n_folders.py create "My Project"
    python n8n_folders.py delete <project-id>
    python n8n_folders.py get <project-id>

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
    # Fall back to N8N_URL if local not available
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
        else:
            print(f"Error: Unsupported HTTP method: {method}")
            sys.exit(1)

        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: Request failed - {e}")
        sys.exit(1)


def list_projects():
    """List all projects/folders."""
    response = make_request("GET", "/projects")

    if response.status_code == 200:
        try:
            data = response.json()
        except Exception:
            # Response might be the array directly
            print(f"Raw response: {response.text[:500]}")
            return

        # Handle both {data: [...]} and direct array responses
        if isinstance(data, list):
            projects = data
        else:
            projects = data.get("data", [])

        if not projects:
            print("No projects found.")
            return

        print(f"\n{'ID':<40} {'Name':<30} {'Type':<15}")
        print("-" * 85)
        for project in projects:
            project_id = project.get("id", "N/A")
            name = project.get("name", "N/A")
            project_type = project.get("type", "N/A")
            print(f"{project_id:<40} {name:<30} {project_type:<15}")
        print()
    else:
        print(f"Error: Failed to list projects (HTTP {response.status_code})")
        print(f"Response: {response.text[:500] if response.text else '(empty)'}")


def create_project(name):
    """Create a new project/folder."""
    data = {"name": name}
    response = make_request("POST", "/projects", data)

    if response.status_code in (200, 201):
        result = response.json()
        print(f"Project created successfully!")
        print(f"  ID:   {result.get('id', 'N/A')}")
        print(f"  Name: {result.get('name', 'N/A')}")
        print(f"  Type: {result.get('type', 'N/A')}")
    else:
        print(f"Error: Failed to create project (HTTP {response.status_code})")
        try:
            print(json.dumps(response.json(), indent=2))
        except Exception:
            print(response.text)


def get_project(project_id):
    """Get details of a specific project."""
    response = make_request("GET", f"/projects/{project_id}")

    if response.status_code == 200:
        result = response.json()
        print(f"\nProject Details:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: Failed to get project (HTTP {response.status_code})")
        try:
            print(json.dumps(response.json(), indent=2))
        except Exception:
            print(response.text)


def delete_project(project_id):
    """Delete a project/folder."""
    response = make_request("DELETE", f"/projects/{project_id}")

    if response.status_code in (200, 204):
        print(f"Project {project_id} deleted successfully!")
    else:
        print(f"Error: Failed to delete project (HTTP {response.status_code})")
        try:
            print(json.dumps(response.json(), indent=2))
        except Exception:
            print(response.text)


def rename_project(project_id, new_name):
    """Rename a project/folder."""
    data = {"name": new_name}
    response = make_request("PATCH", f"/projects/{project_id}", data)

    if response.status_code == 200:
        result = response.json()
        print(f"Project renamed successfully!")
        print(f"  ID:   {result.get('id', 'N/A')}")
        print(f"  Name: {result.get('name', 'N/A')}")
    else:
        print(f"Error: Failed to rename project (HTTP {response.status_code})")
        try:
            print(json.dumps(response.json(), indent=2))
        except Exception:
            print(response.text)


def main():
    parser = argparse.ArgumentParser(
        description="n8n Folder/Project Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s list                      List all projects
    %(prog)s create "My New Folder"    Create a new folder
    %(prog)s get <project-id>          Get project details
    %(prog)s rename <id> "New Name"    Rename a project
    %(prog)s delete <project-id>       Delete a project

Environment:
    N8N_URL      Base URL of your n8n instance
    N8N_API_KEY  Your n8n API key
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    subparsers.add_parser("list", help="List all projects/folders")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new project/folder")
    create_parser.add_argument("name", help="Name of the project to create")

    # Get command
    get_parser = subparsers.add_parser("get", help="Get project details")
    get_parser.add_argument("project_id", help="ID of the project")

    # Rename command
    rename_parser = subparsers.add_parser("rename", help="Rename a project")
    rename_parser.add_argument("project_id", help="ID of the project")
    rename_parser.add_argument("new_name", help="New name for the project")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a project/folder")
    delete_parser.add_argument("project_id", help="ID of the project to delete")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "list":
        list_projects()
    elif args.command == "create":
        create_project(args.name)
    elif args.command == "get":
        get_project(args.project_id)
    elif args.command == "rename":
        rename_project(args.project_id, args.new_name)
    elif args.command == "delete":
        delete_project(args.project_id)


if __name__ == "__main__":
    main()
