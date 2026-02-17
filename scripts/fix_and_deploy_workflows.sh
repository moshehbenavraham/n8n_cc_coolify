#!/bin/bash
# Fix and deploy workflow imports
# Removes non-standard node properties and deploys to n8n
# Usage: ./fix_and_deploy_workflows.sh <file1.json> [file2.json] ...

# Don't exit on error - continue processing

# Resolve project root from script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_PATH="$(dirname "$SCRIPT_DIR")"

# Load environment
if [ -f "$BASE_PATH/.env" ]; then
    set -a
    source "$BASE_PATH/.env"
    set +a
fi

API_URL="${N8N_URL:-http://localhost:5678}"
TEMP_FILE="/tmp/workflow_deploy.json"

# Standard node properties (JSON array for jq)
STANDARD_NODE_PROPS='["id", "name", "type", "position", "parameters", "typeVersion", "credentials", "disabled", "onError", "continueOnFail", "retryOnFail", "maxTries", "waitBetweenTries", "executeOnce", "webhookId", "notesInFlow", "alwaysOutputData"]'

# Standard settings properties
STANDARD_SETTINGS_PROPS='["executionOrder", "timezone", "saveDataErrorExecution", "saveDataSuccessExecution", "saveExecutionProgress", "saveManualExecutions", "executionTimeout", "errorWorkflow"]'

# Function to clean and deploy a workflow
deploy_workflow() {
    local filepath="$1"
    local filename=$(basename "$filepath")

    echo ""
    echo "============================================================"
    echo "Processing: $filename"

    # Extract and clean the workflow using jq, save to temp file
    jq --argjson nodeProps "$STANDARD_NODE_PROPS" \
       --argjson settingsProps "$STANDARD_SETTINGS_PROPS" '
        # Get the inner workflow
        (if .workflow.workflow then .workflow.workflow else .workflow end) as $wf |
        {
            name: ($wf.name // "Imported Workflow"),
            nodes: [$wf.nodes[] | with_entries(select(.key as $k | $nodeProps | index($k)))],
            connections: $wf.connections,
            settings: (($wf.settings // {}) | with_entries(select(.key as $k | $settingsProps | index($k))))
        }
    ' "$filepath" > "$TEMP_FILE"

    if [ $? -ne 0 ]; then
        echo "FAILED! Could not parse workflow JSON"
        return 1
    fi

    local wf_name=$(jq -r '.name' "$TEMP_FILE")
    local node_count=$(jq '.nodes | length' "$TEMP_FILE")

    echo "Workflow: $wf_name"
    echo "Nodes: $node_count"

    # Deploy to n8n using temp file
    local response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "X-N8N-API-KEY: $N8N_API_KEY" \
        -H "Content-Type: application/json" \
        -d "@$TEMP_FILE" \
        "$API_URL/api/v1/workflows")

    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        local wf_id=$(echo "$body" | jq -r '.id')
        echo "SUCCESS! Deployed with ID: $wf_id"
        return 0
    else
        echo "FAILED! HTTP $http_code"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
        return 1
    fi
}

# Check arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 <workflow1.json> [workflow2.json] ..."
    echo ""
    echo "Cleans non-standard node properties from workflow JSON files"
    echo "and deploys them to n8n via the API."
    echo ""
    echo "Environment variables (from .env):"
    echo "  N8N_URL      - n8n instance URL (default: http://localhost:5678)"
    echo "  N8N_API_KEY   - n8n API key"
    exit 1
fi

SUCCESS_COUNT=0
FAIL_COUNT=0

for wf_path in "$@"; do
    if [ ! -f "$wf_path" ]; then
        echo "WARNING: File not found: $wf_path"
        ((FAIL_COUNT++))
        continue
    fi

    if deploy_workflow "$wf_path"; then
        ((SUCCESS_COUNT++))
    else
        ((FAIL_COUNT++))
    fi
done

# Cleanup
rm -f "$TEMP_FILE"

echo ""
echo "============================================================"
echo "SUMMARY"
echo "============================================================"
echo "Successful: $SUCCESS_COUNT"
echo "Failed: $FAIL_COUNT"
