#!/bin/bash
# Deploy all voice_ai workflows to n8n instance

set -e

# Load environment variables
source /home/aiwithapex/n8n_cc_coolify/.env

# Configuration
WORKFLOW_DIR="/home/aiwithapex/n8n_cc_coolify/voice_ai/workflows"
API_URL="${N8N_LOCAL_URL}/api/v1"
LOG_FILE="/home/aiwithapex/n8n_cc_coolify/scripts/deploy_log.txt"
ERROR_LOG="/home/aiwithapex/n8n_cc_coolify/scripts/deploy_errors.txt"

# Clear previous logs
> "$LOG_FILE"
> "$ERROR_LOG"

echo "Starting workflow deployment..."
echo "API URL: $API_URL"
echo "Workflow directory: $WORKFLOW_DIR"
echo ""

# Counter variables
total=0
success=0
failed=0

# Find all workflow JSON files
while IFS= read -r file; do
    total=$((total + 1))

    # Extract the workflow name
    workflow_name=$(jq -r '.workflow.name // .name // "Unknown"' "$file" 2>/dev/null)

    echo "[$total] Deploying: $workflow_name"

    # Build proper request body with only allowed fields
    request_body=$(jq '{
      name: (.workflow.name // .name),
      nodes: (.workflow.workflow.nodes // .workflow.nodes // .nodes // []),
      connections: (.workflow.workflow.connections // .workflow.connections // .connections // {}),
      settings: {executionOrder: "v1"}
    }' "$file" 2>/dev/null)

    if [ -z "$request_body" ] || [ "$request_body" = "null" ]; then
        echo "  ERROR: Could not extract workflow JSON from $file"
        echo "$file: Could not extract workflow JSON" >> "$ERROR_LOG"
        failed=$((failed + 1))
        continue
    fi

    # Make API request to create workflow
    response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/workflows" \
        -H "X-N8N-API-KEY: $N8N_API_KEY" \
        -H "Content-Type: application/json" \
        -d "$request_body" 2>/dev/null)

    # Extract HTTP status code (last line)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        new_id=$(echo "$body" | jq -r '.id // "unknown"')
        echo "  SUCCESS: ID $new_id"
        echo "SUCCESS: $workflow_name (ID: $new_id)" >> "$LOG_FILE"
        success=$((success + 1))
    else
        error_msg=$(echo "$body" | jq -r '.message // .error // "Unknown error"' 2>/dev/null || echo "$body")
        echo "  FAILED: HTTP $http_code - $error_msg"
        echo "FAILED: $workflow_name - HTTP $http_code - $error_msg" >> "$ERROR_LOG"
        failed=$((failed + 1))
    fi

    # Small delay to avoid overwhelming the API
    sleep 0.05

done < <(find "$WORKFLOW_DIR" -name "*.json" -type f | sort)

echo ""
echo "========================================"
echo "Deployment Complete!"
echo "========================================"
echo "Total workflows: $total"
echo "Successful: $success"
echo "Failed: $failed"
echo ""
echo "Logs saved to:"
echo "  Success: $LOG_FILE"
echo "  Errors:  $ERROR_LOG"
