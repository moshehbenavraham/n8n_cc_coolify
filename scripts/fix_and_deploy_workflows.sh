#!/bin/bash
# Fix and deploy failed workflow imports
# Removes non-standard node properties and deploys to n8n

# Don't exit on error - continue processing

# Resolve project root from script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_PATH="$(dirname "$SCRIPT_DIR")"

# Load environment
source "$BASE_PATH/.env"
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
        "$N8N_LOCAL_URL/api/v1/workflows")

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

# Only the remaining failed workflows
WORKFLOWS=(
    "voice_ai/workflows/01-voice-agents/8184-Convert-voice-notes-to-X-posts-with-Google-Drive-a.json"
    "voice_ai/workflows/04-content-creation/video/6777-Generate-AI-videos-from-scripts-with-DeepSeek-TTS.json"
    "voice_ai/workflows/05-business-automation/booking-scheduling/12004-Restaurant-GPT-4-receptionist-for-bookings-deliver.json"
)

SUCCESS_COUNT=0
FAIL_COUNT=0

for wf_path in "${WORKFLOWS[@]}"; do
    full_path="$BASE_PATH/$wf_path"
    if deploy_workflow "$full_path"; then
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
