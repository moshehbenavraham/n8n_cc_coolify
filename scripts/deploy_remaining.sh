#!/bin/bash
# Continue deploying remaining voice_ai workflows

source /home/aiwithapex/n8n_cc_coolify/.env

WORKFLOW_DIR="/home/aiwithapex/n8n_cc_coolify/voice_ai/workflows"
API_URL="${N8N_LOCAL_URL}/api/v1"
LOG_FILE="/home/aiwithapex/n8n_cc_coolify/scripts/deploy_log.txt"
ERROR_LOG="/home/aiwithapex/n8n_cc_coolify/scripts/deploy_errors.txt"

# Get already deployed names
deployed_file=$(mktemp)
cat "$LOG_FILE" | sed 's/SUCCESS: \(.*\) (ID:.*/\1/' > "$deployed_file"
cat "$ERROR_LOG" | sed 's/FAILED: \(.*\) - HTTP.*/\1/' >> "$deployed_file"

echo "Continuing deployment (skipping $(wc -l < "$deployed_file") already processed)..."
echo ""

success=0
failed=0
skipped=0
total=0

while IFS= read -r file; do
    total=$((total + 1))

    workflow_name=$(jq -r '.workflow.name // .name // "Unknown"' "$file" 2>/dev/null)

    # Skip if already deployed
    if grep -qF "$workflow_name" "$deployed_file" 2>/dev/null; then
        skipped=$((skipped + 1))
        continue
    fi

    echo "[$total] Deploying: $workflow_name"

    request_body=$(jq '{
      name: (.workflow.name // .name),
      nodes: (.workflow.workflow.nodes // .workflow.nodes // .nodes // []),
      connections: (.workflow.workflow.connections // .workflow.connections // .connections // {}),
      settings: {executionOrder: "v1"}
    }' "$file" 2>/dev/null)

    if [ -z "$request_body" ] || [ "$request_body" = "null" ]; then
        echo "  ERROR: Could not extract workflow JSON"
        echo "FAILED: $workflow_name - Could not extract JSON" >> "$ERROR_LOG"
        failed=$((failed + 1))
        continue
    fi

    response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/workflows" \
        -H "X-N8N-API-KEY: $N8N_API_KEY" \
        -H "Content-Type: application/json" \
        -d "$request_body" 2>/dev/null)

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

    sleep 0.05
done < <(find "$WORKFLOW_DIR" -name "*.json" -type f | sort)

rm -f "$deployed_file"

echo ""
echo "========================================"
echo "Deployment Complete!"
echo "========================================"
echo "This run: $success succeeded, $failed failed, $skipped skipped"
echo ""
echo "Total in logs:"
echo "  Success: $(wc -l < "$LOG_FILE")"
echo "  Failed:  $(wc -l < "$ERROR_LOG")"
