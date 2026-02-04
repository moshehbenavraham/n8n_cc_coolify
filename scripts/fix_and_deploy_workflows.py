#!/usr/bin/env python3
"""
Fix and deploy failed workflow imports.
Removes non-standard node properties that cause n8n API validation errors.
Uses only standard library.
"""

import json
import urllib.request
import urllib.error
import os
import ssl
from pathlib import Path

# Configuration
N8N_LOCAL_URL = os.environ.get('N8N_LOCAL_URL', 'http://localhost:5678')
N8N_API_KEY = os.environ.get('N8N_API_KEY', '')

# Standard node properties accepted by n8n API
STANDARD_NODE_PROPERTIES = {
    'id',
    'name',
    'type',
    'position',
    'parameters',
    'typeVersion',
    'credentials',
    'disabled',
    'onError',
    'continueOnFail',
    'retryOnFail',
    'maxTries',
    'waitBetweenTries',
    'executeOnce',
    'webhookId',
    'notesInFlow',
    'alwaysOutputData',
}

# Failed workflows to fix
FAILED_WORKFLOWS = [
    {
        'path': 'voice_ai/workflows/01-voice-agents/6211-Process-voice-images-documents-with-GPT-4o-MongoDB.json',
        'error': 'Node 7 has additional properties (extendsCredential)',
    },
    {
        'path': 'voice_ai/workflows/01-voice-agents/8184-Convert-voice-notes-to-X-posts-with-Google-Drive-a.json',
        'error': 'Node 0 has additional properties (notes, notesAlignment)',
    },
    {
        'path': 'voice_ai/workflows/01-voice-agents/8246-Convert-voice-memos-to-blog-posts-with-Deepgram-GP.json',
        'error': 'Node 1 has additional properties (color, notes, direction, notesAlignment)',
    },
    {
        'path': 'voice_ai/workflows/03-messaging-bots/telegram/11817-Manage-Notion-to-do-tasks-via-Telegram-with-voice.json',
        'error': 'Node 16 has additional properties (cid, notes, creator)',
    },
    {
        'path': 'voice_ai/workflows/03-messaging-bots/telegram/9981-Voice-text-Telegram-assistant-with-GPT-4-1-mini-an.json',
        'error': 'Node 10 has additional properties (notes, creator)',
    },
    {
        'path': 'voice_ai/workflows/04-content-creation/video/6777-Generate-AI-videos-from-scripts-with-DeepSeek-TTS.json',
        'error': 'Network timeout - retry',
    },
    {
        'path': 'voice_ai/workflows/05-business-automation/booking-scheduling/12004-Restaurant-GPT-4-receptionist-for-bookings-deliver.json',
        'error': 'Network timeout - retry',
    },
]


def clean_node(node: dict) -> dict:
    """Remove non-standard properties from a node."""
    cleaned = {}
    for key, value in node.items():
        if key in STANDARD_NODE_PROPERTIES:
            cleaned[key] = value
    return cleaned


def clean_workflow(workflow_data: dict) -> dict:
    """Clean all nodes in a workflow."""
    # Navigate to the nested workflow structure
    if 'workflow' in workflow_data and 'workflow' in workflow_data['workflow']:
        inner_workflow = workflow_data['workflow']['workflow']
    elif 'workflow' in workflow_data:
        inner_workflow = workflow_data['workflow']
    else:
        inner_workflow = workflow_data

    # Extract the workflow portion we need
    nodes = inner_workflow.get('nodes', [])
    connections = inner_workflow.get('connections', {})
    settings = inner_workflow.get('settings', {})
    name = inner_workflow.get('name', workflow_data.get('workflow', {}).get('name', 'Imported Workflow'))

    # Clean each node
    cleaned_nodes = [clean_node(node) for node in nodes]

    # Return a clean workflow structure for n8n API
    return {
        'name': name,
        'nodes': cleaned_nodes,
        'connections': connections,
        'settings': settings,
    }


def deploy_workflow(workflow: dict) -> dict:
    """Deploy a workflow to n8n."""
    url = f'{N8N_LOCAL_URL}/api/v1/workflows'

    data = json.dumps(workflow).encode('utf-8')

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            'X-N8N-API-KEY': N8N_API_KEY,
            'Content-Type': 'application/json',
        },
        method='POST'
    )

    # Create SSL context that doesn't verify (for local connections)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, timeout=60, context=ctx) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"HTTP {e.code}: {error_body}")


def main():
    base_path = Path('/home/aiwithapex/n8n_cc_coolify')

    results = {
        'success': [],
        'failed': [],
    }

    for wf_info in FAILED_WORKFLOWS:
        filepath = base_path / wf_info['path']
        print(f"\n{'='*60}")
        print(f"Processing: {filepath.name}")
        print(f"Original error: {wf_info['error']}")

        try:
            # Read the workflow JSON
            with open(filepath, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)

            # Clean the workflow
            cleaned_workflow = clean_workflow(workflow_data)
            print(f"Cleaned workflow: {cleaned_workflow['name']}")
            print(f"  Nodes: {len(cleaned_workflow['nodes'])}")

            # Deploy to n8n
            result = deploy_workflow(cleaned_workflow)
            print(f"  Deployed successfully! ID: {result.get('id')}")
            results['success'].append({
                'name': cleaned_workflow['name'],
                'id': result.get('id'),
                'file': str(filepath),
            })

        except Exception as e:
            print(f"  FAILED: {e}")
            results['failed'].append({
                'file': str(filepath),
                'error': str(e),
            })

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Successful: {len(results['success'])}")
    for item in results['success']:
        print(f"  - {item['name']} (ID: {item['id']})")

    if results['failed']:
        print(f"\nFailed: {len(results['failed'])}")
        for item in results['failed']:
            print(f"  - {item['file']}")
            print(f"    Error: {str(item['error'])[:200]}...")

    return results


if __name__ == '__main__':
    main()
